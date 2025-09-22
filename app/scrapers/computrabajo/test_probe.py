# app/scrapers/computrabajo/test_probe.py
"""
Script ligero para decidir Requests+BS vs Playwright.
Ejecutar: python -m app.scrapers.computrabajo.test_probe
"""

import requests
from bs4 import BeautifulSoup
import json

# URL base para la búsqueda inicial (Desarrollador de software en Colombia)
URL = "https://www.computrabajo.com.co/trabajo-de-desarrollador-de-software"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36"
}

def fetch_html(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    print(f"HTTP {r.status_code} — {len(r.text)} bytes recibidos")
    return r.text

def has_json_ld_jobposting(soup):
    # Busca <script type="application/ld+json"> ... { "@type": "JobPosting" } ...
    scripts = soup.find_all("script", {"type": "application/ld+json"})
    for s in scripts:
        try:
            payload = json.loads(s.string or "{}")
        except Exception:
            continue
        # payload puede ser dict o lista
        if isinstance(payload, dict):
            arr = [payload]
        else:
            arr = payload
        for item in arr:
            if isinstance(item, dict) and item.get("@type", "").lower() == "jobposting":
                return True, item
    return False, None

def find_text_signals(soup):
    # Señales simples: textos como "Hace 3 horas", "Hace 2 días"
    text = soup.get_text(separator=" ", strip=True)
    found = []
    keywords = ["Hace", "hace", "hoy", "día", "días", "hora", "horas"]
    for kw in keywords:
        if kw in text:
            found.append(kw)
    # también buscar elementos tipo tarjetas: article, .offer, .job
    cards = soup.find_all(["article", "li", "div"])
    sample = 0
    for c in cards[:30]:
        t = c.get_text(" ", strip=True)
        if "Hace" in t or "hace" in t:
            sample += 1
    return {"text_signals": len(found)>0, "sample_cards_with_hace": sample}

def main():
    html = fetch_html(URL)
    soup = BeautifulSoup(html, "html.parser")

    # 1) JSON-LD check
    has_ld, ld_item = has_json_ld_jobposting(soup)
    print("JSON-LD JobPosting encontrado?:", has_ld)
    if has_ld:
        print("Ejemplo JSON-LD (parcial):")
        # imprimimos campos claves si existen
        keys = ["title", "datePosted", "hiringOrganization", "jobLocation"]
        for k in keys:
            print(k, ":", ld_item.get(k))

    # 2) Señales de texto "Hace X"
    signals = find_text_signals(soup)
    print("Señales de fecha en HTML:", signals)

    # 3) Conteo aproximado de enlaces que parecen ofertas (href con '/trabajo-' o '/empleos' o '/job/')
    links = soup.find_all("a", href=True)
    job_like = [a for a in links if any(x in a['href'].lower() for x in ["/trabajo-", "/empleo", "/job", "/oferta"])]
    print("Total enlaces:", len(links), "Enlaces que parecen ofertas (heurística):", len(job_like))
    if job_like:
        print("Ejemplo hrefs (5):")
        for a in job_like[:5]:
            print(" -", a['href'][:200])

    print("\nInterpretación sugerida:")
    if has_ld or signals["sample_cards_with_hace"] > 0 or len(job_like) > 5:
        print(" → Parece que la página contiene ofertas en el HTML. Empezamos con Requests + BeautifulSoup.")
    else:
        print(" → Poca señal de contenido en HTML: probablemente se carga con JavaScript. Usar Playwright.")
    print("Fin del probe.")

if __name__ == "__main__":
    main()
