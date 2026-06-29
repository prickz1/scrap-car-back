from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CarBase(BaseModel):
    titulo: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    ano: Optional[int] = None
    quilometragem: Optional[int] = None
    preco: float
    combustivel: Optional[str] = None
    cambio: Optional[str] = None
    cor: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    loja: str
    url_anuncio: str


class CarCreate(CarBase):
    pass


class CarRead(CarBase):
    id: int
    coletado_em: datetime
    criado_em: datetime

    model_config = {"from_attributes": True}
