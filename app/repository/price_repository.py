import uuid

from decimal import Decimal
from sqlalchemy.orm import Session

from app.models import IndexPrice


def create_index_price(
    db: Session,
    currency_id: uuid.UUID,
    price: Decimal,
    timestamp: int,
) -> uuid.UUID:
    index_price = IndexPrice(
        currency_id=currency_id,
        price=price,
        timestamp=timestamp,
    )

    db.add(index_price)
    db.flush()

    return index_price.id