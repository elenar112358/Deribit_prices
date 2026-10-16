from datetime import date

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.schemas import PricesResponse, PricesLineResponse
from app.service import price_service

router = APIRouter()


@router.get(
    "/prices/",
    response_model=PricesLineResponse,
    summary="Получение всех сохраненных данных по указанной валюте"
)
def get_prices(
        currency: str = Query(max_length=20),
        db: Session = Depends(get_db)
):
    return price_service.get_prices(db, currency)


@router.get(
    "/last_price/",
    response_model=PricesResponse,
    summary="Получение последней цены валюты"
)
def get_last_price(
        currency: str = Query(max_length=20),
        db: Session = Depends(get_db)
):
    result = price_service.get_last_price(db, currency)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No prices found for currency '{currency}'",
        )

    return result


@router.get(
    "/date_prices/",
    response_model=list[PricesResponse],
    summary="Получение цены валюты с фильтром по дате"
)
def get_date_prices(
        target_date: date,
        currency: str = Query(max_length=20),
        db: Session = Depends(get_db),
):
    return price_service.get_date_prices(db, target_date, currency)
