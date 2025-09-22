from .config import BLACKLIST_COMPANIES

def is_remote(oferta: dict) -> bool:
    """
    Determina si la oferta es remota (solo en español por ahora).
    """
    check = " ".join([
        oferta.get("titulo") or "",
        oferta.get("ubicacion") or "",
        oferta.get("descripcion") or ""
    ]).lower()

    keywords = [
        "remoto",
        "teletrabajo",
        "desde casa",
    ]
    return any(k in check for k in keywords)

def is_today(oferta: dict) -> bool:
    """
    Acepta solo ofertas con fecha <= 24h: hoy, hora, minuto, menos de.
    """
    raw = (oferta.get("raw_fecha") or "").lower()
    if not raw:
        return False

    if any(k in raw for k in ["hoy", "hora", "minuto", "menos de"]):
        return True

    return False

def not_blacklisted(oferta: dict) -> bool:
    empresa = (oferta.get("empresa") or "").lower()
    if not empresa:
        return True
    for bad in BLACKLIST_COMPANIES:
        if bad.lower() in empresa:   # <--- busca coincidencia parcial
            print(f"[filtro] descartada por blacklist: {oferta['empresa']}")
            return False
    return True

def apply_filters(ofertas: list) -> list:
    """
    Aplica la cadena de filtros: Hoy, Remoto, No en blacklist.
    """
    filtered = []
    for o in ofertas:
        if not is_today(o):
            print(f"[filtro] descartada por fecha: {o.get('raw_fecha')}")
            continue
        if not is_remote(o):
            print(f"[filtro] descartada por remoto: {o.get('titulo')} - {o.get('ubicacion')}")
            continue
        if not not_blacklisted(o):
            print(f"[filtro] descartada por blacklist: {o.get('empresa')}")
            continue
        filtered.append(o)
    return filtered
