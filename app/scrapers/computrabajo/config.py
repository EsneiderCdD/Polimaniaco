# app/scrapers/computrabajo/config.py

# Términos / ubicación base
TERM = "desarrollador-de-software"   # palabra clave (sin espacios, con guiones)
LOCATION = "colombia"

# Límites
MAX_RESULTS = 150   # máximo global que queremos obtener (ajusta a 100/150/200)
MAX_PAGES = 10      # protección extra por si hay muchas páginas

# Lista negra (empresas a ignorar). Edita esto según tu preferencia.
BLACKLIST_COMPANIES = [
    "bairesdev"
]

# Tiempo entre requests (segundos)
REQUEST_DELAY = 1.5
