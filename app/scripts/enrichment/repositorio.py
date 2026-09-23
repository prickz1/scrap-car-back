from sqlalchemy import or_, select, update
from app.core.database import AsyncSessionLocal
from app.models.car import Car

BATCH_SIZE = 500


async def buscar_para_enriquecer() -> list[Car]:
    """Retorna um lote de carros que ainda possuem algum campo por enriquecer."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Car)
            .where(or_(Car.marca.is_(None), Car.modelo.is_(None), Car.ano.is_(None)))
            .order_by(Car.id)
            .limit(BATCH_SIZE)
        )
        return result.scalars().all()


async def atualizar_enriquecimento(registros: list[tuple[int, dict]]) -> int:
    """Recebe lista de (id, {campo: valor}) e aplica UPDATE em lote."""
    if not registros:
        return 0

    async with AsyncSessionLocal() as session:
        for car_id, valores in registros:
            await session.execute(
                update(Car).where(Car.id == car_id).values(**valores)
            )
        await session.commit()

    return len(registros)
