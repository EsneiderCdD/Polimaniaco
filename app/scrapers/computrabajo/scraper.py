# app/scrapers/computrabajo/scraper.py

"""
Scraper principal modular para Computrabajo.
- Pagina automáticamente (siguiendo "Siguiente" o rel=next) hasta MAX_RESULTS o MAX_PAGES.
- Extrae tarjetas, deja raw_fecha, luego aplica filtros (Hoy, Remoto, Blacklist).
- Evita duplicados por URL y por título dentro de la misma ejecución.
- Guarda en la DB usando app.create_app() context.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

from .config import TERM, LOCATION, MAX_RESULTS, MAX_PAGES, REQUEST_DELAY
from .utils import sleep_between_requests, title_is_duplicate
from .filters import apply_filters

from app import create_app
from app.extensions import db
from app.models import Oferta

BASE_URL = "https://www.computrabajo.com.co"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36"
}

def build_search_url(term=TERM, location=LOCATION):
    return f"{BASE_URL}/trabajo-de-{term}-en-{location}"

def fetch_page(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text

def parse_offers_from_soup(soup, max_to_take=50):
    """
    Extrae ofertas desde un BeautifulSoup de una página de resultados.
    Devuelve lista de dicts con: titulo, empresa, ubicacion, raw_fecha, url, descripcion, fuente
    """
    ofertas = []
    cards = soup.find_all("article")
    for c in cards:
        # título y URL
        a = c.find("a", href=True)
        titulo = a.get_text(" ", strip=True) if a else "N/A"
        href = a["href"] if a else None
        url = urljoin(BASE_URL, href) if href else None

        empresa, ubicacion, raw_fecha, descripcion = "N/A", "N/A", None, ""

        # leer todos los <p> de la tarjeta para identificar
        p_tags = c.find_all("p")
        for p in p_tags:
            txt = p.get_text(" ", strip=True)
            if not txt:
                continue
            low = txt.lower()
            # heurística: si contiene 'hace' o 'min' o 'hora' es fecha
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
            "raw_fecha": raw_fecha,   # texto tipo "Hace 3 horas"
            # fecha_publicacion real se colocará como ahora() al guardar
            "url": url,
            "descripcion": descripcion.strip() or "Oferta oculta",
            "fuente": "Computrabajo"
        }
        ofertas.append(oferta)
        if len(ofertas) >= max_to_take:
            break
    return ofertas

def find_next_page_url(soup):
    """
    Intenta encontrar la URL de la siguiente página de resultados.
    Busca <a rel="next"> o enlaces con texto 'Siguiente' / 'siguiente'.
    """
    a_rel = soup.find("a", rel="next")
    if a_rel and a_rel.get("href"):
        return urljoin(BASE_URL, a_rel["href"])
    # fallback: buscar enlaces con texto 'Siguiente' o 'siguiente'
    for a in soup.find_all("a", href=True):
        txt = a.get_text(" ", strip=True).lower()
        if "siguiente" in txt or "sig." in txt or "next" in txt:
            return urljoin(BASE_URL, a["href"])
    return None

def collect_offers(max_total=MAX_RESULTS, max_pages=MAX_PAGES):
    collected = []
    seen_urls = set()
    seen_titles = set()
    page_url = build_search_url()
    pages = 0

    while page_url and len(collected) < max_total and pages < max_pages:
        print(f"[scraper] fetch page: {page_url}")
        html = fetch_page(page_url)
        soup = BeautifulSoup(html, "html.parser")

        offers = parse_offers_from_soup(soup, max_to_take=50)
        print(f"[scraper] ofertas en página: {len(offers)}")

        # deduplicado por url y por título (en la misma ejecución)
        for o in offers:
            if not o["url"]:
                continue
            if o["url"] in seen_urls:
                continue
            if title_is_duplicate(o["titulo"], seen_titles):
                # title_is_duplicate añade el título si no existía
                # si devolvió True (ya visto) lo saltamos
                continue
            seen_urls.add(o["url"])
            collected.append(o)
            if len(collected) >= max_total:
                break

        # intenta siguiente página
        page_url = find_next_page_url(soup)
        pages += 1
        if page_url and len(collected) < max_total:
            sleep_between_requests(REQUEST_DELAY)
        else:
            break

    print(f"[scraper] total recogidas (sin filtrar): {len(collected)}")
    return collected

def guardar_ofertas_db(ofertas):
    """
    Guarda en DB las ofertas (evitando duplicados por URL).
    Usa create_app() y app_context.
    """
    app = create_app()
    with app.app_context():
        nuevas = 0
        for o in ofertas:
            if not o.get("url"):
                continue
            existe = Oferta.query.filter_by(url=o["url"]).first()
            if existe:
                continue
            nueva = Oferta(
                titulo=o.get("titulo"),
                empresa=o.get("empresa"),
                ubicacion=o.get("ubicacion"),
                fecha_publicacion=datetime.utcnow(),  # guardamos fecha de inserción
                url=o.get("url"),
                descripcion=o.get("descripcion"),
                fuente=o.get("fuente")
            )
            db.session.add(nueva)
            nuevas += 1
        db.session.commit()
        print(f"[scraper] guardadas en DB: {nuevas}")

def main():
    # 1) recolectar sin filtrar hasta MAX_RESULTS (ej: 150)
    crudas = collect_offers()
    # 2) aplicar filtros (Hoy, Remoto, Blacklist)
    filtradas = apply_filters(crudas)
    print(f"[scraper] después de filtros (Hoy + Remoto + Blacklist): {len(filtradas)}")
    # limitar a MAX_RESULTS por si sobrepasa
    filtradas = filtradas[:MAX_RESULTS]
    # 3) guardar en DB
    guardar_ofertas_db(filtradas)

if __name__ == "__main__":
    main()

