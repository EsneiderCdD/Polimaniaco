import re

def normalize_text(text: str) -> str:
    """
    Normaliza texto para búsqueda de tecnologías:
    - minúsculas
    - espacios normalizados
    - caracteres especiales opcionales (ej: # → sharp)
    """
    if not text:
        return ""
    
    text = text.lower()
    text = re.sub(r"#", " sharp", text)  # c# → c sharp
    text = re.sub(r"\s+", " ", text)     # normaliza espacios
    text = text.strip()
    return text
