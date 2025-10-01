from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import Oferta, Busqueda, Nota
from app.models.models import (
    Oferta, Busqueda, Nota, AnalisisResultado,
    MetricasTecnologia,
    MetricasUbicacion,
    MetricasModalidad,
    MetricasGenerales
)
import threading
import logging

bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# ==================== ENDPOINTS OFERTAS ====================
@bp.route('/ofertas', methods=['GET'])
def get_ofertas():
    ofertas = Oferta.query.all()
    resultados = []
    for oferta in ofertas:
        resultados.append({
            'id': oferta.id,
            'titulo': oferta.titulo,
            'empresa': oferta.empresa,
            'ubicacion': oferta.ubicacion,
            'fecha_publicacion': oferta.fecha_publicacion.isoformat() if oferta.fecha_publicacion else None,
            'url': oferta.url,
            'descripcion': oferta.descripcion,
            'fuente': oferta.fuente
        })
    return jsonify(resultados), 200

@bp.route('/ofertas', methods=['POST'])
def add_oferta():
    data = request.get_json()
    nueva_oferta = Oferta(
        titulo=data.get('titulo'),
        empresa=data.get('empresa'),
        ubicacion=data.get('ubicacion'),
        fecha_publicacion=data.get('fecha_publicacion'),
        url=data.get('url'),
        descripcion=data.get('descripcion'),
        fuente=data.get('fuente')
    )
    db.session.add(nueva_oferta)
    db.session.commit()
    return jsonify({'mensaje': 'Oferta creada', 'id': nueva_oferta.id}), 201

# ==================== ENDPOINTS BUSQUEDAS ====================
@bp.route('/busquedas', methods=['GET'])
def get_busquedas():
    busquedas = Busqueda.query.all()
    resultados = []
    for b in busquedas:
        resultados.append({
            'id': b.id,
            'termino': b.termino,
            'filtros': b.filtros,
            'fecha_ejecucion': b.fecha_ejecucion.isoformat() if b.fecha_ejecucion else None
        })
    return jsonify(resultados), 200

@bp.route('/busquedas', methods=['POST'])
def add_busqueda():
    data = request.get_json()
    nueva_busqueda = Busqueda(
        termino=data.get('termino'),
        filtros=data.get('filtros'),
        fecha_ejecucion=data.get('fecha_ejecucion')
    )
    db.session.add(nueva_busqueda)
    db.session.commit()
    return jsonify({'mensaje': 'Busqueda creada', 'id': nueva_busqueda.id}), 201

# ==================== ENDPOINTS NOTAS ====================
@bp.route('/notas', methods=['GET'])
def get_notas():
    notas = Nota.query.all()
    resultados = []
    for n in notas:
        resultados.append({
            'id': n.id,
            'oferta_id': n.oferta_id,
            'nota': n.nota
        })
    return jsonify(resultados), 200

@bp.route('/notas', methods=['POST'])
def add_nota():
    data = request.get_json()
    nueva_nota = Nota(
        oferta_id=data.get('oferta_id'),
        nota=data.get('nota')
    )
    db.session.add(nueva_nota)
    db.session.commit()
    return jsonify({'mensaje': 'Nota creada', 'id': nueva_nota.id}), 201

# ==================== ENDPOINTS ANALISIS ====================
@bp.route('/analisis', methods=['GET'])
def get_analisis():
    analisis = AnalisisResultado.query.all()
    resultados = []
    for a in analisis:
        resultados.append({
            'id': a.id,
            'oferta_id': a.oferta_id,
            'url': a.url,
            'compatibilidad': a.compatibilidad,
            'nivel_score': a.nivel_score,
            'fecha': a.fecha.isoformat() if a.fecha else None,
            'ciudad': a.ciudad,
            'modalidad': a.modalidad,
            'cargo': a.cargo,
            'lenguajes': a.lenguajes,
            'frameworks': a.frameworks,
            'librerias': a.librerias,
            'bases_datos': a.bases_datos,
            'nube_devops': a.nube_devops,
            'control_versiones': a.control_versiones,
            'arquitectura_metodologias': a.arquitectura_metodologias,
            'integraciones': a.integraciones,
            'inteligencia_artificial': a.inteligencia_artificial,
            'ofimatica_gestion': a.ofimatica_gestion,
            'ciberseguridad': a.ciberseguridad,
            'marketing_digital': a.marketing_digital,
            'erp_lowcode': a.erp_lowcode,
            'fecha_analisis': a.fecha_analisis.isoformat() if a.fecha_analisis else None
        })
    return jsonify(resultados), 200

# ==================== ENDPOINTS MÉTRICAS ====================
@bp.route('/metricas/tecnologias', methods=['GET'])
def get_metricas_tecnologias():
    metrics = MetricasTecnologia.query.order_by(MetricasTecnologia.conteo.desc()).all()
    return jsonify([
        {
            'nombre_tecnologia': m.nombre_tecnologia,
            'categoria': m.categoria,
            'conteo': m.conteo,
            'porcentaje': m.porcentaje
        } for m in metrics
    ]), 200

@bp.route('/metricas/ubicaciones', methods=['GET'])
def get_metricas_ubicaciones():
    metrics = MetricasUbicacion.query.order_by(MetricasUbicacion.conteo.desc()).all()
    return jsonify([
        {'ciudad': m.ciudad, 'conteo': m.conteo, 'porcentaje': m.porcentaje} for m in metrics
    ]), 200

@bp.route('/metricas/modalidades', methods=['GET'])
def get_metricas_modalidades():
    metrics = MetricasModalidad.query.order_by(MetricasModalidad.conteo.desc()).all()
    return jsonify([
        {'modalidad': m.modalidad, 'conteo': m.conteo, 'porcentaje': m.porcentaje} for m in metrics
    ]), 200

@bp.route('/metricas/generales', methods=['GET'])
def get_metricas_generales():
    metrics = MetricasGenerales.query.all()
    return jsonify([
        {'total_ofertas': m.total_ofertas, 'promedio_compatibilidad': m.promedio_compatibilidad} for m in metrics
    ]), 200

# ==================== ENDPOINTS PROCESO COMPLETO ====================

# Variable global para tracking del estado del proceso
proceso_estado = {
    "en_ejecucion": False,
    "progreso": 0,
    "mensaje": "",
    "error": None
}

def ejecutar_proceso_completo():
    """Ejecuta todo el proceso en un thread separado"""
    global proceso_estado
    
    try:
        from app.scrapers.computrabajo.micro_scraper_description import get_offers, get_details
        from scripts.calc_compatibilidad import run_compatibility
        from scripts.calcular_metricas import calcular_metricas
        from run_processing import main as process_main
        
        proceso_estado["en_ejecucion"] = True
        proceso_estado["error"] = None
        
        # 1. Scraper de ofertas
        proceso_estado["progreso"] = 20
        proceso_estado["mensaje"] = "Recolectando ofertas..."
        logger.info("1/5 - Iniciando scraper de ofertas...")
        get_offers()
        
        # 2. Scraper de descripciones
        proceso_estado["progreso"] = 40
        proceso_estado["mensaje"] = "Obteniendo descripciones completas..."
        logger.info("2/5 - Iniciando scraper de descripciones...")
        get_details()
        
        # 3. Procesamiento
        proceso_estado["progreso"] = 60
        proceso_estado["mensaje"] = "Procesando stack tecnológico..."
        logger.info("3/5 - Iniciando procesamiento de ofertas...")
        process_main()
        
        # 4. Compatibilidad
        proceso_estado["progreso"] = 80
        proceso_estado["mensaje"] = "Calculando compatibilidad..."
        logger.info("4/5 - Calculando compatibilidad...")
        run_compatibility()
        
        # 5. Métricas
        proceso_estado["progreso"] = 90
        proceso_estado["mensaje"] = "Calculando métricas..."
        logger.info("5/5 - Calculando métricas...")
        calcular_metricas()
        
        # Finalizado
        proceso_estado["progreso"] = 100
        proceso_estado["mensaje"] = "Proceso completado exitosamente"
        logger.info("🎉 PROCESO COMPLETO FINALIZADO")
        
    except Exception as e:
        logger.exception(f"Error en el proceso: {e}")
        proceso_estado["error"] = str(e)
        proceso_estado["mensaje"] = f"Error: {str(e)}"
    finally:
        proceso_estado["en_ejecucion"] = False


@bp.route('/ejecutar-proceso', methods=['POST'])
def ejecutar_proceso():
    """Endpoint para ejecutar el proceso completo desde el frontend"""
    global proceso_estado
    
    if proceso_estado["en_ejecucion"]:
        return jsonify({
            "mensaje": "Ya hay un proceso en ejecución",
            "estado": proceso_estado
        }), 409  # Conflict
    
    # Reiniciar estado
    proceso_estado = {
        "en_ejecucion": True,
        "progreso": 0,
        "mensaje": "Iniciando proceso...",
        "error": None
    }
    
    # Ejecutar en un thread separado para no bloquear la respuesta
    thread = threading.Thread(target=ejecutar_proceso_completo)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "mensaje": "Proceso iniciado correctamente",
        "estado": proceso_estado
    }), 202  # Accepted


@bp.route('/estado-proceso', methods=['GET'])
def estado_proceso():
    """Endpoint para consultar el estado del proceso en ejecución"""
    return jsonify(proceso_estado), 200