from app.database import Base

import uuid
from decimal import Decimal

from sqlalchemy import Numeric, String, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Currency(Base):
    __tablename__ = "currency"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    ticker: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    prices: Mapped[list["IndexPrice"]] = relationship(
        back_populates="currency",
    )


class IndexPrice(Base):
    __tablename__ = "index_price"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    currency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("currency.id"),
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    timestamp: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    currency: Mapped["Currency"] = relationship(
        back_populates="prices",
    )