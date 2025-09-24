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
