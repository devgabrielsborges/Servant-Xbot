import logging
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options


def setup_chrome_driver(headless: bool = False) -> uc.Chrome:
    """Set up and return a configured Chrome driver.

    Args:
        headless (bool): Whether to run Chrome in headless mode

    Returns:
        uc.Chrome: Configured Chrome driver
    """
    options = uc.ChromeOptions()

    if headless:
        options.headless = True
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    return uc.Chrome(options=options)


def extract_price_from_text(text: str) -> Optional[float]:
    """Extract price value from text containing Brazilian currency format.

    Args:
        text (str): Text containing price in format R$ XX,XX

    Returns:
        Optional[float]: Extracted price as float or None if extraction fails
    """
    try:
        if not text:
            return None

        price_match = re.search(r"R\$\s*([\d.,]+)", text)
        if not price_match:
            return None

        price_str = price_match.group(1).replace(".", "").replace(",", ".")
        return float(price_str)
    except Exception:
        return None


def create_directory_if_not_exists(directory_path: str) -> None:
    """Create directory if it doesn't exist.

    Args:
        directory_path (str): Directory path
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def format_brazilian_date(dt: datetime = None) -> str:
    """Format datetime in Brazilian format.

    Args:
        dt (datetime, optional): Datetime to format. Defaults to current time.

    Returns:
        str: Formatted date string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%d/%m/%Y %H:%M:%S")


def clean_product_name(name: str) -> str:
    """Clean up a product name by removing extra whitespace and standardizing case.

    Args:
        name (str): Raw product name

    Returns:
        str: Cleaned product name
    """
    if not name:
        return ""

    # Remove excessive whitespace
    cleaned = re.sub(r"\s+", " ", name.strip())

    # Capitalize first letter of each word for main words
    words = cleaned.split()
    if len(words) > 0:
        words[0] = words[0].capitalize()

    return " ".join(words)


def is_amazon_affiliate_link(url: str) -> bool:
    """Check if a URL is an Amazon affiliate link.

    Args:
        url (str): URL to check

    Returns:
        bool: True if the URL is an Amazon affiliate link
    """
    return bool(url and ("amzn.to" in url.lower() or "amazon" in url.lower()))
