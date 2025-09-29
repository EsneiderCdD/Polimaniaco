# app/scrapers/computrabajo/scraper.py
import random
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import LOCATION, MAX_RESULTS, MAX_PAGES, REQUEST_DELAY
from .utils import parse_hace_to_timedelta, title_is_duplicate
from .filters import apply_filters

from app import create_app
from app.extensions import db
from app.models import Oferta

BASE_URL = "https://www.computrabajo.com.co"

# Lista de user-agents realistas (rotar entre ellos)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"
]

# Headers base (completos y realistas)
HEADERS_BASE = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}

# Search terms (puedes mantener o extender)
SEARCH_TERMS = [
    "desarrollador-de-software",
    "desarrollador-web",
    "desarrollador-fullstack",
    "desarrollador-frontend"
]


def make_session():
    """Crea sesión requests con reintentos para errores transitorios."""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    # No establecer User-Agent aquí: lo ponemos por request para rotarlo.
    return session


def get_random_headers(request_count: int, referer: str = None):
    """Construye headers rotativos y 'afeitados' para parecer un navegador real."""
    headers = dict(HEADERS_BASE)  # copia
    headers["User-Agent"] = random.choice(USER_AGENTS)

    # Referer: simula navegación
    if referer:
        headers["Referer"] = referer
    else:
        headers["Referer"] = f"{BASE_URL}/"

    # Simula cabeceras de fetch propias de navegadores modernos
    # (puede variar — aquí se añaden solo si tiene sentido)
    headers["Sec-Fetch-Site"] = "same-origin"
    headers["Sec-Fetch-Mode"] = "navigate"
    headers["Sec-Fetch-Dest"] = "document"
    return headers


def smart_delay(request_count: int, base_range=None):
    """
    Delay 'humano' y progresivo.
    - base_range: tuple(min,max) en segundos (si None, derivado de REQUEST_DELAY)
    """
    if base_range is None:
        try:
            base_range = (max(1, REQUEST_DELAY[0] * 1.5), max(2, REQUEST_DELAY[1] * 1.5))
        except Exception:
            base_range = (3, 8)

    delay = random.uniform(base_range[0], base_range[1])

    # incrementar delays después de muchas requests
    if request_count > 40:
        delay += random.uniform(4, 8)
    elif request_count > 20:
        delay += random.uniform(2, 5)

    # cada 10 requests, hay una pausa más larga (simula que la persona revisa otros resultados)
    if request_count % 10 == 0 and request_count != 0:
        extra = random.uniform(15, 40)
        print(f"[scraper] Checkpoint pause extra de {extra:.1f}s (request #{request_count})")
        delay += extra

    print(f"[scraper] Durmiendo {delay:.2f}s (request #{request_count})")
    time.sleep(delay)


def build_search_url(term, location=LOCATION, page=None):
    """
    Construye la URL de búsqueda.
    Se acepta `page` si se usa paginación con query params o path (Computrabajo usa rutas).
    """
    base = f"{BASE_URL}/trabajo-de-{term}-en-{location}"
    if page and isinstance(page, int) and page > 1:
        # Computrabajo usa /p{n} o parámetros; el código original detecta next via href,
        # así que es seguro simplemente usar la base y seguir enlaces 'next'
        return base  # nos apoyamos en find_next_page_url
    return base


def fetch_page(session: requests.Session, url: str, request_count: int, max_retries: int = 3):
    """
    Obtiene HTML de la página con manejo de 403 y reintentos adaptativos.
    Lanza Exception si no puede recuperarse.
    """
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            if request_count > 0:
                smart_delay(request_count)

            headers = get_random_headers(request_count, referer=BASE_URL)
            print(f"[scraper] Request #{request_count + 1} -> {url} (attempt {attempt})")
            r = session.get(url, headers=headers, timeout=20)
            status = r.status_code

            if status == 403:
                print(f"[scraper] Recibido 403 (attempt {attempt}) en {url}")
                # esperar más y reintentar (backoff aleatorio)
                if attempt < max_retries:
                    wait = random.uniform(10, 25) * attempt
                    print(f"[scraper] Esperando {wait:.1f}s antes de reintentar por 403...")
                    time.sleep(wait)
                    last_exc = Exception("403")
                    continue
                else:
                    raise Exception("403 Forbidden persistente")
            r.raise_for_status()
            return r.text
        except requests.exceptions.RequestException as e:
            print(f"[scraper] Error request attempt {attempt} para {url}: {e}")
            last_exc = e
            # backoff entre reintentos
            if attempt < max_retries:
                time.sleep(random.uniform(4, 10) * attempt)
            else:
                break

    raise last_exc or Exception("No se pudo obtener la página")


def parse_offers_from_soup(soup, max_to_take=50):
    """Extrae ofertas de la página de resultados (intenta ser robusto con distintos HTML)"""
    ofertas = []
    # Buscar artículos / tarjetas que contienen la oferta
    cards = soup.find_all("article")
    if not cards:
        # fallback: buscar por contenedores comunes
        cards = soup.find_all("div", class_=lambda c: c and ("offer" in c.lower() or "job" in c.lower()))

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
    """Detecta el enlace a la siguiente página de resultados."""
    a_rel = soup.find("a", rel="next")
    if a_rel and a_rel.get("href"):
        return urljoin(BASE_URL, a_rel["href"])

    for a in soup.find_all("a", href=True):
        txt = a.get_text(" ", strip=True).lower()
        if "siguiente" in txt or "sig." in txt or "next" in txt:
            return urljoin(BASE_URL, a["href"])
    return None


def collect_offers(term, max_total=MAX_RESULTS, max_pages=MAX_PAGES):
    """
    Colecta ofertas para un término dado usando la estrategia anti-bloqueo.
    """
    session = make_session()
    collected = []
    seen_urls = set()
    seen_titles = set()
    page_url = build_search_url(term)
    pages = 0
    request_count = 0

    print(f"[scraper] Iniciando recolección para término: {term}")
    while page_url and len(collected) < max_total and pages < max_pages:
        try:
            print(f"[scraper] fetch page: {page_url} (page {pages+1})")
            html = fetch_page(session, page_url, request_count)
            request_count += 1

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

            # Delay entre páginas
            if page_url and len(collected) < max_total:
                smart_delay(request_count)

        except Exception as e:
            print(f"[scraper] Error en collect_offers (page {pages+1}): {e}")
            # Si fue un 403 persistente, damos una pausa larga y salimos (puedes ajustar)
            if "403" in str(e).lower():
                print("[scraper] 403 persistente detectado. Pausa larga de 60s y reintento.")
                time.sleep(60)
                # Intentamos una vez más con la misma página
                try:
                    html = fetch_page(session, page_url, request_count)
                    request_count += 1
                    soup = BeautifulSoup(html, "html.parser")
                    offers = parse_offers_from_soup(soup, max_to_take=50)
                    for o in offers:
                        if not o["url"] or o["url"] in seen_urls:
                            continue
                        seen_urls.add(o["url"])
                        collected.append(o)
                except Exception as e2:
                    print(f"[scraper] Segundo intento falló: {e2}")
                    break
            else:
                break

    print(f"[scraper] total crudas para {term}: {len(collected)}")
    return collected


def guardar_ofertas_db(ofertas):
    """Guarda ofertas en DB, evitando duplicados por URL y calculando fecha_publicacion."""
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
                descripcion=o.get("descripcion"),  # placeholder posible
                fuente=o.get("fuente")
            )
            db.session.add(nueva)
            nuevas += 1
        db.session.commit()
        print(f"[scraper] guardadas en DB: {nuevas}")


def main():
    """Scraper principal. Mantiene compatibilidad con tu flujo actual."""
    todas_filtradas = []
    for i, term in enumerate(SEARCH_TERMS):
        print(f"[main] Procesando término {i+1}/{len(SEARCH_TERMS)}: {term}")
        try:
            crudas = collect_offers(term)
            filtradas = apply_filters(crudas)
            print(f"[main] después de filtros para {term}: {len(filtradas)}")
            todas_filtradas.extend(filtradas)

            # Pausa realista entre términos
            if i < len(SEARCH_TERMS) - 1:
                pausa = random.uniform(30, 90)
                print(f"[main] Pausa entre términos: {pausa:.1f}s")
                time.sleep(pausa)

        except Exception as e:
            print(f"[main] Error procesando término {term}: {e}")
            continue

    # Eliminar duplicados globales por URL
    seen_urls_global = set()
    final_guardar = []
    for o in todas_filtradas:
        if o["url"] in seen_urls_global:
            continue
        seen_urls_global.add(o["url"])
        final_guardar.append(o)

    print(f"[main] Guardando {len(final_guardar)} ofertas en DB...")
    guardar_ofertas_db(final_guardar)
    print(f"[main] Scraping completado. Total final: {len(final_guardar)}")


if __name__ == "__main__":
    main()
