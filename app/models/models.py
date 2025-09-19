from app.extensions import db

class Oferta(db.Model):
    __tablename__ = 'ofertas'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    empresa = db.Column(db.String(255))
    ubicacion = db.Column(db.String(255))
    fecha_publicacion = db.Column(db.Date)
    url = db.Column(db.String(512))
    descripcion = db.Column(db.Text)
    fuente = db.Column(db.String(50))  # ejemplo: 'FamaEmpleo'

class Busqueda(db.Model):
    __tablename__ = 'busquedas'
    id = db.Column(db.Integer, primary_key=True)
    termino = db.Column(db.String(255))
    filtros = db.Column(db.JSON)
    fecha_ejecucion = db.Column(db.DateTime)

class Nota(db.Model):
    __tablename__ = 'notas'
    id = db.Column(db.Integer, primary_key=True)
    oferta_id = db.Column(db.Integer, db.ForeignKey('ofertas.id'))
    nota = db.Column(db.Text)
