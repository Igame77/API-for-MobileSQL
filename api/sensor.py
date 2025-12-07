from fastapi import APIRouter
from fastapi.responses import  StreamingResponse
from models import SensorSchema, sensor
from sqlalchemy import insert, text
from sqlalchemy.ext.asyncio import AsyncEngine
from api.getterImages import get_image_from_table
class SensorsManager:
    def __init__(self, async_engine: AsyncEngine, router: APIRouter):
        self.async_engine = async_engine
        self.router = router
        self.tags = ['sensors']

    def setup(self):
        @self.router.get('/tables/sensors/get_data/{isImage}', tags=self.tags)
        async def get_sensors_data(isImage : bool = False):
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('select * from `sensor` limit 0,500'))).all()
            return get_image_from_table(res, isImage)

        @self.router.get('/tables/sensors/get_headers', tags=self.tags)
        async def get_sensors_headers():
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('show columns from `sensor`'))).all()
                res = [[el[0], el[1]] for el in res]
            return res

        @self.router.get('/tables/sensors/get_data_by_element/{name_elem}/{value_elem}/{isImage}', tags=self.tags)
        async def get_sensor_by_elem(name_elem: str, value_elem: str | float | int, isImage : bool):
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text(f'select * from `sensor` where {name_elem}={value_elem}'))).all()
            return get_image_from_table(res, isImage)

        @self.router.post('/tables/sensors/send_data', tags=self.tags)
        async def send_sensor_data(sensor_data: SensorSchema):
            async with self.async_engine.connect() as conn:
                user_dev_id = (await conn.execute(text('select * from `user_dev` order by id desc limit 1'))).first()[0]

                stmt = insert(sensor).values([{
                    'accuracy': sensor_data.accuracy,
                    'date': sensor_data.date,
                    'user_dev_id': user_dev_id
                }])
                await conn.execute(stmt)
                await conn.commit()
            return {'isSuccess': True, 'code': 200}

        @self.router.delete('/tables/sensors/delete_by_element/{name_elem}/{value_elem}', tags=self.tags)
        async def delete_sensor_by_elem(name_elem: str, value_elem: str | int | float):
            res = (await get_sensor_by_elem(name_elem, value_elem))
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                await conn.execute(text(f'delete from `sensor` where {name_elem}={value_elem}'))
                await conn.commit()
            return res
