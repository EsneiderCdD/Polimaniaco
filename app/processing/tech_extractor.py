import re
from typing import List, Dict
from .utils import normalize_text

# Lista inicial de tecnologías conocidas
# 🚨 Esta lista se puede extender fácilmente en el futuro
TECHNOLOGIES = [
    "python", "java", "javascript", "typescript", "c#", ".net",
    "react", "angular", "vue", "django", "flask",
    "sql", "mysql", "postgresql", "mongodb",
    "aws", "azure", "gcp", "docker", "kubernetes",
    "html", "css", "php", "ruby", "go", "rust"
]

def extract_technologies(text: str) -> List[str]:
    """
    Extrae las tecnologías mencionadas en un texto.
    Retorna una lista única de tecnologías detectadas.
    """
    if not text:
        return []

    text = normalize_text(text)

    found = []
    for tech in TECHNOLOGIES:
        # regex con word boundaries para evitar falsos positivos
        pattern = r"\b" + re.escape(tech.lower()) + r"\b"
        if re.search(pattern, text):
            found.append(tech)

    return sorted(set(found))


def extract_from_offers(offers: List[Dict]) -> List[Dict]:
    """
    Procesa múltiples ofertas (dict con 'id' y 'description').
    Retorna [{id, technologies: [...]}, ...]
    """
    results = []
    for offer in offers:
        techs = extract_technologies(offer.get("description", ""))
        results.append({
            "id": offer.get("id"),
            "technologies": techs
        })
    return results
