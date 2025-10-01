from app.extensions import db
from datetime import datetime, timezone

class Oferta(db.Model):
    __tablename__ = 'ofertas'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    empresa = db.Column(db.String(255))
    ubicacion = db.Column(db.String(255))
    fecha_publicacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    raw_fecha = db.Column(db.String(50))
    url = db.Column(db.String(512), unique=True)
    descripcion = db.Column(db.Text)
    fuente = db.Column(db.String(50))

class Busqueda(db.Model):
    __tablename__ = 'busquedas'
    id = db.Column(db.Integer, primary_key=True)
    termino = db.Column(db.String(255))
    filtros = db.Column(db.JSON)
    fecha_ejecucion = db.Column(db.DateTime, default=datetime.utcnow)

class Nota(db.Model):
    __tablename__ = 'notas'
    id = db.Column(db.Integer, primary_key=True)
    oferta_id = db.Column(db.Integer, db.ForeignKey('ofertas.id'))
    nota = db.Column(db.Text)


# 🔹 NUEVAS TABLAS 🔹

class AnalisisOferta(db.Model):
    __tablename__ = 'analisis_ofertas'
    id = db.Column(db.Integer, primary_key=True)
    oferta_id = db.Column(db.Integer, db.ForeignKey('ofertas.id'), unique=True, nullable=False)
    fecha_analisis = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    ciudad = db.Column(db.String(255))
    modalidad = db.Column(db.String(100))
    cargo = db.Column(db.String(255))

    oferta = db.relationship("Oferta", backref=db.backref("analisis", uselist=False))


class CategoriaTecnologia(db.Model):
    __tablename__ = 'categorias_tecnologia'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)


class Tecnologia(db.Model):
    __tablename__ = 'tecnologias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_tecnologia.id'), nullable=False)

    categoria = db.relationship("CategoriaTecnologia", backref="tecnologias")


class OfertaTecnologia(db.Model):
    __tablename__ = 'ofertas_tecnologias'
    id = db.Column(db.Integer, primary_key=True)
    oferta_id = db.Column(db.Integer, db.ForeignKey('ofertas.id'), nullable=False)
    tecnologia_id = db.Column(db.Integer, db.ForeignKey('tecnologias.id'), nullable=False)

    oferta = db.relationship("Oferta", backref="ofertas_tecnologias")
    tecnologia = db.relationship("Tecnologia", backref="tecnologias_ofertas")


class AnalisisResultado(db.Model):
    __tablename__ = 'analisis_resultados'

    id = db.Column(db.Integer, primary_key=True)

    # Relación con oferta original
    oferta_id = db.Column(db.Integer, db.ForeignKey('ofertas.id'), nullable=False)
    oferta = db.relationship('Oferta', backref=db.backref('analisis_resultado', lazy=True))

    # URL de la oferta
    url = db.Column(db.String(512))

    # Puntaje de compatibilidad
    compatibilidad = db.Column(db.Float, default=0.0)

    # 🆕 NUEVO: Scoring de nivel (junior/mid/senior)
    nivel_score = db.Column(db.Integer, default=0)  # Rango: -10 a +10

    # Datos principales de la oferta
    fecha = db.Column(db.DateTime)
    ciudad = db.Column(db.String(255))
    modalidad = db.Column(db.String(255))
    cargo = db.Column(db.String(255))

    # Stack tecnológico (columnas amplias - todas opcionales)
    lenguajes = db.Column(db.Text)
    frameworks = db.Column(db.Text)
    librerias = db.Column(db.Text)
    bases_datos = db.Column(db.Text)
    nube_devops = db.Column(db.Text)
    control_versiones = db.Column(db.Text)
    arquitectura_metodologias = db.Column(db.Text)
    integraciones = db.Column(db.Text)
    inteligencia_artificial = db.Column(db.Text)
    ofimatica_gestion = db.Column(db.Text)
    ciberseguridad = db.Column(db.Text)
    marketing_digital = db.Column(db.Text)
    erp_lowcode = db.Column(db.Text)

    # Fecha de creación de este análisis
    fecha_analisis = db.Column(db.DateTime, default=datetime.utcnow)

# ----------------- NUEVAS TABLAS DE METRICAS -----------------

class MetricasTecnologia(db.Model):
    __tablename__ = 'metricas_tecnologia'
    id = db.Column(db.Integer, primary_key=True)
    nombre_tecnologia = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50))
    conteo = db.Column(db.Integer, default=0)
    porcentaje = db.Column(db.Float, default=0.0)
    fecha_calculo = db.Column(db.DateTime, default=datetime.utcnow)

class MetricasUbicacion(db.Model):
    __tablename__ = 'metricas_ubicacion'
    id = db.Column(db.Integer, primary_key=True)
    ciudad = db.Column(db.String(255), nullable=False)
    conteo = db.Column(db.Integer, default=0)
    porcentaje = db.Column(db.Float, default=0.0)
    fecha_calculo = db.Column(db.DateTime, default=datetime.utcnow)

class MetricasModalidad(db.Model):
    __tablename__ = 'metricas_modalidad'
    id = db.Column(db.Integer, primary_key=True)
    modalidad = db.Column(db.String(50), nullable=False)
    conteo = db.Column(db.Integer, default=0)
    porcentaje = db.Column(db.Float, default=0.0)
    fecha_calculo = db.Column(db.DateTime, default=datetime.utcnow)

class MetricasGenerales(db.Model):
    __tablename__ = 'metricas_generales'
    id = db.Column(db.Integer, primary_key=True)
    total_ofertas = db.Column(db.Integer, default=0)
    promedio_compatibilidad = db.Column(db.Float, default=0.0)
    fecha_calculo = db.Column(db.DateTime, default=datetime.utcnow)
