from sqlalchemy.exc import IntegrityError
from app.core.database import AsyncSessionLocal
from app.models.car import Car


async def salvar_anuncios(anuncios):
    salvos = 0
    duplicados = 0

    async with AsyncSessionLocal() as session:
        for anuncio in anuncios:
            carro = Car(
                titulo=anuncio["titulo"],
                preco=anuncio["preco"],
                cidade=anuncio["cidade"],
                quilometragem=anuncio["quilometragem"],
                loja="OLX",
                url_anuncio=anuncio["link"],
            )
            session.add(carro)
            try:
                await session.commit()
                salvos += 1
            except IntegrityError:
                await session.rollback()
                duplicados += 1

    return {"salvos": salvos, "duplicados": duplicados}
