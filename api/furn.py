from fastapi import APIRouter
from models import furn, FurnSchema
from sqlalchemy import text, insert
from sqlalchemy.ext.asyncio import AsyncEngine
from api.getterImages import get_image_from_table

class FurnManager:
    def __init__(self, engine: AsyncEngine, router: APIRouter):
        self.async_engine = engine
        self.router = router
        self.tags = ['furn']

    def setup(self):
        @self.router.get('/tables/furn/get_data/{isImage}', tags=self.tags)
        async def get_furn_data(isImage:bool):
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('select * from `Furn`'))).all()
            return get_image_from_table(res, isImage)

        @self.router.get('/tables/furn/get_headers', tags=self.tags)
        async def get_furn_headers():
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('show columns from `Furn'))).all()
                res = [[el[0], el[1]] for el in res]
            return res

        @self.router.get('/tables/furn/get_by_element/{name_elem}/{value_elem}/{isImage}', tags=self.tags)
        async def get_furn_by_elem(name_elem: str, value_elem: int | float | str, isImage:bool):
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text(f'select * from `Furn where {name_elem}={value_elem}'))).all()
            return get_image_from_table(res, isImage)

        @self.router.post('/tables/furn/send_data', tags=self.tags)
        async def post_furn_data(furn_data: FurnSchema):
            async with self.async_engine.connect() as conn:
                stmt = insert(furn).values([{
                    'loss': furn_data.loss,
                    'date_create': furn_data.date_create
                }])
                await conn.execute(stmt)
                await conn.commit()
            return {'isSuccess': True, 'code': 200}

        @self.router.delete('/tables/furn/delete_by_element/{name_elem}/{value_elem}', tags=self.tags)
        async def delete_furn_by_elem(name_elem: str, value_elem: str | int| float):
            res = (await get_furn_by_elem(name_elem, value_elem))
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                await conn.execute(text(f'delete from `Furn where {name_elem}={value_elem}'))
                await conn.commit()
            return res


