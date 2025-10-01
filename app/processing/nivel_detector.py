import re
from .utils import normalize_text

# Palabras clave por nivel (español e inglés)
NIVEL_KEYWORDS = {
    "junior_positivo": [
        "junior", "trainee", "auxiliar", "asistente",
        "sin experiencia", "recién egresado", "recien egresado",
        "practicante", "aprendiz", "entry level", "entrada",
        "principiante", "iniciando", "primer empleo",
        "0-1 año", "0-2 años", "menos de 2 años"
    ],
    "junior_negativo": [
        "senior", "líder", "lider", "lead", "arquitecto",
        "experto", "especialista senior", "jefe",
        "5+ años", "5 años de experiencia", "experiencia amplia",
        "más de 3 años", "mas de 3 años", "mínimo 4 años",
        "minimo 4 años"
    ],
    "mid_keywords": [
        "semi senior", "semisenior", "mid level", "intermedio",
        "2-4 años", "3 años de experiencia", "experiencia moderada"
    ],
    "senior_keywords": [
        "senior", "líder técnico", "lider tecnico", "tech lead",
        "arquitecto", "especialista", "experto",
        "5+ años", "más de 5 años", "amplia experiencia"
    ]
}


def calcular_nivel_score(texto_completo: str) -> int:
    """
    Analiza el texto (título + descripción) y devuelve un score de nivel.
    
    Retorna:
        +10 a +5: Claramente junior
        +4 a +1: Probablemente junior
        0: Neutro/ambiguo
        -1 a -4: Probablemente mid/senior
        -5 a -10: Claramente senior/líder
    """
    if not texto_completo:
        return 0
    
    texto = normalize_text(texto_completo)
    
    score = 0
    
    # Buscar keywords junior positivas (+2 por cada una, máx 3 matches)
    junior_pos_count = 0
    for kw in NIVEL_KEYWORDS["junior_positivo"]:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if re.search(pattern, texto) and junior_pos_count < 3:
            score += 2
            junior_pos_count += 1
    
    # Buscar keywords junior negativas (-3 por cada una, máx 2 matches)
    junior_neg_count = 0
    for kw in NIVEL_KEYWORDS["junior_negativo"]:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if re.search(pattern, texto) and junior_neg_count < 2:
            score -= 3
            junior_neg_count += 1
    
    # Buscar keywords mid (neutro, pero baja score si es muy alto)
    for kw in NIVEL_KEYWORDS["mid_keywords"]:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if re.search(pattern, texto):
            score -= 1
            break  # Solo una vez
    
    # Buscar keywords senior (-2 por cada una, máx 2 matches)
    senior_count = 0
    for kw in NIVEL_KEYWORDS["senior_keywords"]:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if re.search(pattern, texto) and senior_count < 2:
            score -= 2
            senior_count += 1
    
    # Limitar rango a [-10, +10]
    score = max(-10, min(10, score))
    
    return score


def interpretar_nivel_score(score: int) -> str:
    """
    Convierte el score numérico en una etiqueta legible.
    """
    if score >= 5:
        return "Junior Alta Confianza"
    elif score >= 1:
        return "Junior Probable"
    elif score == 0:
        return "Neutro/Ambiguo"
    elif score >= -4:
        return "Mid/Senior Probable"
    else:
        return "Senior Alta Confianza"