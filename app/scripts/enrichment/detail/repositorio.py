from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.models.car import Car

BATCH_SIZE = 50


async def buscar_para_enriquecer(min_id: int = 0) -> list[Car]:
    """Retorna próximo lote com marca IS NULL a partir de min_id, em ordem crescente."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Car)
            .where(Car.marca.is_(None))
            .where(Car.id > min_id)
            .order_by(Car.id.asc())
            .limit(BATCH_SIZE)
        )
        return result.scalars().all()


async def atualizar_detalhes(registros: list[tuple[int, dict]]) -> int:
    if not registros:
        return 0
    async with AsyncSessionLocal() as session:
        for car_id, valores in registros:
            await session.execute(
                update(Car).where(Car.id == car_id).values(**valores)
            )
        await session.commit()
    return len(registros)
