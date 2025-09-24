from app import create_app
from app.extensions import db
from app.models.models import AnalisisResultado
from app.processing.tech_extractor import TECH_CATEGORIES, extract_stack

app = create_app()

# Perfil de usuario (tus skills)
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

def compute_compatibility(analisis_skills, user_skills):
    score = 0
    for category, skills in user_skills.items():
        oferta_skills = analisis_skills.get(category, [])
        for s in skills:
            if s.lower() in [x.lower() for x in oferta_skills]:
                score += 1
    return score

with app.app_context():
    analisis_list = AnalisisResultado.query.all()

    for a in analisis_list:
        # Extraemos el stack de la oferta
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

        # Calculamos compatibilidad
        puntaje = compute_compatibility(analisis_skills, USER_PROFILE)

        # Asignamos puntaje y URL desde la oferta relacionada
        a.compatibilidad = puntaje
        a.url = a.oferta.url if a.oferta else None

    db.session.commit()

    # Mostrar resultados ordenados
    resultados_ordenados = sorted(analisis_list, key=lambda x: x.compatibilidad, reverse=True)
    for r in resultados_ordenados:
        print(f"Puntaje: {r.compatibilidad}, Título: {r.cargo}, URL: {r.url}")
