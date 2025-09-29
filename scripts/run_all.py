import logging
from app import create_app
from app.scrapers.computrabajo.micro_scraper_description import get_offers, get_details
from scripts.calc_compatibilidad import run_compatibility
from scripts.calcular_metricas import calcular_metricas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_all_process():
    """Ejecuta todo el proceso completo: scraper -> processing -> compatibilidad -> métricas"""
    app = create_app()
    with app.app_context():
        try:
            logger.info("1/5 - Iniciando scraper de ofertas...")
            get_offers()
            logger.info("✓ Scraper de ofertas completado")

            logger.info("2/5 - Iniciando scraper de descripciones...")
            get_details()
            logger.info("✓ Scraper de descripciones completado")

            logger.info("3/5 - Iniciando procesamiento de ofertas...")
            from run_processing import main as process_main
            process_main()
            logger.info("✓ Procesamiento completado")

            logger.info("4/5 - Calculando compatibilidad...")
            run_compatibility()
            logger.info("✓ Compatibilidad calculada")

            logger.info("5/5 - Calculando métricas...")
            calcular_metricas()
            logger.info("✓ Métricas calculadas")

            logger.info("🎉 PROCESO COMPLETO FINALIZADO")
            return True

        except Exception as e:
            logger.exception(f"Error en el proceso: {e}")
            return False

if __name__ == "__main__":
    run_all_process()