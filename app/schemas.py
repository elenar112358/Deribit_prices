from decimal import Decimal

from pydantic import BaseModel, Field


class PricesResponse(BaseModel):
    currency: str = Field(max_length=20)
    price: Decimal
    timestamp: int


class PricesLineResponse(BaseModel):
    currency: str = Field(max_length=20)
    prices: list[Decimal]
    timestamps: list[int]
