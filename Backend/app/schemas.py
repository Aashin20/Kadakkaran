from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    sku: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: float = Field(ge=0)
    cost: float = Field(default=0, ge=0)
    initial_stock: int = Field(default=0, ge=0)
    unit: str = Field(default="കിലോ", max_length=50)
    minimum_stock: int = Field(default=5, ge=0)
    expiry_days: Optional[int] = Field(default=None, ge=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    sku: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: Optional[float] = Field(default=None, ge=0)
    cost: Optional[float] = Field(default=None, ge=0)
    unit: Optional[str] = Field(default=None, max_length=50)
    minimum_stock: Optional[int] = Field(default=None, ge=0)
    expiry_days: Optional[int] = Field(default=None, ge=0)


class StockChange(BaseModel):
    quantity: int = Field(gt=0)
    note: Optional[str] = Field(default=None, max_length=500)


class CreditCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    amount: float = Field(gt=0)
    pay_at: datetime


class CreditUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    amount: Optional[float] = Field(default=None, gt=0)
    pay_at: Optional[datetime] = None


class AIChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class BillItem(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class BillCreate(BaseModel):
    items: list[BillItem] = Field(min_length=1)
    discount: float = Field(default=0, ge=0)
    generate_pdf: bool = False
