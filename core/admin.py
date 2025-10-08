import re, textwrap, requests
from django.contrib import admin, messages
from django import forms
from django.utils import timezone
from .models import SiteTheme, SiteSettings, Service, YouTubeVideo, IntegrationKeys
from .secrets import get_secret

# ---------- Paleta de cores ----------
class ColorInput(forms.TextInput):
    input_type = "color"

class SiteThemeForm(forms.ModelForm):
    class Meta:
        model = SiteTheme
        fields = "__all__"
        widgets = {c: ColorInput() for c in ["color1","color2","color3","color4","color5"]}

@admin.register(SiteTheme)
class SiteThemeAdmin(admin.ModelAdmin):
    form = SiteThemeForm
    list_display = ("name", "updated_at")

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "domain", "city_state", "theme")
    fieldsets = (
        ("Geral", {"fields": ("site_name","domain","city_state","founded","about")}),
        ("Marca", {"fields": ("use_gradient_logo_text","theme")}),
        ("Canais", {"fields": ("youtube_url",)}),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title","active","order")
    list_editable = ("active","order")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title","summary")

# ---------- Chaves de Integração (com máscara, diagnóstico) ----------
class IntegrationKeysForm(forms.ModelForm):
    openai_api_key = forms.CharField(required=False, widget=forms.PasswordInput(render_value=True))
    youtube_api_key = forms.CharField(required=False, widget=forms.PasswordInput(render_value=True))
    class Meta:
        model = IntegrationKeys
        fields = "__all__"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst = self.instance
        if inst and inst.pk:
            if inst.openai_api_key:
                self.initial["openai_api_key"] = "********" + inst.openai_api_key[-4:]
            if inst.youtube_api_key:
                self.initial["youtube_api_key"] = "********" + inst.youtube_api_key[-4:]
    def clean_openai_api_key(self):
        v = self.cleaned_data.get("openai_api_key","")
        if v.startswith("********") and self.instance and self.instance.pk:
            return self.instance.openai_api_key
        return v
    def clean_youtube_api_key(self):
        v = self.cleaned_data.get("youtube_api_key","")
        if v.startswith("********") and self.instance and self.instance.pk:
            return self.instance.youtube_api_key
        return v

def _test_youtube(api_key: str):
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {"part": "snippet", "id": "dQw4w9WgXcQ", "key": api_key}
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        if data.get("items"):
            return True, "YouTube OK"
        if "error" in data:
            return False, f"YouTube ERRO: {data['error'].get('message','Erro desconhecido')}"
        return False, "YouTube ERRO: resposta sem itens."
    except Exception as e:
        return False, f"YouTube EXC: {e}"

def _test_openai(api_key: str):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":"Ping curto. Responda 'OK'."}],
            max_tokens=5, temperature=0
        )
        txt = (res.choices[0].message.content or "").strip()
        return True, f"OpenAI OK ({txt[:20] or 'resposta recebida'})"
    except Exception as e:
        return False, f"OpenAI EXC: {e}"

@admin.register(IntegrationKeys)
class IntegrationKeysAdmin(admin.ModelAdmin):
    form = IntegrationKeysForm
    list_display = ("__str__","updated_at")
    actions = ["diagnose_integrations"]
    def diagnose_integrations(self, request, queryset):
        openai_key = get_secret("OPENAI_API_KEY")
        yt_key = get_secret("YOUTUBE_API_KEY")
        if not openai_key and not yt_key:
            self.message_user(request, "Nenhuma chave configurada (env/Admin).", level=messages.ERROR)
            return
        if yt_key:
            ok, msg = _test_youtube(yt_key)
            self.message_user(request, f"Diagnóstico YouTube: {'✅' if ok else '❌'} {msg}",
                              level=(messages.SUCCESS if ok else messages.ERROR))
        else:
            self.message_user(request, "YouTube: chave ausente (env/Admin).", level=messages.WARNING)
        if openai_key:
            ok, msg = _test_openai(openai_key)
            self.message_user(request, f"Diagnóstico OpenAI: {'✅' if ok else '❌'} {msg}",
                              level=(messages.SUCCESS if ok else messages.ERROR))
        else:
            self.message_user(request, "OpenAI: chave ausente (env/Admin).", level=messages.WARNING)
    diagnose_integrations.short_description = "Diagnosticar chaves (YouTube/OpenAI)"

# ---------- Vídeos: ações de pull/sumário ----------
def _pull_one(video, api_key: str):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {"part": "snippet,contentDetails", "id": video.video_id, "key": api_key}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    items = data.get("items", [])
    if not items:
        return False, "Não encontrado no YouTube."
    it = items[0]
    sn = it.get("snippet", {}) or {}
    cd = it.get("contentDetails", {}) or {}
    video.title = sn.get("title") or video.title
    video.channel_title = sn.get("channelTitle","")
    video.original_description = sn.get("description","")
    video.duration = cd.get("duration","")
    from django.utils.dateparse import parse_datetime
    if sn.get("publishedAt"):
        video.published_at = parse_datetime(sn["publishedAt"])
    video.last_refreshed = timezone.now()
    video.save()
    return True, "OK"

def _fallback_extract_summary(text: str, max_chars: int = 300) -> str:
    # remove links e espaços extras
    txt = re.sub(r'https?://\S+', '', text or '').strip()
    # divide em sentenças simples e junta 2–3 até ~300 chars
    sents = re.split(r'(?<=[\.!\?])\s+', txt)
    out, total = [], 0
    for s in sents:
        s = s.strip()
        if not s: 
            continue
        out.append(s)
        total += len(s)
        if total >= (max_chars - 20) or len(out) >= 3:
            break
    return textwrap.shorten(" ".join(out), width=max_chars, placeholder="…")

def _summarize_one(video, api_key: str):
    base = (video.original_description or "").strip()
    title = (video.title or "").strip()
    if not base:
        return False, "Sem descrição original para resumir."
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = (
            "Você é um assistente de conteúdo. Gere um resumo curto (2–3 frases, máx. ~300 caracteres), "
            "claro e chamativo, em pt-BR, para o vídeo abaixo. Não repita o título. "
            "Entregue apenas o texto final, sem prefixos.\n\n"
            f"Título: {title}\n\nDescrição original:\n{base}"
        )
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"Resuma em pt-BR com concisão e apelo."},
                {"role":"user","content":prompt},
            ],
            temperature=0.6, max_tokens=140
        )
        text = (resp.choices[0].message.content or "").strip()
        if not text:
            raise RuntimeError("Resposta vazia da IA.")
        video.optimized_summary = text
        video.last_refreshed = timezone.now()
        video.save()
        return True, "OK"
    except Exception as e:
        # Se for quota/429, aplica fallback local gratuito
        emsg = str(e).lower()
        if "insufficient_quota" in emsg or "quota" in emsg or "429" in emsg:
            video.optimized_summary = _fallback_extract_summary(base)
            video.last_refreshed = timezone.now()
            video.save()
            return True, "Fallback local aplicado (sem custo)"
        # Outros erros: marca como falha
        return False, f"Falha IA: {e}"

@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = ("title","video_id","active","order","published_at","last_refreshed")
    list_editable = ("active","order")
    search_fields = ("title","video_id","original_description","optimized_summary")
    actions = ["pull_from_youtube","summarize_with_ai"]

    def pull_from_youtube(self, request, queryset):
        api_key = get_secret("YOUTUBE_API_KEY")
        if not api_key:
            self.message_user(request, "Configure a chave em: Core → Chaves de Integração (ou env).",
                              level=messages.ERROR)
            return
        ok = fail = 0
        for v in queryset:
            try:
                s, _ = _pull_one(v, api_key)
                ok += int(s); fail += int(not s)
            except Exception:
                fail += 1
        self.message_user(request, f"Atualização YouTube: OK={ok}, Falhas={fail}.")
    pull_from_youtube.short_description = "Atualizar metadados a partir do YouTube"

    def summarize_with_ai(self, request, queryset):
        ai_key = get_secret("OPENAI_API_KEY")  # pode estar vazio; fallback cobre
        ok = fail = 0
        for v in queryset:
            try:
                s, _ = _summarize_one(v, ai_key or "")
                ok += int(s); fail += int(not s)
            except Exception:
                fail += 1
        msg_level = messages.SUCCESS if fail == 0 else (messages.WARNING if ok else messages.ERROR)
        self.message_user(request, f"Resumo (IA/fallback): OK={ok}, Falhas={fail}.", level=msg_level)
    summarize_with_ai.short_description = "Gerar resumo curto (IA com fallback)"
