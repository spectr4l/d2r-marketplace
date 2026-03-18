from dataclasses import dataclass
from typing import Optional


@dataclass
class Transaction:
    type: str
    item_id: Optional[str]
    token_amount: int
    description: str