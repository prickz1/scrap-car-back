from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func
from app.core.database import Base


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Dados do veículo
    marca: Mapped[str] = mapped_column(String(100), index=True)
    modelo: Mapped[str] = mapped_column(String(100), index=True)
    ano: Mapped[int]
    quilometragem: Mapped[Optional[int]] = mapped_column(nullable=True)
    preco: Mapped[float]
    combustivel: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cambio: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cor: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Localização
    cidade: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)

    # Fonte
    loja: Mapped[str] = mapped_column(String(100))
    url_anuncio: Mapped[str] = mapped_column(String(500), unique=True)

    # Metadados
    coletado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())