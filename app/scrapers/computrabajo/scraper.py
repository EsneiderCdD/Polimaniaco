import requests
from bs4 import BeautifulSoup
from datetime import datetime
from app.extensions import db
from app.models import Oferta
from app import create_app

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

    cards = soup.find_all("article", limit=max_results)

    for c in cards:
        # Título y URL
        titulo_tag = c.find("a", href=True)
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else "N/A"
        url = BASE_URL + titulo_tag["href"] if titulo_tag else None

        empresa, ubicacion, fecha, descripcion = "N/A", "N/A", None, ""

        # Buscar párrafos dentro de la tarjeta
        p_tags = c.find_all("p")
        for p in p_tags:
            txt = p.get_text(" ", strip=True)
            if not txt:
                continue
            if "Hace" in txt or "hace" in txt or "hora" in txt or "día" in txt:
                fecha = txt  # no lo usamos, pero lo dejamos por referencia
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
            "fecha_publicacion": datetime.utcnow(),
            "url": url,
            "descripcion": descripcion.strip() if descripcion else "Oferta oculta",
            "fuente": "Computrabajo"
        }
        ofertas.append(oferta)

    return ofertas

def guardar_ofertas(ofertas):
    """
    Guarda ofertas nuevas en la DB evitando duplicados por URL.
    """
    nuevas = 0
    for o in ofertas:
        existente = Oferta.query.filter_by(url=o["url"]).first()
        if existente:
            continue
        nueva = Oferta(
            titulo=o["titulo"],
            empresa=o["empresa"],
            ubicacion=o["ubicacion"],
            fecha_publicacion=o["fecha_publicacion"],
            url=o["url"],
            descripcion=o["descripcion"],
            fuente=o["fuente"]
        )
        db.session.add(nueva)
        nuevas += 1
    db.session.commit()
    print(f"Guardadas {nuevas} ofertas nuevas en la DB.")

def main():
    html = fetch_search_page()
    ofertas = parse_search_results(html, max_results=5)
    print("Ofertas extraídas:", len(ofertas))

    app = create_app()
    with app.app_context():
        guardar_ofertas(ofertas)

if __name__ == "__main__":
    main()
