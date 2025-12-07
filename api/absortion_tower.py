from fastapi import APIRouter
from models import absortion_tower, AbsortionSchema
from sqlalchemy import insert, text
from sqlalchemy.ext.asyncio import AsyncEngine
from api.getterImages import get_image_from_table

class AbsortManager:
    def __init__(self, engine: AsyncEngine, router: APIRouter):
        self.async_engine = engine
        self.router = router
        self.tags = ['Absort tower']

    def setup(self):
        @self.router.get('/tables/absort_tower/get_data/{isImage}', tags=self.tags)
        async def get_absort_data(isImage : bool):
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('select * from `absortion tower` limit 0,500'))).all()
            return get_image_from_table(res, isImage)

        @self.router.get('/tables/absort_tower/get_headers', tags=self.tags)
        async def get_absort_header():
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('show columns from `absortion tower`'))).all()
                res = [[el[0], el[1]] for el in res]
            return res

        @self.router.get('/tables/absort_tower/get_data_by_element/{name_elem}/{value_elem}/{isImage}', tags=self.tags)
        async def get_absort_by_elem(name_elem: str, value_elem: str | float | int, isImage:bool):
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text(f'selec * from `absortion tower` where {name_elem}={value_elem}'))).all()
            return get_image_from_table(res, isImage)

        @self.router.post('/tables/absort_tower/send_data', tags=self.tags)
        async def send_absort_data(absort_data: AbsortionSchema):
            async with self.async_engine.connect() as conn:
                stmt = insert(absortion_tower).values([{
                    'accuracy': absort_data.accuracy
                }])
                await conn.execute(stmt)
                await conn.commit()
            return {'isSuccess': True, 'code': 200}

        @self.router.delete('/tables/absort_tower/delete_by_element/{name_elem}/{value_elem}', tags=self.tags)
        async def delete_absort_by_elem(name_elem: str, value_elem: str | int | float):
            res = (await get_absort_by_elem(name_elem, value_elem))
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                await conn.execute(text(f'delete from `absortion tower` where {name_elem}={value_elem}'))
                await conn.commit()
            return res