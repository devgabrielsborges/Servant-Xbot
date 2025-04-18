from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    """Represents an Amazon product."""

    name: str
    url: str
    price: float
    affiliate_url: Optional[str] = None
    last_price: Optional[float] = None
    updated_at: Optional[datetime] = None

    def to_dict(self):
        """Convert to dictionary for database storage."""
        result = {
            "Produto": self.name,
            "Link": self.url if not self.affiliate_url else self.affiliate_url,
            "Valor": self.price,
            "Ultimo_valor": self.last_price if self.last_price else self.price,
        }

        if self.updated_at:
            result["Data"] = self.updated_at.isoformat()

        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Create a Product instance from a dictionary."""
        return cls(
            name=data.get("Produto", ""),
            url=data.get("Link", ""),
            price=float(data.get("Valor", 0.0)),
            last_price=float(data.get("Ultimo_valor", 0.0)),
            updated_at=datetime.fromisoformat(data.get("Data"))
            if "Data" in data
            else None,
        )
