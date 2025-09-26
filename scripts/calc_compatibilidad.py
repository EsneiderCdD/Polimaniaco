from app import create_app
from app.extensions import db
from app.models.models import AnalisisResultado

# Perfil del usuario: puntaje base = 1 por skill, luego puedes ponderar
USER_PROFILE = {
    "lenguajes": ["javascript", "html5", "css3", "sql", "typescript", "python"],
    "frameworks": ["react"],
    "librerias": ["bootstrap", "tailwind"],
    "bases_datos": ["postgresql"],
    "nube_devops": [],
    "control_versiones": ["git"],
    "arquitectura_metodologias": [],
    "integraciones": ["pasarelas de pago", "apis", "webservices", "api rest", "servicios web", "integraciones"],
    "inteligencia_artificial": [],
    "ofimatica_gestion": [],
    "ciberseguridad": [],
    "marketing_digital": ["seo"],
    "erp_lowcode": [],
}

# Ponderación opcional por categoría (1 a 10)
CATEGORY_WEIGHTS = {
    "lenguajes": 3,
    "frameworks": 5,
    "librerias": 3,
    "bases_datos": 2,
    "nube_devops": 2,
    "control_versiones": 3,
    "arquitectura_metodologias": 1,
    "integraciones": 3,
    "inteligencia_artificial": 1,
    "ofimatica_gestion": 1,
    "ciberseguridad": 1,
    "marketing_digital": 1,
    "erp_lowcode": 1,
}

# Puntaje máximo permitido
MAX_SCORE = 100

def compute_compatibility(analisis_skills, user_skills, category_weights=None, max_score=100):
    """
    Calcula compatibilidad entre perfil del usuario y una oferta.
    - analisis_skills: dict con skills de la oferta
    - user_skills: dict con skills del usuario
    - category_weights: dict opcional de ponderaciones por categoría
    - max_score: truncamiento máximo
    Retorna: puntaje total y detalle por categoría
    """
    category_weights = category_weights or {}
    score = 0
    details = {}

    for category, skills in user_skills.items():
        oferta_skills = analisis_skills.get(category, [])
        match_count = sum(1 for s in skills if s.lower() in [x.lower() for x in oferta_skills])
        weight = category_weights.get(category, 1)
        weighted_score = match_count * weight
        details[category] = weighted_score
        score += weighted_score

    # Truncamiento
    if score > max_score:
        score = max_score

    return score, details

def run_compatibility():
    app = create_app()
    with app.app_context():
        analisis_list = AnalisisResultado.query.all()

        for a in analisis_list:
            # Extraemos stack de la oferta como listas
            analisis_skills = {
                "lenguajes": a.lenguajes.split(", ") if a.lenguajes else [],
                "frameworks": a.frameworks.split(", ") if a.frameworks else [],
                "librerias": a.librerias.split(", ") if a.librerias else [],
                "bases_datos": a.bases_datos.split(", ") if a.bases_datos else [],
                "nube_devops": a.nube_devops.split(", ") if a.nube_devops else [],
                "control_versiones": a.control_versiones.split(", ") if a.control_versiones else [],
                "arquitectura_metodologias": a.arquitectura_metodologias.split(", ") if a.arquitectura_metodologias else [],
                "integraciones": a.integraciones.split(", ") if a.integraciones else [],
                "inteligencia_artificial": a.inteligencia_artificial.split(", ") if a.inteligencia_artificial else [],
                "ofimatica_gestion": a.ofimatica_gestion.split(", ") if a.ofimatica_gestion else [],
                "ciberseguridad": a.ciberseguridad.split(", ") if a.ciberseguridad else [],
                "marketing_digital": a.marketing_digital.split(", ") if a.marketing_digital else [],
                "erp_lowcode": a.erp_lowcode.split(", ") if a.erp_lowcode else [],
            }

            puntaje, detalle = compute_compatibility(
                analisis_skills, USER_PROFILE, CATEGORY_WEIGHTS, MAX_SCORE
            )

            # Asignamos puntaje y URL
            a.compatibilidad = puntaje
            a.url = a.oferta.url if a.oferta else None

            # Guardamos detalles si quieres depurarlos (opcional)
            # a.detalle_compatibilidad = str(detalle)

        db.session.commit()

        # Mostrar resultados ordenados
        resultados_ordenados = sorted(analisis_list, key=lambda x: x.compatibilidad, reverse=True)
        for r in resultados_ordenados:
            print(f"Puntaje: {r.compatibilidad}, Título: {r.cargo}, URL: {r.url}, Detalle: {detalle}")

if __name__ == "__main__":
    run_compatibility()
