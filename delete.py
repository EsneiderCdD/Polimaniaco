from app import create_app
from app.extensions import db
from app.models import Oferta

app = create_app()
with app.app_context():
    num_deleted = Oferta.query.delete()
    db.session.commit()
    print(f"Ofertas eliminadas: {num_deleted}")
