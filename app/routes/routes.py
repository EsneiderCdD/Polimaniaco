from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import Oferta, Busqueda, Nota

bp = Blueprint('api', __name__)

# Endpoint para listar todas las ofertas
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

# Endpoint para agregar una oferta manualmente (para pruebas)
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

# --- Endpoints para Busquedas ---
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

# --- Endpoints para Notas ---
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
