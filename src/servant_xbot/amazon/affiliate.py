import logging
import time
import random
from typing import Optional
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located,
    element_to_be_clickable,
)
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.settings import ERROR_LOG_PATH

logger = logging.getLogger(__name__)
handler = logging.FileHandler(ERROR_LOG_PATH)
logger.addHandler(handler)


class AffiliateGenerator:
    """Handles generating Amazon affiliate links."""

    def __init__(self, driver: uc.Chrome, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def _random_sleep(self, min_sec=1, max_sec=3):
        """Sleep for a random time between min_sec and max_sec."""
        time.sleep(random.uniform(min_sec, max_sec))

    def generate_affiliate_link(self, product_url: str) -> Optional[str]:
        """Generate an affiliate link for a product URL.

        Args:
            product_url (str): URL of the product page

        Returns:
            Optional[str]: Affiliate link or None if generation fails
        """
        try:
            logger.info(f"Generating affiliate link for {product_url}")

            # Navigate to the product page
            self.driver.get(product_url)
            self._random_sleep(2, 4)

            # Attempt to find the affiliate link button with multiple selectors
            affiliate_button_selectors = [
                (By.ID, "amzn-ss-get-link-button"),
                (By.CSS_SELECTOR, "#amzn-ss-get-link"),
                (By.XPATH, "//span[contains(text(), 'Obtenha o link')]"),
                (By.XPATH, "//span[contains(text(), 'Get link')]"),
                (By.CSS_SELECTOR, ".amzn-ss-wrap button"),
            ]

            # Try each selector
            for by, selector in affiliate_button_selectors:
                try:
                    logger.info(f"Looking for affiliate button with {by}: {selector}")
                    button = self.wait.until(element_to_be_clickable((by, selector)))
                    button.click()
                    logger.info(f"Clicked affiliate button using {by}: {selector}")
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
            else:
                logger.error("Could not find affiliate button")
                self.driver.save_screenshot(
                    str(ERROR_LOG_PATH).replace(
                        ".log",
                        f"_affiliate_button_error_{product_url.split('/')[-2]}.png",
                    )
                )
                return None

            self._random_sleep(1, 3)

            # Take screenshot
            self.driver.save_screenshot(
                str(ERROR_LOG_PATH).replace(
                    ".log", f"_after_affiliate_click_{product_url.split('/')[-2]}.png"
                )
            )

            # Try to find the text area with the generated link
            link_textarea_selectors = [
                (By.ID, "amzn-ss-text-shortlink-textarea"),
                (By.CSS_SELECTOR, ".amzn-ss-text-shortlink-textarea"),
                (By.CSS_SELECTOR, "textarea.a-text-center"),
                (By.XPATH, "//textarea[contains(@id, 'shortlink')]"),
            ]

            # Try each selector
            for by, selector in link_textarea_selectors:
                try:
                    logger.info(f"Looking for link textarea with {by}: {selector}")
                    textarea = self.wait.until(
                        presence_of_element_located((by, selector))
                    )
                    self._random_sleep(0.5, 1.5)
                    affiliate_link = textarea.text or textarea.get_attribute("value")

                    if affiliate_link:
                        logger.info(f"Found affiliate link: {affiliate_link}")
                        return affiliate_link
                except (TimeoutException, NoSuchElementException):
                    continue

            logger.error("Could not find affiliate link textarea")
            self.driver.save_screenshot(
                str(ERROR_LOG_PATH).replace(
                    ".log", f"_affiliate_link_error_{product_url.split('/')[-2]}.png"
                )
            )
            return None

        except Exception as e:
            logger.error(f"Error generating affiliate link for {product_url}: {str(e)}")
            return None
