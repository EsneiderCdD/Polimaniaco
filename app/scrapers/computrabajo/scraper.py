# app/scrapers/computrabajo/scraper.py

"""
Scraper mínimo para Computrabajo.
Ejecutar: python -m app.scrapers.computrabajo.scraper
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.computrabajo.com.co"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36"
}

def fetch_search_page(termino="desarrollador-de-software", ubicacion="colombia"):
    """
    Descarga la página de resultados de búsqueda.
    """
    url = f"{BASE_URL}/trabajo-de-{termino}-en-{ubicacion}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text

def parse_search_results(html, max_results=10):
    """
    Parsea el HTML y devuelve una lista de ofertas (diccionarios).
    """
    soup = BeautifulSoup(html, "html.parser")
    ofertas = []

    # Cada oferta suele estar en un contenedor <article> o similar
    cards = soup.find_all("article", limit=max_results)

    for c in cards:
        # Título y URL
        titulo_tag = c.find("a", href=True)
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else "N/A"
        url = BASE_URL + titulo_tag["href"] if titulo_tag else None

        # Empresa
        empresa_tag = c.find("p", class_="dIB")
        empresa = empresa_tag.get_text(strip=True) if empresa_tag else "N/A"

        # Ubicación
        ubicacion_tag = c.find("p", class_="fs16")
        ubicacion = ubicacion_tag.get_text(strip=True) if ubicacion_tag else "N/A"

        # Fecha de publicación (texto)
        fecha_tag = c.find("p", class_="fc_base")
        fecha = fecha_tag.get_text(strip=True) if fecha_tag else "N/A"

        # Descripción breve
        desc_tag = c.find("p", class_="fs13")
        descripcion = desc_tag.get_text(strip=True) if desc_tag else ""

        oferta = {
            "titulo": titulo,
            "empresa": empresa,
            "ubicacion": ubicacion,
            "fecha_publicacion": fecha,  # luego convertimos a date
            "url": url,
            "descripcion": descripcion,
            "fuente": "Computrabajo"
        }
        ofertas.append(oferta)

    return ofertas

def main():
    html = fetch_search_page()
    ofertas = parse_search_results(html, max_results=5)
    print("Ofertas encontradas:")
    for o in ofertas:
        print(o)

if __name__ == "__main__":
    main()
