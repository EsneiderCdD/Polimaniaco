# app/scrapers/computrabajo/filters.py

from .utils import normalize_text, within_last_24h
from .config import BLACKLIST_COMPANIES

def is_remote(oferta: dict) -> bool:
    """
    Determina si la oferta es remota buscando 'remoto' en título/ubicación/descripcion.
    """
    check = " ".join([
        oferta.get("titulo") or "",
        oferta.get("ubicacion") or "",
        oferta.get("descripcion") or ""
    ]).lower()
    return "remoto" in check or "remote" in check

def is_today(oferta: dict) -> bool:
    """
    Usa el campo fecha_publicacion textual (p.ej. 'Hace 4 horas') para decidir si es hoy.
    El scraper extrae este texto en 'raw_fecha' (si existe). Si no existe, lo excluye.
    """
    raw = oferta.get("raw_fecha")
    if not raw:
        # conservador: excluir si no podemos confirmar
        return False
    return within_last_24h(raw)

def not_blacklisted(oferta: dict) -> bool:
    empresa = (oferta.get("empresa") or "").lower()
    if not empresa:
        return True
    for bad in BLACKLIST_COMPANIES:
        if bad.lower() in empresa:
            return False
    return True

def apply_filters(ofertas: list) -> list:
    """
    Aplica la cadena de filtros: Hoy, Remoto, No en blacklist.
    Devuelve lista filtrada.
    """
    filtered = []
    for o in ofertas:
        if not is_today(o):
            continue
        if not is_remote(o):
            continue
        if not not_blacklisted(o):
            continue
        filtered.append(o)
    return filtered
