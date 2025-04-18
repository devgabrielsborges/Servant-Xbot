import re
import logging
import time
import random
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import (
    presence_of_all_elements_located,
    presence_of_element_located,
)
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    StaleElementReferenceException,
)
from config.settings import ERROR_LOG_PATH
from ..models.product import Product


logger = logging.getLogger(__name__)
handler = logging.FileHandler(ERROR_LOG_PATH)
logger.addHandler(handler)


class AmazonScraper:
    """Handles scraping product information from Amazon."""

    def __init__(self, driver: uc.Chrome, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def _random_sleep(self, min_sec=1, max_sec=3):
        """Sleep for a random time between min_sec and max_sec."""
        time.sleep(random.uniform(min_sec, max_sec))

    def get_bestsellers(self, category_url: str) -> List[Product]:
        """Get bestseller products from a category URL."""
        products = []

        try:
            logger.info(f"Fetching bestsellers from {category_url}")

            # Navigate to the category page
            self.driver.get(category_url.strip())
            self._random_sleep(3, 5)

            # Take screenshot for debugging
            self.driver.save_screenshot(
                str(ERROR_LOG_PATH).replace(
                    ".log", f"_category_{category_url.split('/')[-2]}.png"
                )
            )

            # Scroll to load more products with human-like behavior
            for _ in range(3):
                self.driver.execute_script(
                    f"window.scrollBy(0, {random.randint(300, 700)});"
                )
                self._random_sleep(0.5, 2)

            # Look for product elements with different possible selectors
            product_name_selectors = [
                (By.CLASS_NAME, "_cDEzb_p13n-sc-css-line-clamp-3_g3dy1"),
                (By.CSS_SELECTOR, ".a-link-normal .a-size-base"),
                (By.CSS_SELECTOR, "[id^='p13n-asin-index'] .p13n-sc-truncate"),
                (By.XPATH, "//div[contains(@class, 'p13n-sc-truncate')]"),
                (
                    By.CSS_SELECTOR,
                    ".zg-grid-general-faceout .p13n-sc-truncate-desktop-type2",
                ),
                (By.CSS_SELECTOR, ".zg-item-immersion .a-text-normal"),
                (By.CSS_SELECTOR, ".p13n-sc-truncate-desktop-type2"),
                (By.CSS_SELECTOR, ".p13n-sc-truncate"),
            ]

            product_price_selectors = [
                (By.CLASS_NAME, "_cDEzb_p13n-sc-price_3mJ9Z"),
                (By.CSS_SELECTOR, ".a-price-whole"),
                (By.CSS_SELECTOR, ".p13n-sc-price"),
                (By.CSS_SELECTOR, ".a-color-price"),
                (By.XPATH, "//span[contains(@class, 'p13n-sc-price')]"),
                (By.CSS_SELECTOR, ".zg-item-immersion .a-color-price"),
                (By.CSS_SELECTOR, ".a-price .a-offscreen"),
            ]

            product_link_selectors = [
                (By.CSS_SELECTOR, "a.a-link-normal.aok-block"),
                (By.CSS_SELECTOR, "a.a-link-normal"),
                (By.CSS_SELECTOR, ".zg-item-immersion a"),
                (By.CSS_SELECTOR, ".a-link-normal[title]"),
                (
                    By.XPATH,
                    "//a[contains(@class, 'a-link-normal') and contains(@href, '/dp/')]",
                ),
            ]

            # Try each selector for product names
            product_names = []
            for by, selector in product_name_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    if elements:
                        product_names = [
                            element.text.strip()
                            for element in elements
                            if element.text.strip()
                        ]
                        logger.info(
                            f"Found {len(product_names)} product names using {by}: {selector}"
                        )
                        break
                except (NoSuchElementException, StaleElementReferenceException):
                    continue

            # Try each selector for product prices
            product_prices = []
            for by, selector in product_price_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    if elements:
                        price_texts = [
                            element.text.strip()
                            for element in elements
                            if element.text.strip()
                        ]
                        product_prices = []
                        for price_text in price_texts:
                            try:
                                # Try to extract price with various formats
                                price_match = re.search(r"R\$\s*([\d.,]+)", price_text)
                                if price_match:
                                    price_str = (
                                        price_match.group(1)
                                        .replace(".", "")
                                        .replace(",", ".")
                                    )
                                    product_prices.append(float(price_str))
                            except (ValueError, AttributeError):
                                continue
                        if product_prices:
                            logger.info(
                                f"Found {len(product_prices)} product prices using {by}: {selector}"
                            )
                            break
                except (NoSuchElementException, StaleElementReferenceException):
                    continue

            # Try each selector for product URLs
            product_urls = []
            for by, selector in product_link_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    if elements:
                        product_urls = [
                            element.get_attribute("href")
                            for element in elements
                            if element.get_attribute("href")
                            and "dp/" in element.get_attribute("href")
                        ]
                        logger.info(
                            f"Found {len(product_urls)} product URLs using {by}: {selector}"
                        )
                        break
                except (NoSuchElementException, StaleElementReferenceException):
                    continue

            # Log what we found for debugging
            logger.info(f"Product names count: {len(product_names)}")
            logger.info(f"Product prices count: {len(product_prices)}")
            logger.info(f"Product URLs count: {len(product_urls)}")

            # Create Product objects from the smallest list length to avoid index errors
            max_products = min(
                len(product_names), len(product_prices), len(product_urls)
            )
            for i in range(max_products):
                products.append(
                    Product(
                        name=product_names[i],
                        url=product_urls[i],
                        price=product_prices[i],
                    )
                )

            logger.info(f"Successfully created {len(products)} product objects")
            return products

        except WebDriverException as e:
            logger.error(
                f"WebDriver error scraping bestsellers from {category_url}: {str(e)}"
            )
            # Take screenshot for debugging
            try:
                self.driver.save_screenshot(
                    str(ERROR_LOG_PATH).replace(
                        ".log", f"_error_category_{category_url.split('/')[-2]}.png"
                    )
                )
            except:
                pass
            return []
        except Exception as e:
            logger.error(f"Error scraping bestsellers from {category_url}: {str(e)}")
            try:
                self.driver.save_screenshot(
                    str(ERROR_LOG_PATH).replace(
                        ".log", f"_error_category_{category_url.split('/')[-2]}.png"
                    )
                )
            except:
                pass
            return []

    def get_product_details(self, url: str) -> Optional[Product]:
        """Get detailed product information from a product URL."""
        try:
            logger.info(f"Fetching product details from {url}")
            self.driver.get(url)
            self._random_sleep(2, 4)

            html_body = self.driver.page_source
            soup = BeautifulSoup(html_body, "html.parser")

            # Try multiple selectors for the price
            price = None
            price_selectors = [
                "span.a-offscreen",
                "span.a-price span.a-offscreen",
                "#price_inside_buybox",
                "#priceblock_ourprice",
                ".a-price .a-offscreen",
            ]

            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.text.strip()
                    price_match = re.search(r"R\$\s*([\d.,]+)", price_text)
                    if price_match:
                        price_str = (
                            price_match.group(1).replace(".", "").replace(",", ".")
                        )
                        try:
                            price = float(price_str)
                            break
                        except ValueError:
                            continue

            # Try multiple selectors for the product name
            name = None
            name_selectors = [
                "#productTitle",
                ".product-title-word-break",
                ".a-size-large.product-title-word-break",
            ]

            for selector in name_selectors:
                name_element = soup.select_one(selector)
                if name_element:
                    name = name_element.text.strip()
                    break

            if name and price:
                return Product(name=name, url=url, price=price)
            else:
                logger.warning(
                    f"Could not extract complete product information from {url}"
                )
                return None

        except Exception as e:
            logger.error(f"Error getting product details from {url}: {str(e)}")
            return None
