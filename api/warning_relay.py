from fastapi import APIRouter
from models import SchemaRelay, warning_relay
from sqlalchemy import text, insert
from sqlalchemy.ext.asyncio import AsyncEngine
from api.getterImages import get_image_from_table

class RelayManager:
    def __init__(self, engine: AsyncEngine, router: APIRouter):
        self.async_engine = engine
        self.router = router
        self.tags = ['relay']

    def setup(self):
        @self.router.get('/tables/relay/get_data/{isImage}', tags=self.tags)
        async def get_relay_data(isImage:bool):
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('select * from `Warning relay` limit 0,500'))).all()
            return get_image_from_table(res, isImage)

        @self.router.get('/tables/relay/get_headers', tags=self.tags)
        async def get_valve_headers():
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text("SHOW COLUMNS FROM `Warning relay`"))).all()
                res = [[el[0], el[1]] for el in res]
            return res

        @self.router.get('/tables/relay/get_rows_by_element/{name_elem}/{value_elem}/{isImage}', tags=self.tags)
        async def get_valve_by_elem(name_elem: str, value_elem: int | float | str, isImage:bool):
            async with self.async_engine.connect() as conn:
                res = (
                    await conn.execute(text(f'SELECT * FROM `Warning relay` WHERE {name_elem} = {value_elem}'))).all()
            return get_image_from_table(res, isImage)

        @self.router.post('/tables/relay/send_data', tags=self.tags)
        async def post_valve_data(relay_data: SchemaRelay):
            async with self.async_engine.connect() as conn:
                stmt = insert(warning_relay).values([{
                    'maxDust': relay_data.maxDust,
                    'maxConcentration': relay_data.maxConcentration
                }])
                await conn.execute(stmt)
                await conn.commit()
            return {'success': True, 'code': 200}

        @self.router.delete('/tables/relay/delete_by_element/{name_elem}/{value_elem}', tags=self.tags)
        async def delete_valve_by_elem(name_elem: str, value_elem: float | int | str):
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                res = (
                    await conn.execute(text(f'SELECT * FROM `Warning relay` WHERE {name_elem} = {value_elem}'))).first()
                await conn.execute(text(f'DELETE FROM `Warning valve` WHERE {name_elem} = {value_elem}'))
                await conn.commit()
            return list(res)
