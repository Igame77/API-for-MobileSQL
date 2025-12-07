from fastapi import APIRouter
from models import CiclonSchema, ciclon
from sqlalchemy import text, insert
from sqlalchemy.ext.asyncio import AsyncEngine
from api.getterImages import get_image_from_table

class CiclonManager:
    def __init__(self, engine: AsyncEngine, router: APIRouter):
        self.async_engine = engine
        self.router = router
        self.tags = ['Ciclon']

    def setup(self):
        @self.router.get('/tables/ciclon/get_data/{isImage}', tags=self.tags)
        async def get_ciclon_data(isImage:bool):
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('select * from `Ciclon` limit 0,500'))).all()
            return get_image_from_table(res, isImage)

        @self.router.get('/tables/ciclon/get_headers', tags=self.tags)
        async def get_ciclon_header():
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('show columns from `Ciclon`'))).all()
                res = [[el[0], el[1]] for el in res]
            return res

        @self.router.get('/tables/ciclon/get_data_by_element/{name_elem}/{value_elem}/{isImage}', tags=self.tags)
        async def get_ciclon_by_elem(name_elem: str, value_elem: str | float | int, isImage:bool):
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text(f'selec * from `Ciclon` where {name_elem}={value_elem}'))).all()
            return get_image_from_table(res, isImage)

        @self.router.post('/tables/ciclon/send_data', tags=self.tags)
        async def send_ciclon_data(ciclon_data: CiclonSchema):
            async with self.async_engine.connect() as conn:
                stmt = insert(ciclon).values([{
                    'Pressure': ciclon_data.pressure,
                    'Concentration': ciclon_data.concentration
                }])
                await conn.execute(stmt)
                await conn.commit()
            return {'isSuccess': True, 'code': 200}

        @self.router.delete('/tables/ciclon/delete_by_element/{name_elem}/{value_elem}', tags=self.tags)
        async def delete_ciclon_by_elem(name_elem: str, value_elem: str | int | float):
            res = (await get_ciclon_by_elem(name_elem, value_elem))
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                await conn.execute(text(f'delete from `Ciclon` where {name_elem}={value_elem}'))
                await conn.commit()
            return res