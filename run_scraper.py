import logging
from app.scrapers.computrabajo.micro_scraper_description import get_offers, get_details

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting offers scraper...")
        get_offers()
        logger.info("Offers scraper finished.")

        logger.info("Starting details scraper...")
        get_details()
        logger.info("Details scraper finished.")

    except Exception:
        logger.exception("An error occurred while running the scrapers")


if __name__ == "__main__":
    main()
