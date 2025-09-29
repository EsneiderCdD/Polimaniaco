# app/scrapers/computrabajo/micro_scraper_description.py
import random
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app import create_app
from app.extensions import db
from app.models import Oferta

# Import main scraper (wrapper) para mantener compatibilidad con tu runflow
from .scraper import main as run_main_scraper

# User agents (mismos que en scraper.py o una lista similar)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

HEADERS_BASE = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
}


def make_session():
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
    return session


def get_random_headers(request_count: int, referer: str = None):
    headers = dict(HEADERS_BASE)
    headers["User-Agent"] = random.choice(USER_AGENTS)
    headers["Referer"] = referer or "https://www.computrabajo.com.co/"
    headers["Sec-Fetch-Site"] = "same-origin"
    headers["Sec-Fetch-Mode"] = "navigate"
    headers["Sec-Fetch-Dest"] = "document"
    return headers


def smart_delay_description(request_count: int):
    """Delay más conservador para requests a páginas de detalle."""
    base = random.uniform(3, 8)
    if request_count > 10:
        base += random.uniform(2, 5)
    if request_count % 5 == 0 and request_count != 0:
        base += random.uniform(10, 25)
    print(f"[detail] Durmiendo {base:.2f}s (request #{request_count})")
    time.sleep(base)


class DescriptionScraper:
    """Clase para manejar requests a páginas de detalle con estrategia anti-bloqueo."""

    def __init__(self):
        self.session = make_session()
        self.request_count = 0

    def fetch_offer_detail(self, url: str, max_retries: int = 3) -> str:
        """
        Intenta obtener la descripción completa de la oferta.
        Devuelve una cadena con la descripción o un placeholder si falla.
        """
        last_exc = None
        for attempt in range(1, max_retries + 1):
            try:
                if self.request_count > 0:
                    smart_delay_description(self.request_count)

                headers = get_random_headers(self.request_count, referer="https://www.computrabajo.com.co/")
                print(f"[detail] Request #{self.request_count + 1} -> {url} (attempt {attempt})")
                resp = self.session.get(url, headers=headers, timeout=25)
                status = resp.status_code
                self.request_count += 1

                if status == 403:
                    print(f"[detail] 403 en detalle (attempt {attempt}) para {url}")
                    if attempt < max_retries:
                        wait = random.uniform(10, 25) * attempt
                        print(f"[detail] Esperando {wait:.1f}s antes de reintentar por 403...")
                        time.sleep(wait)
                        last_exc = Exception("403")
                        continue
                    else:
                        return "Descripción no disponible (403)"

                resp.raise_for_status()

                soup = BeautifulSoup(resp.text, "html.parser")
                description = self.extract_description_multi_selector(soup)
                if description and "acceso denegado" in description.lower():
                    # Página dice que no hay acceso
                    return "Descripción no disponible (acceso denegado)"
                return description or "Descripción no disponible"

            except requests.exceptions.RequestException as e:
                print(f"[detail] Error request attempt {attempt} para {url}: {e}")
                last_exc = e
                if attempt < max_retries:
                    time.sleep(random.uniform(5, 12) * attempt)
                else:
                    break

        # Si fallaron todos los intentos
        if last_exc:
            return f"Descripción no disponible (error: {str(last_exc)})"
        return "Descripción no disponible (max retries)"

    @staticmethod
    def extract_description_multi_selector(soup: BeautifulSoup) -> str:
        """
        Intenta múltiples selectores y fallbacks para extraer la descripción.
        """
        # Selector principal conocido en Computrabajo
        p_tags = soup.find_all("p", class_="mbB")
        if p_tags:
            text = " ".join(p.get_text(" ", strip=True) for p in p_tags if p.get_text(" ", strip=True))
            if text:
                return text

        # Fallback: div con clase que contenga "descripcion"
        div_desc = soup.find("div", class_=lambda c: c and "descripcion" in c.lower())
        if div_desc:
            t = div_desc.get_text(" ", strip=True)
            if t:
                return t

        # Fallback: section o div con id que contenga "descripcion"
        section_desc = soup.find(["section", "div"], id=lambda x: x and "descripcion" in x.lower())
        if section_desc:
            t = section_desc.get_text(" ", strip=True)
            if t:
                return t

        # Fallback: buscar encabezado "Descripción" y tomar siguiente contenido
        for elem in soup.find_all(text=lambda t: t and "descripción" in t.lower()):
            parent = elem.parent
            if parent:
                # buscar párrafos dentro del mismo bloque
                sibling = parent.find_next_sibling()
                if sibling:
                    t = sibling.get_text(" ", strip=True)
                    if t:
                        return t

        # Fallback: buscar párrafos largos
        all_p = soup.find_all("p")
        for p in all_p:
            text = p.get_text(" ", strip=True)
            if len(text) > 120:
                return text

        # Fallback final: obtener todo el main/article
        main_block = soup.find("main") or soup.find("article")
        if main_block:
            t = main_block.get_text(" ", strip=True)
            if t and len(t) > 80:
                return t

        return ""


def update_missing_descriptions():
    """
    Encuentra en la DB ofertas con descripción placeholder y las actualiza con la
    DescriptionScraper. Hace commits parciales para evitar pérdida.
    """
    app = create_app()
    with app.app_context():
        offers = Oferta.query.filter(
            (Oferta.descripcion == None)
            | (Oferta.descripcion == "Descripción no disponible")
            | (Oferta.descripcion == "Oferta oculta")
            | (Oferta.descripcion.like("Descripción no disponible%"))
        ).all()

        print(f"[update_missing_descriptions] Ofertas a actualizar: {len(offers)}")
        if not offers:
            print("[update_missing_descriptions] Nada para actualizar.")
            return

        scraper = DescriptionScraper()
        updated = 0
        errors = 0

        for i, o in enumerate(offers, start=1):
            try:
                print(f"[update_missing_descriptions] ({i}/{len(offers)}) fetch {o.url}")
                desc = scraper.fetch_offer_detail(o.url)
                # Guardar solo si obtenemos algo útil
                if desc and desc not in ["Descripción no disponible", "Oferta oculta"]:
                    o.descripcion = desc
                    db.session.add(o)
                    updated += 1

                    # Commit cada 10 actualizaciones (checkpoint)
                    if updated % 10 == 0:
                        db.session.commit()
                        print(f"[update_missing_descriptions] Checkpoint: {updated} actualizadas")

                else:
                    errors += 1
                    print(f"[update_missing_descriptions] No se obtuvo descripción útil para {o.url}")

                # Pausa extra cada 20 requests para mayor conservadurismo
                if i % 20 == 0:
                    extra = random.uniform(30, 60)
                    print(f"[update_missing_descriptions] Pausa extra de {extra:.1f}s...")
                    time.sleep(extra)

            except Exception as e:
                errors += 1
                print(f"[update_missing_descriptions] Error actualizando oferta {getattr(o, 'id', 'n/a')}: {e}")
                continue

        db.session.commit()
        print("[update_missing_descriptions] ✅ Actualización completada.")
        print(f"  - Actualizadas: {updated}")
        print(f"  - Errores: {errors}")
        print(f"  - Total requests: {scraper.request_count}")


# Compatibilidad con run_scraper.py (API pública)
def get_offers():
    """Ejecuta el scraper principal (lista) y guarda en DB"""
    run_main_scraper()
    return None


def get_details(offers=None):
    """Actualiza descripciones pendientes usando el micro-scraper"""
    update_missing_descriptions()
    return None


if __name__ == "__main__":
    update_missing_descriptions()
