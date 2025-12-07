from fastapi import APIRouter
from models import ore, OreSchema
from sqlalchemy import text, insert
from sqlalchemy.ext.asyncio import AsyncEngine
from api.getterImages import get_image_from_table

class OreManager:
    def __init__(self, engine: AsyncEngine, router: APIRouter):
        self.async_engine = engine
        self.router = router
        self.tags = ['Ore']

    def setup(self):
        @self.router.get('/tables/ore/get_data/{isImage}', tags=self.tags)
        async def get_ore_data(isImage:bool):
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('select * from `Ore` limit 0,500'))).all()
            return get_image_from_table(res, isImage)

        @self.router.get('/tables/ore/get_headers', tags=self.tags)
        async def get_ore_headers():
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('show columns from `Ore`'))).all()
                res = [[el[0], el[1]] for el in res]
            return res

        @self.router.get('/tables/ore/get_by_element/{name_elem}/{value_elem}/{isImage}', tags=self.tags)
        async def get_ore_by_elem(name_elem: str, value_elem: int | float | str, isImage:bool):
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text(f'select * from `Ore` where {name_elem}={value_elem}'))).all()
            return get_image_from_table(res, isImage)

        @self.router.post('/tables/ore/send_data', tags=self.tags)
        async def post_ore_data(ore_data: OreSchema):
            async with self.async_engine.connect() as conn:
                stmt = insert(ore).values([{
                    'weight': ore_data.weight,
                    'content': ore_data.content,
                    'waste': ore_data.waste,
                    'Production_unit_id': ore_data.production_unit_id
                }])
                await conn.execute(stmt)
                await conn.commit()
            return {'isSuccess': True, 'code': 200}

        @self.router.delete('/tables/ore/delete_by_element/{name_elem}/{value_elem}', tags=self.tags)
        async def delete_ore_by_elem(name_elem: str, value_elem: str | int | float):
            res = (await get_ore_by_elem(name_elem, value_elem))
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                await conn.execute(text(f'delete from `Ore` where {name_elem}={value_elem}'))
                await conn.commit()
            return res