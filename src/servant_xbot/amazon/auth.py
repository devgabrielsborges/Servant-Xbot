import pickle
import logging
import time
import random
from typing import Optional
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located,
    element_to_be_clickable,
)
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.settings import AMAZON_EMAIL, AMAZON_PASSWORD, COOKIES_PATH, ERROR_LOG_PATH
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
handler = logging.FileHandler(ERROR_LOG_PATH)
logger.addHandler(handler)


class AmazonAuthenticator:
    """Handles Amazon authentication and cookie management."""

    def __init__(self, driver: uc.Chrome, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def _human_like_typing(self, element, text):
        """Type text in a human-like way with random delays."""
        if text is None:
            logger.error("Cannot type None text")
            return

        # Clear the field first
        element.clear()

        # Type each character with a random delay
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))

        # Small pause after finishing typing
        time.sleep(random.uniform(0.2, 0.5))

    def _random_sleep(self, min_sec=1, max_sec=3):
        """Sleep for a random time between min_sec and max_sec."""
        time.sleep(random.uniform(min_sec, max_sec))

    def login(self) -> bool:
        """Log into Amazon account and save cookies.

        Returns:
            bool: True if login was successful, False otherwise
        """
        try:
            logger.info("Starting Amazon login process")

            # Check if we have valid credentials
            if not AMAZON_EMAIL:
                logger.error("AMAZON_EMAIL environment variable is not set")
                return False

            if not AMAZON_PASSWORD:
                logger.error("AMAZON_PASSWORD environment variable is not set")
                return False

            # Navigate directly to the login page
            self.driver.get(
                "https://www.amazon.com.br/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com.br%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=brflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
            )
            self._random_sleep(2, 4)

            # Take screenshot of the login page for debugging
            self.driver.save_screenshot(
                str(ERROR_LOG_PATH).replace(".log", "_login_page.png")
            )
            logger.info("Saved login page screenshot")

            # Look for email field - try different selectors
            email_selectors = [
                (By.ID, "ap_email"),
                (By.NAME, "email"),
                (By.CSS_SELECTOR, "input[type='email']"),
            ]

            email_input = None
            for by, selector in email_selectors:
                try:
                    logger.info(f"Trying to find email field with {by}: {selector}")
                    self.wait.until(presence_of_element_located((by, selector)))
                    email_input = self.driver.find_element(by, selector)
                    logger.info(f"Found email field: {by}: {selector}")
                    break
                except (TimeoutException, NoSuchElementException):
                    continue

            if not email_input:
                logger.error("Could not find email input field")
                self.driver.save_screenshot(
                    str(ERROR_LOG_PATH).replace(".log", "_login_error.png")
                )
                return False

            # Enter email in a human-like way
            self._human_like_typing(email_input, AMAZON_EMAIL)
            self._random_sleep()

            # Try to find the continue button or press Enter
            continue_selectors = [
                (By.ID, "continue"),
                (By.ID, "continue-announce"),
                (By.ID, "continue-button"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//span[contains(text(), 'Continuar')]/.."),
            ]

            for by, selector in continue_selectors:
                try:
                    logger.info(f"Trying to find continue button with {by}: {selector}")
                    continue_button = self.wait.until(
                        element_to_be_clickable((by, selector))
                    )
                    self._random_sleep()
                    continue_button.click()
                    logger.info(f"Clicked continue button using {by}: {selector}")
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
            else:
                # If button not found, try pressing Enter
                email_input.send_keys(Keys.RETURN)
                logger.info("Pressed Enter to continue")

            self._random_sleep(2, 4)

            # Take screenshot of password page for debugging
            self.driver.save_screenshot(
                str(ERROR_LOG_PATH).replace(".log", "_password_page.png")
            )

            # Look for password field
            password_selectors = [
                (By.ID, "ap_password"),
                (By.NAME, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
            ]

            password_input = None
            for by, selector in password_selectors:
                try:
                    logger.info(f"Trying to find password field with {by}: {selector}")
                    self.wait.until(presence_of_element_located((by, selector)))
                    password_input = self.driver.find_element(by, selector)
                    break
                except (TimeoutException, NoSuchElementException):
                    continue

            if not password_input:
                logger.error("Could not find password input field")
                self.driver.save_screenshot(
                    str(ERROR_LOG_PATH).replace(".log", "_password_error.png")
                )
                return False

            # Enter password in a human-like way
            self._human_like_typing(password_input, AMAZON_PASSWORD)
            self._random_sleep()

            # Try to submit the form
            signin_selectors = [
                (By.ID, "signInSubmit"),
                (By.ID, "auth-signin-button"),
                (By.NAME, "signIn"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//span[contains(text(), 'Fazer login')]/.."),
                (By.XPATH, "//button[contains(text(), 'Entrar')]"),
            ]

            for by, selector in signin_selectors:
                try:
                    logger.info(f"Trying to find signin button with {by}: {selector}")
                    signin_button = self.wait.until(
                        element_to_be_clickable((by, selector))
                    )
                    self._random_sleep()
                    signin_button.click()
                    logger.info(f"Clicked signin button using {by}: {selector}")
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
            else:
                # If button not found, try pressing Enter
                password_input.send_keys(Keys.RETURN)
                logger.info("Pressed Enter to sign in")

            # Wait for login to complete - longer timeout here
            self._random_sleep(5, 10)

            # Take screenshot after login attempt
            self.driver.save_screenshot(
                str(ERROR_LOG_PATH).replace(".log", "_after_login.png")
            )

            # Check for successful login by looking for account indicators
            success_indicators = [
                (By.ID, "nav-link-accountList"),
                (By.ID, "nav-link-accountList-nav-line-1"),
                (By.XPATH, "//span[contains(text(), 'Olá,')]"),
                (By.XPATH, "//a[contains(@href, 'account')]"),
                (By.CSS_SELECTOR, "#navbar-main"),
            ]

            for by, selector in success_indicators:
                try:
                    self.wait.until(presence_of_element_located((by, selector)))
                    logger.info(f"Login verified by presence of {by}: {selector}")

                    # Save cookies
                    self._save_cookies()
                    return True
                except (TimeoutException, NoSuchElementException):
                    continue

            logger.error("Login verification failed")
            self.driver.save_screenshot(
                str(ERROR_LOG_PATH).replace(".log", "_verification_error.png")
            )
            return False

        except Exception as e:
            logger.error(f"Error during login process: {str(e)}")
            self.driver.save_screenshot(
                str(ERROR_LOG_PATH).replace(".log", "_exception_error.png")
            )
            return False

    def _save_cookies(self) -> None:
        """Save browser cookies to file."""
        try:
            with open(COOKIES_PATH, "wb") as file:
                pickle.dump(self.driver.get_cookies(), file)
            logger.info(f"Cookies saved to {COOKIES_PATH}")
        except Exception as e:
            logger.error(f"Error saving cookies: {str(e)}")

    def load_cookies(self) -> bool:
        """Load cookies from file and add them to the driver.

        Returns:
            bool: True if cookies were loaded successfully, False otherwise
        """
        # First visit the domain
        self.driver.get("https://www.amazon.com.br/")
        self._random_sleep(2, 4)

        try:
            with open(COOKIES_PATH, "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        logger.warning(f"Could not add cookie: {str(e)}")

            # Refresh page after loading cookies
            self.driver.refresh()
            self._random_sleep(2, 4)

            # Verify cookies worked by checking for login state
            for by, selector in [
                (By.ID, "nav-link-accountList"),
                (By.XPATH, "//span[contains(text(), 'Olá,')]"),
            ]:
                try:
                    self.wait.until(presence_of_element_located((by, selector)))
                    logger.info("Cookies loaded and logged in successfully")
                    return True
                except (TimeoutException, NoSuchElementException):
                    continue

            logger.warning("Cookies loaded but login state not verified")
            return False
        except (FileNotFoundError, EOFError) as e:
            logger.warning(f"Could not load cookies: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error loading cookies: {str(e)}")
            return False
