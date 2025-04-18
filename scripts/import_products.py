#!/usr/bin/env python3
import logging
import time
import argparse
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait

from config.settings import ERROR_LOG_PATH, AFFILIATE_LINKS_PATH
from src.servant_xbot.utils.helpers import setup_chrome_driver, is_amazon_affiliate_link
from src.servant_xbot.amazon.scraper import AmazonScraper
from src.servant_xbot.database.firebase import FirebaseManager


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Import Amazon product links to the database"
    )
    parser.add_argument(
        "--file",
        type=str,
        default=AFFILIATE_LINKS_PATH,
        help=f"File containing Amazon links (default: {AFFILIATE_LINKS_PATH})",
    )
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(ERROR_LOG_PATH), logging.StreamHandler()],
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Starting product import from {args.file}")

    # Check if file exists
    if not Path(args.file).exists():
        logger.error(f"File {args.file} does not exist")
        return

    # Initialize Chrome driver
    driver = setup_chrome_driver(headless=True)
    wait = WebDriverWait(driver, 20)

    try:
        # Initialize scraper
        scraper = AmazonScraper(driver, wait)

        # Initialize Firebase manager
        db_manager = FirebaseManager()

        # Read links from file
        with open(args.file, "r") as f:
            links = [line.strip() for line in f.readlines() if line.strip()]

        # Filter valid Amazon/affiliate links
        valid_links = [link for link in links if is_amazon_affiliate_link(link)]
        logger.info(f"Found {len(valid_links)} valid links out of {len(links)} total")

        # Process each link
        for i, link in enumerate(valid_links):
            try:
                logger.info(f"Processing link {i + 1}/{len(valid_links)}: {link}")

                # Get product details
                product = scraper.get_product_details(link)

                if product:
                    # If this is an affiliate link, store it
                    if "amzn.to" in link:
                        product.affiliate_url = link

                    # Add to database
                    db_manager.add_product(product)
                    logger.info(f"Added product: {product.name}")

                # Rate limiting
                time.sleep(2)

            except Exception as e:
                logger.error(f"Error processing link {link}: {str(e)}")

        logger.info(f"Product import completed. Processed {len(valid_links)} links.")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
