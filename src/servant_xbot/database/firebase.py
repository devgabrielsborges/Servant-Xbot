import os
import logging
from typing import Dict, Any, Optional, List
import firebase_admin
from firebase_admin import db, credentials
from config.settings import (
    FIREBASE_CREDENTIALS_PATH,
    FIREBASE_DATABASE_URL,
    ERROR_LOG_PATH,
)
from ..models.product import Product


logger = logging.getLogger(__name__)
handler = logging.FileHandler(ERROR_LOG_PATH)
logger.addHandler(handler)


class FirebaseManager:
    """Manages Firebase database operations."""

    def __init__(self):
        """Initialize Firebase connection."""
        try:
            if not FIREBASE_CREDENTIALS_PATH.exists():
                logger.warning(
                    f"Firebase credentials file not found: {FIREBASE_CREDENTIALS_PATH}"
                )
                logger.warning("Running in test mode without Firebase")
                self.test_mode = True
                return

            cred = credentials.Certificate(str(FIREBASE_CREDENTIALS_PATH))
            if not firebase_admin._apps:
                firebase_admin.initialize_app(
                    cred, {"databaseURL": FIREBASE_DATABASE_URL}
                )
            self.test_mode = False
        except Exception as e:
            logger.error(f"Firebase initialization error: {str(e)}")
            logger.warning("Running in test mode without Firebase")
            self.test_mode = True

    def get_last_item_index(self) -> int:
        """Get the index of the last product item."""
        if self.test_mode:
            return 0

        try:
            return db.reference("/last_item").get() or 0
        except Exception as e:
            logger.error(f"Error getting last item index: {str(e)}")
            return 0

    def update_last_item_index(self, index: int) -> None:
        """Update the last item index."""
        if self.test_mode:
            return

        try:
            db.reference("/last_item").set(index)
        except Exception as e:
            logger.error(f"Error updating last item index: {str(e)}")

    def add_product(self, product: Product) -> int:
        """Add a product to the database."""
        if self.test_mode:
            logger.info(f"Test mode: Would add product {product.name}")
            return 0

        try:
            last_index = self.get_last_item_index()
            new_index = last_index + 1

            # Update product in database
            db.reference(f"/itens/{new_index}").update(product.to_dict())

            # Update last item index
            self.update_last_item_index(new_index)

            return new_index
        except Exception as e:
            logger.error(f"Error adding product: {str(e)}")
            return 0

    def update_product(self, index: int, product: Product) -> bool:
        """Update a product in the database."""
        try:
            db.reference(f"/items/{index}").update(product.to_dict())
            return True
        except Exception as e:
            logger.error(f"Error updating product at index {index}: {str(e)}")
            return False

    def get_product(self, index: int) -> Optional[Product]:
        """Get a product from the database."""
        try:
            product_data = db.reference(f"/items/{index}").get()
            if product_data:
                return Product.from_dict(product_data)
            return None
        except Exception as e:
            logger.error(f"Error getting product at index {index}: {str(e)}")
            return None

    def get_all_products(self) -> List[Product]:
        """Get all products from the database."""
        products = []
        try:
            last_index = self.get_last_item_index()
            for index in range(1, last_index + 1):
                product = self.get_product(index)
                if product:
                    products.append(product)
        except Exception as e:
            logger.error(f"Error getting all products: {str(e)}")
        return products
