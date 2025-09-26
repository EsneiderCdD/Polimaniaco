import re
from typing import Dict, List
from .utils import normalize_text

# ----------------- Tecnologías por categoría -----------------
TECH_CATEGORIES: Dict[str, List[str]] = {
    "lenguajes": ["php", "javascript", "node.js", "c#", "html5", "css3",
                  "sql", "json", "c", "linq", "typescript", "python",
                  "pl/sql", "java", "ruby"],
    "frameworks": ["shopify", "magento", "woocommerce", "vtex", "laravel",
                   "vue.js", "quasar", "angular", ".net core", "asp.net core",
                   "scrum", "kanban", "wordpress", "odoo", "django", "fastapi",
                   "nestjs", "spring webflux", "react", "ruby on rails",
                   "express.js", "vuetify", "hotwire"],
    "librerias": ["bootstrap", "jquery", "ajax", "tailwind", "sequelize", "typeorm"],
    "bases_datos": ["mysql", "sql server", "mongodb", "postgresql", "redis",
                    "firestore", "firebase"],
    "nube_devops": ["azure", "azure devops", "docker", "kubernetes", "aws",
                    "gcp", "ci/cd", "helm", "grafana"],
    "control_versiones": ["git", "github actions"],
    "arquitectura_metodologias": ["microservicios", "restful", "soa", "poo",
                                  "async/await", "inyeccion de dependencias",
                                  "inyección de dependencias", "singleton",
                                  "solid", "cliente-servidor", "n-capas",
                                  "graphql", "websockets", "sse", "grpc", "http/2",
                                  "oauth", "jwt", "tdd"],
    "integraciones": ["pasarelas de pago", "apis", "webservices", "api rest",
                      "servicios web", "integraciones"],
    "inteligencia_artificial": ["inteligencia artificial", "ia", "langchain",
                                "langgraph", "llm", "embeddings", "rag", "crewai",
                                "mcp", "machine learning", "ml", "deep learning",
                                "ai", "artificial intelligence"],
    "ofimatica_gestion": ["jira", "asana", "trello", "excel", "google workspace",
                          "drive", "sheets", "docs", "sonarcloud", "sonarqube",
                          "postman", "swagger", "jest", "cypress", "vitest"],
    "ciberseguridad": ["ciberseguridad", "unit testing", "wcag",
                       "security", "testing", "pruebas unitarias",
                       "seguridad informatica", "seguridad informática"],
    "marketing_digital": ["seo", "marketing digital", "crm", "sem", "google ads",
                          "facebook ads", "social media", "redes sociales"],
    "erp_lowcode": ["wordpress", "odoo", "flutterflow", "low code", "no code",
                    "sap", "erp", "crm systems"],
}

# ----------------- Sinónimos / variaciones -----------------
TECH_SYNONYMS = {
    "javascript": ["javascript", "js"],
    "node.js": ["node.js", "node"],
    "react": ["react", "react.js", "reactjs"],
    "postgresql": ["postgresql", "postgres", "pg"],
    "c#": ["c#", "c sharp"],
    "html5": ["html5", "html"],
    "css3": ["css3", "css"],
    "sql": ["sql"],
    "python": ["python"],
    "bootstrap": ["bootstrap"],
    "tailwind": ["tailwind", "tailwindcss"],
    "git": ["git", "github actions"],
    "angular": ["angular", "angular.js"],
    "vue.js": ["vue.js", "vuejs", "vue"],
    "laravel": ["laravel"],
    "django": ["django"],
    "fastapi": ["fastapi"],
    "nestjs": ["nestjs"],
    ".net core": [".net core", "dotnet core", "asp.net core"],
    "ruby on rails": ["ruby on rails", "rails"],
}

# ----------------- Función de extracción -----------------
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
            synonyms = TECH_SYNONYMS.get(tech, [tech])
            for syn in synonyms:
                pattern = r"\b" + re.escape(syn.lower()) + r"\b"
                if re.search(pattern, text):
                    found[category].append(tech)
                    break  # Evita contar múltiples sinónimos de la misma tech

    # Eliminar duplicados
    for category in found:
        found[category] = sorted(set(found[category]))

    return found
