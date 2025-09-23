"""
Scraper principal modular para Computrabajo.
- Pagine automáticamente hasta MAX_RESULTS o MAX_PAGES.
- Extrae tarjetas, deja raw_fecha, luego aplica filtros.
- Evita duplicados por URL y por título dentro de la misma ejecución.
- Guarda en la DB usando app.create_app() context.
- Solo guarda descripción básica; descripciones completas las llena micro_scraper_descripcion.py
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone

from .config import LOCATION, MAX_RESULTS, MAX_PAGES, REQUEST_DELAY
from .utils import sleep_between_requests, title_is_duplicate, parse_hace_to_timedelta
from .filters import apply_filters

from app import create_app
from app.extensions import db
from app.models import Oferta

BASE_URL = "https://www.computrabajo.com.co"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/121.0 Safari/537.36"
}

SEARCH_TERMS = [
    "desarrollador-de-software",
    "desarrollador-web",
    "desarrollador-fullstack",
    "desarrollador-frontend"
]

def build_search_url(term, location=LOCATION):
    return f"{BASE_URL}/trabajo-de-{term}-en-{location}"

def fetch_page(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text

def fetch_offer_detail(url: str) -> str:
    """Coloca descripción placeholder; micro_scraper llenará descripción completa"""
    return "Descripción no disponible"

def parse_offers_from_soup(soup, max_to_take=50):
    """Extrae ofertas de la página de resultados"""
    ofertas = []
    cards = soup.find_all("article")
    for c in cards:
        a = c.find("a", href=True)
        titulo = a.get_text(" ", strip=True) if a else "N/A"
        href = a["href"] if a else None
        url = urljoin(BASE_URL, href) if href else None

        empresa, ubicacion, raw_fecha, descripcion = "N/A", "N/A", None, ""

        p_tags = c.find_all("p")
        for p in p_tags:
            txt = p.get_text(" ", strip=True)
            if not txt:
                continue
            low = txt.lower()
            if ("hace" in low) or ("min" in low) or ("hora" in low) or ("hoy" in low):
                raw_fecha = txt
            elif empresa == "N/A":
                empresa = txt
            elif ubicacion == "N/A":
                ubicacion = txt
            else:
                descripcion += " " + txt

        oferta = {
            "titulo": titulo,
            "empresa": empresa,
            "ubicacion": ubicacion,
            "raw_fecha": raw_fecha,
            "url": url,
            "descripcion": descripcion.strip() or "Oferta oculta",
            "fuente": "Computrabajo"
        }
        ofertas.append(oferta)
        if len(ofertas) >= max_to_take:
            break
    return ofertas

def find_next_page_url(soup):
    a_rel = soup.find("a", rel="next")
    if a_rel and a_rel.get("href"):
        return urljoin(BASE_URL, a_rel["href"])
    for a in soup.find_all("a", href=True):
        txt = a.get_text(" ", strip=True).lower()
        if "siguiente" in txt or "sig." in txt or "next" in txt:
            return urljoin(BASE_URL, a["href"])
    return None

def collect_offers(term, max_total=MAX_RESULTS, max_pages=MAX_PAGES):
    collected = []
    seen_urls = set()
    seen_titles = set()
    page_url = build_search_url(term)
    pages = 0

    while page_url and len(collected) < max_total and pages < max_pages:
        print(f"[scraper] fetch page: {page_url}")
        html = fetch_page(page_url)
        soup = BeautifulSoup(html, "html.parser")

        offers = parse_offers_from_soup(soup, max_to_take=50)
        print(f"[scraper] ofertas en página: {len(offers)}")

        for o in offers:
            if not o["url"]:
                continue
            if o["url"] in seen_urls:
                continue
            if title_is_duplicate(o["titulo"], seen_titles):
                continue
            seen_urls.add(o["url"])
            collected.append(o)
            if len(collected) >= max_total:
                break

        page_url = find_next_page_url(soup)
        pages += 1
        if page_url and len(collected) < max_total:
            sleep_between_requests(REQUEST_DELAY)
        else:
            break

    print(f"[scraper] total crudas para {term}: {len(collected)}")
    return collected

def guardar_ofertas_db(ofertas):
    """Guarda ofertas en DB, evitando duplicados por URL y calcula fecha_publicacion desde raw_fecha"""
    app = create_app()
    with app.app_context():
        nuevas = 0
        for o in ofertas:
            if not o.get("url"):
                continue
            existe = Oferta.query.filter_by(url=o["url"]).first()
            if existe:
                continue

            raw = o.get("raw_fecha")
            td = parse_hace_to_timedelta(raw)
            fecha_pub = datetime.now(timezone.utc) - td if td else datetime.now(timezone.utc)

            nueva = Oferta(
                titulo=o.get("titulo"),
                empresa=o.get("empresa"),
                ubicacion=o.get("ubicacion"),
                raw_fecha=raw,
                fecha_publicacion=fecha_pub,
                url=o.get("url"),
                descripcion=o.get("descripcion"),  # placeholder
                fuente=o.get("fuente")
            )
            db.session.add(nueva)
            nuevas += 1
        db.session.commit()
        print(f"[scraper] guardadas en DB: {nuevas}")

def main():
    todas_filtradas = []
    for term in SEARCH_TERMS:
        crudas = collect_offers(term)
        filtradas = apply_filters(crudas)
        print(f"[scraper] después de filtros para {term}: {len(filtradas)}")
        todas_filtradas.extend(filtradas)

    # Evitar duplicados globales antes de guardar
    seen_urls_global = set()
    final_guardar = []
    for o in todas_filtradas:
        if o["url"] in seen_urls_global:
            continue
        seen_urls_global.add(o["url"])
        final_guardar.append(o)

    guardar_ofertas_db(final_guardar)
    print(f"[scraper] total combinadas filtradas: {len(final_guardar)}")

if __name__ == "__main__":
    main()
