#!/usr/bin/env python3
import logging
import time
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait

from config.settings import ERROR_LOG_PATH
from src.servant_xbot.utils.helpers import setup_chrome_driver, format_brazilian_date
from src.servant_xbot.amazon.scraper import AmazonScraper
from src.servant_xbot.database.firebase import FirebaseManager


def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(ERROR_LOG_PATH),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Starting product update at {format_brazilian_date()}")
    
    # Initialize Chrome driver
    driver = setup_chrome_driver(headless=True)
    wait = WebDriverWait(driver, 20)
    
    try:
        # Initialize scraper
        scraper = AmazonScraper(driver, wait)
        
        # Initialize Firebase manager
        db_manager = FirebaseManager()
        
        # Get all products from the database
        products = db_manager.get_all_products()
        logger.info(f"Found {len(products)} products to update")
        
        # Update each product
        for i, product in enumerate(products):
            try:
                logger.info(f"Processing product {i+1}/{len(products)}: {product.name}")
                
                # Get latest product details
                updated_product = scraper.get_product_details(product.url)
                
                if updated_product:
                    # Keep affiliate URL if it exists
                    if product.affiliate_url:
                        updated_product.affiliate_url = product.affiliate_url
                    
                    # Store the previous price as last_price
                    updated_product.last_price = product.price
                    
                    # Update timestamp
                    updated_product.updated_at = datetime.now()
                    
                    # Update in database
                    index = i + 1  # Assuming 1-indexed in the database
                    db_manager.update_product(index, updated_product)
                    
                    # Log price changes
                    if product.price != updated_product.price:
                        logger.info(f"Price changed for {product.name}: {product.price} -> {updated_product.price}")
                
                # Rate limiting
                time.sleep(2)
            
            except Exception as e:
                logger.error(f"Error updating product {product.name}: {str(e)}")
        
        logger.info(f"Product update completed at {format_brazilian_date()}")
    
    finally:
        driver.quit()


if __name__ == "__main__":
    main()