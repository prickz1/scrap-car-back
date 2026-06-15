from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.car import Car
from app.schemas.car import CarCreate, CarRead

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/cars", response_model=list[CarRead])
async def listar_carros(db: AsyncSession = Depends(get_db)):
    resultado = await db.execute(select(Car))
    return resultado.scalars().all()


@router.get("/cars/{id}", response_model=CarRead)
async def buscar_por_id(id: int, db: AsyncSession = Depends(get_db)):
    resultado = await db.execute(select(Car).where(Car.id == id))
    carro = resultado.scalar_one_or_none()

    if not carro:
        raise HTTPException(status_code=404, detail="Carro não encontrado")

    return carro


@router.post("/cars", response_model=CarRead, status_code=201)
async def criar_carro(carro: CarCreate, db: AsyncSession = Depends(get_db)):
    novo_carro = Car(**carro.model_dump())
    db.add(novo_carro)
    await db.commit()
    await db.refresh(novo_carro)
    return novo_carro
