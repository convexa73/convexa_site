import os
from typing import Optional

def get_secret(name: str) -> str:
    """
    1) Se existir na variável de ambiente, usa ela (prioridade).
    2) Senão, tenta ler do admin (model IntegrationKeys, 1º registro).
    3) Senão, retorna string vazia.
    """
    val = os.getenv(name) or ""
    if val:
        return val
    try:
        from .models import IntegrationKeys
        rec = IntegrationKeys.objects.order_by('-pk').first()
        if not rec:
            return ""
        if name.upper() == "OPENAI_API_KEY":
            return rec.openai_api_key or ""
        if name.upper() == "YOUTUBE_API_KEY":
            return rec.youtube_api_key or ""
    except Exception:
        return ""
    return ""
