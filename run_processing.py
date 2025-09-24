import logging
from app import create_app, db
from app.models import Oferta
from app.processing.tech_extractor import extract_from_offers

logging.basicConfig(level=logging.INFO)

def main():
    logging.info("Iniciando procesamiento real...")

    app = create_app()
    with app.app_context():
        # 🔹 Consultamos todas las ofertas con descripción no nula
        ofertas = Oferta.query.filter(Oferta.descripcion.isnot(None)).all()

        # 🔹 Transformamos al formato que necesita extract_from_offers
        offers = [{"id": o.id, "description": o.descripcion} for o in ofertas]

        results = extract_from_offers(offers)

        # 🔹 Mostrar resultados en consola
        for r in results:
            logging.info(f"Oferta {r['id']} → Tecnologías: {r['technologies']}")

if __name__ == "__main__":
    main()
