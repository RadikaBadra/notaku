from pydantic import BaseModel, Field, field_validator
from typing import List
from datetime import datetime

class ReceiptItem(BaseModel):
  product_name: str
  qty: int
  price: float
  
class Receipt(BaseModel):
    merchant_name: str
    date: datetime
    total: int
    items: List[ReceiptItem]
    
class ReceiptCreate(Receipt):
  pass

class ReceiptInDB(Receipt):
  id: str = Field(..., alias="_id")
  user_id: str
  
  class Config:
    populate_by_name = True
