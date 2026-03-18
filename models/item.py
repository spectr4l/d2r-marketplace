from dataclasses import dataclass
from typing import Optional


@dataclass
class Item:
    id: str
    name: str
    item_type: str
    quality: str
    attributes: str
    source: str
    status: str = "available"
    exported_from: Optional[str] = None