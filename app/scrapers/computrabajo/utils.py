import time
import re
from datetime import datetime, timedelta

def sleep_between_requests(seconds):
    """Pausa educada entre requests."""
    time.sleep(seconds)

def normalize_text(t: str):
    if not t:
        return ""
    return " ".join(t.lower().split())

def parse_hace_to_timedelta(text: str):
    """
    Intenta convertir textos como "Hace 3 días" "Hace 57 minutos" a timedelta.
    Devuelve timedelta o None si no se pudo interpretar.
    """
    if not text:
        return None
    text_low = text.lower()
    # Buscar minutos
    m = re.search(r'([0-9]+)\s*min', text_low)
    if m:
        return timedelta(minutes=int(m.group(1)))
    m = re.search(r'([0-9]+)\s*minuto', text_low)
    if m:
        return timedelta(minutes=int(m.group(1)))
    m = re.search(r'([0-9]+)\s*hora', text_low)
    if m:
        return timedelta(hours=int(m.group(1)))
    m = re.search(r'([0-9]+)\s*d[ií]a', text_low)
    if m:
        return timedelta(days=int(m.group(1)))
    # "hoy" lo consideramos 0 horas
    if "hoy" in text_low:
        return timedelta(hours=0)
    return None

def within_last_24h(text_fecha: str) -> bool:
    """
    Decide si el texto 'Hace X' corresponde a <= 24 horas.
    """
    td = parse_hace_to_timedelta(text_fecha)
    if td is None:
        # si no podemos parsear, conservador: devolver False (excluir)
        return False
    return td <= timedelta(days=1)

def title_is_duplicate(title: str, seen_titles: set) -> bool:
    n = normalize_text(title)
    # simple heuristic: exact match or very similar (exact normalized)
    if n in seen_titles:
        return True
    seen_titles.add(n)
    return False
