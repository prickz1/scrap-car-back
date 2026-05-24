from datetime import datetime
from pydantic import BaseModel


class CarBase(BaseModel):
    title: str
    price: float
    source_url: str


class CarCreate(CarBase):
    pass


class CarRead(CarBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
