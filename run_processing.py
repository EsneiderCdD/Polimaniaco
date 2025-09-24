import logging
import re
from datetime import datetime
from app import create_app, db
from app.models.models import Oferta, AnalisisResultado
from app.processing.utils import normalize_text

logging.basicConfig(level=logging.INFO)

# 🧩 Diccionario de stack tecnológico
STACK = {
    "lenguajes": [
        "php", "javascript", "node.js", "c#", "html5", "css3", "sql",
        "json", "c", "linq", "typescript", "python"
    ],
    "frameworks": [
        "shopify", "magento", "woocommerce", "vtex",
        "laravel", "vue.js", "quasar", "angular",
        ".net core", "asp.net core", "scrum", "kanban",
        "wordpress", "odoo"
    ],
    "librerias": ["bootstrap", "jquery", "ajax"],
    "bases_datos": ["mysql", "sql server", "mongodb"],
    "nube_devops": ["azure", "azure devops", "docker", "kubernetes"],
    "control_versiones": ["git"],
    "arquitectura_metodologias": [
        "microservicios", "restful", "soa", "poo", "async/await",
        "inyección de dependencias", "singleton", "solid",
        "cliente-servidor", "n-capas"
    ],
    "integraciones": ["pasarelas de pago", "apis", "webservices"],
    "inteligencia_artificial": ["inteligencia artificial", "ia"],
    "ofimatica_gestion": [
        "jira", "asana", "trello", "excel", "google workspace",
        "drive", "sheets", "docs"
    ],
    "ciberseguridad": ["ciberseguridad", "unit testing", "buenas prácticas"],
    "marketing_digital": ["seo", "marketing digital"],
    "erp_lowcode": ["wordpress", "odoo"]
}


def detectar_modalidad(texto: str) -> str:
    """Detecta modalidad en el texto de la descripción."""
    texto = texto.lower()
    if any(p in texto for p in ["remoto", "teletrabajo", "home office"]):
        return "Remoto"
    if "híbrido" in texto or "mixto" in texto:
        return "Híbrido"
    if "presencial" in texto or "en oficina" in texto:
        return "Presencial"
    return None


def extraer_stack(texto: str) -> dict:
    """Extrae stack tecnológico de la descripción según categorías."""
    if not texto:
        return {cat: [] for cat in STACK.keys()}

    texto = normalize_text(texto)
    encontrados = {cat: [] for cat in STACK.keys()}

    for categoria, items in STACK.items():
        for item in items:
            pattern = r"\b" + re.escape(item.lower()) + r"\b"
            if re.search(pattern, texto):
                encontrados[categoria].append(item)

    # Convertir listas a strings separados por coma
    return {cat: ", ".join(sorted(set(vals))) for cat, vals in encontrados.items()}


def main():
    logging.info("🔎 Iniciando procesamiento real...")

    app = create_app()
    with app.app_context():
        ofertas = Oferta.query.filter(Oferta.descripcion.isnot(None)).all()

        for o in ofertas:
            # Buscar si ya existe resultado previo
            resultado = AnalisisResultado.query.filter_by(oferta_id=o.id).first()
            if not resultado:
                resultado = AnalisisResultado(oferta_id=o.id)

            # Copiar datos de oferta
            resultado.fecha = o.fecha_publicacion
            resultado.ciudad = o.ubicacion
            resultado.modalidad = detectar_modalidad(o.descripcion or "")
            resultado.cargo = o.titulo

            # Extraer stack tecnológico
            stack = extraer_stack(o.descripcion or "")
            resultado.lenguajes = stack["lenguajes"]
            resultado.frameworks = stack["frameworks"]
            resultado.librerias = stack["librerias"]
            resultado.bases_datos = stack["bases_datos"]
            resultado.nube_devops = stack["nube_devops"]
            resultado.control_versiones = stack["control_versiones"]
            resultado.arquitectura_metodologias = stack["arquitectura_metodologias"]
            resultado.integraciones = stack["integraciones"]
            resultado.inteligencia_artificial = stack["inteligencia_artificial"]
            resultado.ofimatica_gestion = stack["ofimatica_gestion"]
            resultado.ciberseguridad = stack["ciberseguridad"]
            resultado.marketing_digital = stack["marketing_digital"]
            resultado.erp_lowcode = stack["erp_lowcode"]

            # Fecha del análisis
            resultado.fecha_analisis = datetime.utcnow()

            db.session.add(resultado)
            db.session.commit()

            logging.info(
                f"Oferta {o.id} procesada → "
                f"Lenguajes: {resultado.lenguajes} | Frameworks: {resultado.frameworks}"
            )

        logging.info("✅ Procesamiento terminado. Datos guardados en analisis_resultados.")


if __name__ == "__main__":
    main()
