import requests
from bs4 import BeautifulSoup
from app import create_app
from app.extensions import db
from app.models import Oferta

# Import scraper principal
from app.scrapers.computrabajo.scraper import main as run_main_scraper

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36"
}


def fetch_offer_detail(url: str) -> str:
    """
    Extract full job description from the detail page.
    Uses <p class="mbB"> as main selector.
    """
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Find main container with <p class="mbB">
        p_tags = soup.find_all("p", class_="mbB")
        if not p_tags:
            # fallback: find any div containing "descripcion"
            div_fallback = soup.find("div", class_=lambda c: c and "descripcion" in c.lower())
            if div_fallback:
                return div_fallback.get_text(" ", strip=True)
            return "Descripción no disponible"

        description = " ".join(p.get_text(" ", strip=True) for p in p_tags)
        return description.strip() or "Descripción no disponible"

    except Exception as e:
        print(f"[fetch_offer_detail] Error fetching {url}: {e}")
        return "Descripción no disponible"


def update_missing_descriptions():
    """
    Find all offers in DB with empty or placeholder descriptions
    and update them with the full detail.
    """
    app = create_app()
    with app.app_context():
        offers = Oferta.query.filter(
            (Oferta.descripcion == None) | (Oferta.descripcion == "Descripción no disponible") | (Oferta.descripcion == "Oferta oculta")
        ).all()
        print(f"[update_missing_descriptions] Offers to update: {len(offers)}")

        for i, o in enumerate(offers, start=1):
            desc = fetch_offer_detail(o.url)
            o.descripcion = desc
            db.session.add(o)
            print(f"[update_missing_descriptions] Processed {i}/{len(offers)}")

        db.session.commit()
        print(f"[update_missing_descriptions] Update completed.")


# 🔹 API usada por run_scraper.py
def get_offers():
    run_main_scraper()  # guarda en DB
    return None


def get_details(offers=None):
    update_missing_descriptions()  # actualiza en DB
    return None


if __name__ == "__main__":
    update_missing_descriptions()
