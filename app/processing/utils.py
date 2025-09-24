import re

def normalize_text(text: str) -> str:
    """
    Normaliza texto para búsqueda de tecnologías:
    - minúsculas
    - espacios normalizados
    """
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()
