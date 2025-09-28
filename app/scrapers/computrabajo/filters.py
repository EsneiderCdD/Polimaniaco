from .config import BLACKLIST_COMPANIES
from .utils import within_last_24h, normalize_text

def apply_filters(ofertas):
    """Aplica filtros de blacklist y fecha de publicación (≤24h)."""
    filtradas = []
    for o in ofertas:
        empresa = normalize_text(o.get("empresa", ""))
        fecha = o.get("raw_fecha")

        # filtro blacklist
        for b in BLACKLIST_COMPANIES:
            if normalize_text(b) in empresa:
                print(f"[filters] Excluida por blacklist: {empresa}")
                break
        else:  # solo entra aquí si no se ejecutó el break
            # filtro fecha
            if not within_last_24h(fecha):
                print(f"[filters] Excluida por fecha >24h: {fecha}")
                continue

            filtradas.append(o)

    return filtradas
