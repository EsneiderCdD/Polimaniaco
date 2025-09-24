import logging
from datetime import datetime
from app import create_app, db
from app.models.models import Oferta, AnalisisResultado
from app.processing.tech_extractor import extract_stack

logging.basicConfig(level=logging.INFO)


def main():
    logging.info("🔎 Iniciando procesamiento real...")

    app = create_app()
    with app.app_context():
        ofertas = Oferta.query.filter(Oferta.descripcion.isnot(None)).all()

        for oferta in ofertas:
            stack = extract_stack(oferta.descripcion)

            resultado = AnalisisResultado.query.filter_by(oferta_id=oferta.id).first()
            if not resultado:
                resultado = AnalisisResultado(oferta_id=oferta.id)

            # Campos básicos desde Oferta
            resultado.fecha = oferta.fecha_publicacion
            resultado.ciudad = oferta.ubicacion
            resultado.modalidad = None  # aún no la tenemos en ofertas
            resultado.cargo = oferta.titulo

            # Guardamos stack tecnológico como texto separado por comas
            resultado.lenguajes = ", ".join(stack["lenguajes"])
            resultado.frameworks = ", ".join(stack["frameworks"])
            resultado.librerias = ", ".join(stack["librerias"])
            resultado.bases_datos = ", ".join(stack["bases_datos"])
            resultado.nube_devops = ", ".join(stack["nube_devops"])
            resultado.control_versiones = ", ".join(stack["control_versiones"])
            resultado.arquitectura_metodologias = ", ".join(stack["arquitectura_metodologias"])
            resultado.integraciones = ", ".join(stack["integraciones"])
            resultado.inteligencia_artificial = ", ".join(stack["inteligencia_artificial"])
            resultado.ofimatica_gestion = ", ".join(stack["ofimatica_gestion"])
            resultado.ciberseguridad = ", ".join(stack["ciberseguridad"])
            resultado.marketing_digital = ", ".join(stack["marketing_digital"])
            resultado.erp_lowcode = ", ".join(stack["erp_lowcode"])

            resultado.fecha_analisis = datetime.utcnow()

            db.session.add(resultado)
            logging.info(
                f"Oferta {oferta.id} procesada → Lenguajes: {resultado.lenguajes} | Frameworks: {resultado.frameworks}"
            )

        db.session.commit()
        logging.info("✅ Procesamiento terminado. Datos guardados en analisis_resultados.")


if __name__ == "__main__":
    main()
