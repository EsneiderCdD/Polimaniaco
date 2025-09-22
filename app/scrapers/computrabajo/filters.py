from datetime import timedelta
from .config import BLACKLIST_COMPANIES
from .utils import parse_hace_to_timedelta

def not_blacklisted(oferta: dict) -> bool:
    empresa = (oferta.get("empresa") or "").lower()
    if not empresa:
        return True
    for bad in BLACKLIST_COMPANIES:
        if bad.lower() in empresa:   # <--- busca coincidencia parcial
            print(f"[filtro] descartada por blacklist: {oferta['empresa']}")
            return False
    return True

def is_recent(oferta: dict) -> bool:
    """
    Acepta solo ofertas con fecha <= 3 días.
    """
    raw = (oferta.get("raw_fecha") or "").lower()
    if not raw:
        return False

    td = parse_hace_to_timedelta(raw)
    if td is None:
        return False
    return td <= timedelta(days=3)  # ahora 3 días

def apply_filters(ofertas: list) -> list:
    """
    Aplica los filtros:
    - Recientes (<= 3 días)
    - No en blacklist
    """
    filtered = []
    for o in ofertas:
        if not is_recent(o):
            print(f"[filtro] descartada por fecha (>3 días): {o.get('raw_fecha')}")
            continue
        if not not_blacklisted(o):
            print(f"[filtro] descartada por blacklist: {o.get('empresa')}")
            continue
        filtered.append(o)
    return filtered
