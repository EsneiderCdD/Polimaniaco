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

    # Datos principales de la oferta (copiados para conveniencia)
    fecha = db.Column(db.DateTime)
    ciudad = db.Column(db.String(255))
    modalidad = db.Column(db.String(255))
    cargo = db.Column(db.String(255))

    # Stack tecnológico: columnas amplias (todas opcionales al inicio)
    lenguajes = db.Column(db.Text)               # Ej: "PHP, JavaScript, Python"
    frameworks = db.Column(db.Text)              # Ej: "Laravel, Vue.js"
    librerias = db.Column(db.Text)               # Ej: "Bootstrap, jQuery"
    bases_datos = db.Column(db.Text)             # Ej: "MySQL, SQL Server"
    nube_devops = db.Column(db.Text)             # Ej: "Azure, Docker"
    control_versiones = db.Column(db.Text)       # Ej: "Git"
    arquitectura_metodologias = db.Column(db.Text) # Ej: "Microservicios, SOLID"
    integraciones = db.Column(db.Text)           # Ej: "APIs, Pasarelas de pago"
    inteligencia_artificial = db.Column(db.Text) # Ej: "IA básica"
    ofimatica_gestion = db.Column(db.Text)       # Ej: "Jira, Trello, Excel"
    ciberseguridad = db.Column(db.Text)          # Ej: "Unit Testing, Buenas prácticas"
    marketing_digital = db.Column(db.Text)       # Ej: "SEO, Marketing digital"
    erp_lowcode = db.Column(db.Text)             # Ej: "Odoo, WordPress"

    # Fecha de creación de este análisis
    fecha_analisis = db.Column(db.DateTime, default=datetime.utcnow)
