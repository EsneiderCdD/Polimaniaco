import requests
from bs4 import BeautifulSoup
from app import create_app
from app.extensions import db
from app.models import Oferta

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36"
}

def fetch_offer_detail(url: str) -> str:
    """
    Extrae descripción completa de la oferta desde la página de detalle.
    Usa <p class="mbB"> como selector principal.
    """
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Buscar contenedor principal que incluya los <p class="mbB">
        p_tags = soup.find_all("p", class_="mbB")
        if not p_tags:
            # fallback: buscar cualquier div que contenga "descripcion"
            div_fallback = soup.find("div", class_=lambda c: c and "descripcion" in c.lower())
            if div_fallback:
                return div_fallback.get_text(" ", strip=True)
            return "Descripción no disponible"

        descripcion = " ".join(p.get_text(" ", strip=True) for p in p_tags)
        return descripcion.strip() or "Descripción no disponible"

    except Exception as e:
        print(f"[fetch_offer_detail] Error al obtener {url}: {e}")
        return "Descripción no disponible"


def update_missing_descriptions():
    """
    Recorre todas las ofertas en DB con descripcion vacía o 'Descripción no disponible'
    y actualiza con el contenido completo.
    """
    app = create_app()
    with app.app_context():
        ofertas = Oferta.query.filter(
            (Oferta.descripcion == None) | (Oferta.descripcion == "Descripción no disponible")
        ).all()
        print(f"[update_missing_descriptions] Total ofertas a actualizar: {len(ofertas)}")

        for i, o in enumerate(ofertas, start=1):
            desc = fetch_offer_detail(o.url)
            o.descripcion = desc
            db.session.add(o)
            print(f"[update_missing_descriptions] Procesadas {i}/{len(ofertas)}")

        db.session.commit()
        print(f"[update_missing_descriptions] Actualización completa.")


if __name__ == "__main__":
    update_missing_descriptions()
