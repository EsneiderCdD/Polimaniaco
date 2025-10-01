from app import create_app
from app.extensions import db
from app.models.models import AnalisisResultado

# ----------------- Perfil del usuario -----------------
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

# ----------------- Ponderación por categoría -----------------
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

# ----------------- Peso por skill individual -----------------
SKILL_WEIGHTS = {
    "javascript": 5,
    "html5": 4,
    "css3": 3,
    "sql": 4,
    "typescript": 4,
    "python": 5,
    "react": 5,
    "bootstrap": 3,
    "tailwind": 3,
    "postgresql": 4,
    "git": 2,
    "seo": 1,
    "pasarelas de pago": 2,
    "apis": 3,
    "webservices": 3,
    "api rest": 3,
    "servicios web": 3,
    "integraciones": 2
}

# ----------------- Puntaje máximo permitido -----------------
MAX_SCORE = 100

# ----------------- Función de compatibilidad (SIN CAMBIOS) -----------------
def compute_compatibility(analisis_skills, user_skills, category_weights=None, skill_weights=None, max_score=100):
    """
    Calcula compatibilidad entre perfil del usuario y una oferta.
    """
    category_weights = category_weights or {}
    skill_weights = skill_weights or {}
    score = 0
    details = {}

    for category, skills in user_skills.items():
        oferta_skills = analisis_skills.get(category, [])
        category_score = 0
        for s in skills:
            if s.lower() in [x.lower() for x in oferta_skills]:
                category_score += skill_weights.get(s, 1)
        weight = category_weights.get(category, 1)
        weighted_score = category_score * weight
        details[category] = weighted_score
        score += weighted_score

    if score > max_score:
        score = max_score

    return score, details


# 🆕 NUEVA FUNCIÓN: Calcular compatibilidad final con factor de nivel
def compute_final_score(stack_score, nivel_score):
    """
    Combina el puntaje de stack con el factor de nivel.
    
    Lógica:
    - Si nivel_score >= 3 (junior claro) → Bonus +15%
    - Si nivel_score >= 1 → Bonus +10%
    - Si nivel_score == 0 → Sin cambio
    - Si nivel_score <= -3 (senior claro) → Penalización -20%
    - Si nivel_score < 0 → Penalización -10%
    """
    if nivel_score >= 3:
        bonus = stack_score * 0.15
        return min(100, stack_score + bonus)
    elif nivel_score >= 1:
        bonus = stack_score * 0.10
        return min(100, stack_score + bonus)
    elif nivel_score == 0:
        return stack_score
    elif nivel_score <= -3:
        penalty = stack_score * 0.20
        return max(0, stack_score - penalty)
    else:  # nivel_score < 0
        penalty = stack_score * 0.10
        return max(0, stack_score - penalty)


# ----------------- Ejecutar compatibilidad -----------------
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

            # Calcular puntaje de stack (sin cambios)
            stack_score, detalle = compute_compatibility(
                analisis_skills, USER_PROFILE, CATEGORY_WEIGHTS, SKILL_WEIGHTS, MAX_SCORE
            )

            # 🆕 NUEVO: Ajustar con factor de nivel
            nivel_score = a.nivel_score or 0
            final_score = compute_final_score(stack_score, nivel_score)

            # Asignar puntaje final y URL
            a.compatibilidad = round(final_score, 2)
            a.url = a.oferta.url if a.oferta else None

        db.session.commit()

        # Mostrar resultados ordenados (top 10)
        resultados_ordenados = sorted(analisis_list, key=lambda x: x.compatibilidad, reverse=True)
        print("\n" + "="*80)
        print("TOP 10 OFERTAS MÁS COMPATIBLES")
        print("="*80)
        for i, r in enumerate(resultados_ordenados[:10], 1):
            print(f"\n{i}. {r.cargo}")
            print(f"   Compatibilidad: {r.compatibilidad:.2f} | Nivel Score: {r.nivel_score}")
            print(f"   Ciudad: {r.ciudad} | Modalidad: {r.modalidad}")
            print(f"   URL: {r.url}")
        print("\n" + "="*80)

if __name__ == "__main__":
    run_compatibility()