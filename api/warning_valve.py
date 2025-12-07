from fastapi import APIRouter
from models import ValveSchema, warning_valve
from sqlalchemy import text, insert
from sqlalchemy.ext.asyncio import AsyncEngine
from api.getterImages import get_image_from_table


class ValveManager:

    def __init__(self, engine: AsyncEngine, router: APIRouter):
        self.async_engine: AsyncEngine = engine
        self.router = router

    def setup(self):
        @self.router.get('/tables/valve/get_data/{isImage}', tags=['valve🔧'])
        async def get_valve_data(isImage:bool):
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text("SELECT * FROM `Warning valve` LIMIT 0, 500"))).all()
            return get_image_from_table(res, isImage)

        @self.router.get('/tables/valve/get_headers', tags=['valve🔧'])
        async def get_valve_headers():
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text("SHOW COLUMNS FROM `Warning valve`"))).all()
                res = [[el[0], el[1]] for el in res]
            return res

        @self.router.get('/tables/valve/get_rows_by_element/{name_elem}/{value_elem}/{isImage}', tags=['valve🔧'])
        async def get_valve_by_elem(name_elem: str, value_elem: int | float | str, isImage:bool):
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text(f'SELECT * FROM `Warning valve` WHERE {name_elem} = {value_elem}'))).all()
            return get_image_from_table(res, isImage)

        @self.router.post('/tables/valve/send_data', tags=['valve🔧'])
        async def post_valve_data(valve_data: ValveSchema):
            async with self.async_engine.connect() as conn:
                stmt = insert(warning_valve).values([{
                    'Power': valve_data.power,
                    'maxPressure': valve_data.maxPressure,
                    'maxTemp': valve_data.maxTemp
                }])
                print(stmt)
                await conn.execute(stmt)
                await conn.commit()
            return {'success': True, 'code': 200}

        @self.router.delete('/tables/valve/delete_by_element/{name_elem}/{value_elem}', tags=['valve🔧'])
        async def delete_valve_by_elem(name_elem: str, value_elem: float | int | str):
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text(f'SELECT * FROM `Warning valve` WHERE {name_elem} = {value_elem}'))).first()
                await conn.execute(text(f'DELETE FROM `Warning valve` WHERE {name_elem} = {value_elem}'))
                await conn.commit()
            return list(res)