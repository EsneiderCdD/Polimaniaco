import re
from typing import Dict, List
from .utils import normalize_text

# Diccionario de stack tecnológico por categorías
TECH_CATEGORIES: Dict[str, List[str]] = {
    "lenguajes": [
        "php", "javascript", "node.js", "c#", "html5", "css3",
        "sql", "json", "c", "linq", "typescript", "python"
    ],
    "frameworks": [
        "shopify", "magento", "woocommerce", "vtex", "laravel",
        "vue.js", "quasar", "angular", ".net core", "asp.net core",
        "scrum", "kanban", "wordpress", "odoo"
    ],
    "librerias": ["bootstrap", "jquery", "ajax"],
    "bases_datos": ["mysql", "sql server", "mongodb"],
    "nube_devops": ["azure", "azure devops", "docker", "kubernetes"],
    "control_versiones": ["git"],
    "arquitectura_metodologias": [
        "microservicios", "restful", "soa", "poo",
        "async/await", "inyeccion de dependencias",
        "singleton", "solid", "cliente-servidor", "n-capas"
    ],
    "integraciones": ["pasarelas de pago", "apis", "webservices"],
    "inteligencia_artificial": ["inteligencia artificial", "ia"],
    "ofimatica_gestion": [
        "jira", "asana", "trello", "excel", "google workspace",
        "drive", "sheets", "docs"
    ],
    "ciberseguridad": ["ciberseguridad", "unit testing"],
    "marketing_digital": ["seo", "marketing digital"],
    "erp_lowcode": ["wordpress", "odoo"]
}


def extract_stack(text: str) -> Dict[str, List[str]]:
    """
    Extrae tecnologías de un texto y las organiza por categoría.
    Retorna un dict con categorías → lista de tecnologías encontradas.
    """
    if not text:
        return {cat: [] for cat in TECH_CATEGORIES}

    text = normalize_text(text)
    found: Dict[str, List[str]] = {cat: [] for cat in TECH_CATEGORIES}

    for category, tech_list in TECH_CATEGORIES.items():
        for tech in tech_list:
            pattern = r"\b" + re.escape(tech.lower()) + r"\b"
            if re.search(pattern, text):
                found[category].append(tech)

    # Eliminamos duplicados
    for category in found:
        found[category] = sorted(set(found[category]))

    return found
