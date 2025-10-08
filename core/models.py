from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse

class SiteTheme(models.Model):
    name = models.CharField(_("Nome da paleta"), max_length=60, default="Padrão")
    color1 = models.CharField(_("Primária"), max_length=7, default="#0b1020")
    color2 = models.CharField(_("Secundária"), max_length=7, default="#6aa3ff")
    color3 = models.CharField(_("Acento"), max_length=7, default="#10bfae")
    color4 = models.CharField(_("Texto"), max_length=7, default="#e8eefc")
    color5 = models.CharField(_("Muted"), max_length=7, default="#9fb3d1")
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = _("Paleta de cores")
        verbose_name_plural = _("Paletas de cores")
    def __str__(self):
        return f"{self.name} ({self.pk})"

class SiteSettings(models.Model):
    site_name = models.CharField(_("Nome do site"), max_length=120, default="Convexa")
    domain = models.CharField(_("Domínio"), max_length=120, default="convexa.com.br")
    city_state = models.CharField(_("Local"), max_length=120, default="Rio de Janeiro - RJ")
    founded = models.DateField(_("Fundação"), null=True, blank=True)
    about = models.TextField(_("Sobre"), blank=True)
    use_gradient_logo_text = models.BooleanField(_("Texto da marca com gradiente"), default=True)
    youtube_url = models.URLField(_("Canal do YouTube"), blank=True)
    theme = models.ForeignKey(SiteTheme, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta:
        verbose_name = _("Configuração do site")
        verbose_name_plural = _("Configurações do site")
    def __str__(self):
        return self.site_name

class Service(models.Model):
    title = models.CharField(_("Título"), max_length=120)
    slug = models.SlugField(unique=True)
    summary = models.TextField(_("Descrição"))
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    class Meta:
        ordering = ("order", "title")
        verbose_name = _("Serviço")
        verbose_name_plural = _("Serviços")
    def __str__(self):
        return self.title

class YouTubeVideo(models.Model):
    title = models.CharField(_("Título"), max_length=150)
    slug = models.SlugField(_("Slug"), max_length=170, blank=True)
    video_id = models.CharField(_("ID do vídeo (YouTube)"), max_length=20, help_text="Ex.: dQw4w9WgXcQ")
    channel_title = models.CharField(_("Canal"), max_length=150, blank=True)
    duration = models.CharField(_("Duração (ISO8601)"), max_length=32, blank=True)
    published_at = models.DateTimeField(_("Publicado em"), null=True, blank=True)
    original_description = models.TextField(_("Descrição original"), blank=True)
    optimized_summary = models.TextField(_("Resumo otimizado (IA)"), blank=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    last_refreshed = models.DateTimeField(_("Última atualização"), null=True, blank=True)
    class Meta:
        ordering = ("order", "-published_at", "title")
        verbose_name = _("Vídeo do YouTube")
        verbose_name_plural = _("Vídeos do YouTube")
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:165] if self.title else slugify(self.video_id)
        super().save(*args, **kwargs)
    @property
    def thumb_url(self):
        return f"https://i.ytimg.com/vi/{self.video_id}/hqdefault.jpg"
    def get_absolute_url(self):
        return reverse("video_detail", kwargs={"slug": f"{self.slug}-{self.pk}"})

class IntegrationKeys(models.Model):
    """
    Guarda chaves para integrações. Segurança:
      - A aplicação prioriza variáveis de ambiente.
      - Estes campos aparecem mascarados no admin.
      - Restrinja acesso ao /admin e ao banco.
    """
    openai_api_key = models.CharField(_("OpenAI API Key"), max_length=200, blank=True)
    youtube_api_key = models.CharField(_("YouTube API Key"), max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = _("Chaves de Integração")
        verbose_name_plural = _("Chaves de Integração")
    def __str__(self):
        tail_o = (self.openai_api_key[-4:] if self.openai_api_key else "----")
        tail_y = (self.youtube_api_key[-4:] if self.youtube_api_key else "----")
        return f"Chaves (OpenAI ••••{tail_o}, YouTube ••••{tail_y})"
