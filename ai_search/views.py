import os, json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

# IA desativada por padrão; só liga se ENABLE_AI for verdadeiro
ENABLE_AI = os.getenv("ENABLE_AI", "").lower() in {"1", "true", "yes", "on"}

client = None
_init_error = None
if ENABLE_AI:
    try:
        # Importa 'openai' apenas quando a IA está habilitada (evita erro se não instalado)
        from openai import OpenAI  # type: ignore
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY não definido")
        client = OpenAI(api_key=api_key)
    except Exception as e:
        ENABLE_AI = False
        client = None
        _init_error = str(e)

@csrf_exempt
def chat_api(request):
    """
    GET  /ia/api/chat/     -> status
    POST /ia/api/chat/     -> { "q": "pergunta" } (stub enquanto IA estiver off)
    """
    if request.method not in {"GET", "POST"}:
        return HttpResponseBadRequest("Use GET ou POST.")

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8") or "{}")
        except Exception:
            data = {}
        prompt = data.get("q") or data.get("prompt") or ""

        if not ENABLE_AI or client is None:
            return JsonResponse({
                "ok": True,
                "mode": "stub",
                "message": "IA local desativada. Defina ENABLE_AI=1 e OPENAI_API_KEY para ativar.",
                "echo": prompt
            })

        # Quando for ativar a IA de verdade, implemente aqui a chamada ao provedor:
        # resp = client.responses.create(model="gpt-4o-mini", input=[{"role":"user","content":prompt}])
        # return JsonResponse({"ok": True, "mode": "enabled", "answer": resp.output_text})
        return JsonResponse({"ok": True, "mode": "enabled", "note": "Implementar chamada ao provedor aqui."})

    # GET: status da rota de IA
    return JsonResponse({
        "ok": True,
        "ia_enabled": ENABLE_AI,
        "init_error": _init_error,
        "hint": "POST com {q: 'sua pergunta'} para testar."
    })

# --- ROTA COMPATÍVEL COM URLs ANTIGAS ---
def ia_hub(request):
    # Página/endpoint de status simples, usado por urls.py antigos
    return JsonResponse({
        "ok": True,
        "route": "ia_hub",
        "ia_enabled": ENABLE_AI,
        "hint": "Use POST em /ia/api/chat/ com {q: 'sua pergunta'} para receber resposta (stub enquanto IA estiver off)."
    })
