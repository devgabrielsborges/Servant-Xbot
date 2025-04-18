#!/usr/bin/env python3
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait

from config.settings import BESTSELLER_TOPICS_PATH, AFFILIATE_LINKS_PATH, ERROR_LOG_PATH
from src.servant_xbot.amazon.auth import AmazonAuthenticator
from src.servant_xbot.amazon.scraper import AmazonScraper
from src.servant_xbot.amazon.affiliate import AffiliateGenerator
from src.servant_xbot.database.firebase import FirebaseManager


def main():
    # Ensure all directories exist
    Path(BESTSELLER_TOPICS_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(AFFILIATE_LINKS_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(ERROR_LOG_PATH).parent.mkdir(parents=True, exist_ok=True)

    # Set up logging to console and file
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(ERROR_LOG_PATH), logging.StreamHandler()],
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bestseller scraping process")

    if not Path(BESTSELLER_TOPICS_PATH).exists():
        logger.error(f"Topics file not found: {BESTSELLER_TOPICS_PATH}")
        return

    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    driver = uc.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        auth = AmazonAuthenticator(driver, wait)

        # Try to load cookies first
        if not auth.load_cookies():
            # If cookies don't exist or are invalid, log in
            logger.info("Need to perform login")
            login_success = auth.login()
            if not login_success:
                logger.error("Login failed, cannot continue")
                driver.save_screenshot(
                    str(ERROR_LOG_PATH).replace(".log", "_login_failed.png")
                )
                return

        # Add a random delay
        time.sleep(random.uniform(2, 5))

        scraper = AmazonScraper(driver, wait)

        affiliate_gen = AffiliateGenerator(driver, wait)

        try:
            db_manager = FirebaseManager()
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            db_manager = None

        # Read bestseller category URLs
        with open(BESTSELLER_TOPICS_PATH, "r") as f:
            topics = f.readlines()
            logger.info(f"Loaded {len(topics)} category topics")

        # Process each category
        for topic in topics:
            topic = topic.strip()
            if not topic:
                continue

            logger.info(f"Processing category: {topic}")
            products = scraper.get_bestsellers(topic)

            if not products:
                logger.warning(f"No products found for category: {topic}")
                continue

            logger.info(f"Found {len(products)} products in category {topic}")

            for i, product in enumerate(products):
                try:
                    logger.info(
                        f"Processing product {i + 1}/{len(products)}: {product.name}"
                    )

                    affiliate_url = affiliate_gen.generate_affiliate_link(product.url)
                    if affiliate_url:
                        product.affiliate_url = affiliate_url

                        # Add to database if Firebase is available
                        if db_manager:
                            db_manager.add_product(product)

                        with open(AFFILIATE_LINKS_PATH, "a") as file:
                            file.write(f"{affiliate_url}\n")
                            logger.info(f"Saved affiliate link for {product.name}")
                    else:
                        logger.warning(
                            f"Failed to generate affiliate link for {product.name}"
                        )

                    # Rate limiting with random delay
                    time.sleep(random.uniform(2, 5))

                except Exception as e:
                    logger.error(f"Error processing product {product.name}: {str(e)}")

        logger.info("Bestseller scraping process completed successfully")

    except Exception as e:
        logger.error(f"Unexpected error in main process: {str(e)}")

    finally:
        try:
            driver.quit()
            logger.info("Browser closed")
        except:
            logger.warning("Error while closing browser")


if __name__ == "__main__":
    main()
