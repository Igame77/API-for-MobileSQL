from fastapi import APIRouter
from models import PressureSchema, detector_pressure, TempSchema, detector_temp, SO2Schema, detector_so2
from models import DustinessSchema, detector_dustiness
from models import type_pressure, type_dustiness
from models import type_temp, type_so2
from sqlalchemy import text, insert
from sqlalchemy.ext.asyncio import AsyncEngine
from api.getterImages import get_image_from_table

class DetectorsManager:
    def __init__(self, engine: AsyncEngine, router: APIRouter):
        self.async_engine = engine
        self.router = router
        self.tags = [['detector pressure'], ['detector dustiness'], ['detector temp'], ['detector so2']]

    def setup_pressure(self):
        @self.router.get('/tables/pressure_detector/get_data/{isImage}', tags=self.tags[0])
        async def get_pressure_data(isImage:bool):
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('select * from `Datchik davleniya` limit 0,500'))).all()
            return get_image_from_table(res, isImage)

        @self.router.get('/tables/pressure_detector/get_headers', tags=self.tags[0])
        async def get_pressure_headers():
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('show columns from `Datchik davleniya`'))).all()
                res = [[el[0], el[1]] for el in res]
            return res

        @self.router.get('/tables/pressure_detector/get_by_element/{name_elem}/{value_elem}/{isImage}', tags=self.tags[0])
        async def get_pressure_by_elem(name_elem: str, value_elem: int | float | str, isImage:bool):
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text(f'select * from `Datchik davleniya` where {name_elem}={value_elem}'))).all()
            return get_image_from_table(res, isImage)

        @self.router.post('/tables/pressure_detector/send_data', tags=self.tags[0])
        async def post_pressure_data(pressure_data: PressureSchema):
            async with self.async_engine.connect() as conn:
                stmt = insert(detector_pressure).values([{
                    'Pressure': pressure_data.pressure,
                    'maxLoss': pressure_data.maxLoss
                }])
                last_id = (await conn.execute(stmt)).lastrowid
                sensor_id = (await conn.execute(text('select * from `sensor` order by id desc limit 1'))).first()[0]
                stmt = insert(type_pressure).values([{
                    'Datchik davleniya_id': last_id,
                    'sensor_id': sensor_id,
                    'type_press': pressure_data.type_pressure,
                    'title_press': pressure_data.title_pressure

                }])

                await conn.execute(stmt)
                await conn.commit()
            return {'isSuccess': True, 'code': 200}

        @self.router.delete('/tables/pressure_detector/delete_by_element/{name_elem}/{value_elem}', tags=self.tags[0])
        async def delete_pressure_by_elem(name_elem: str, value_elem: str | int | float):
            res = (await get_pressure_by_elem(name_elem, value_elem))
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                await conn.execute(text(f'delete from `Datchik davleniya` where {name_elem}={value_elem}'))
                for row in res:
                    type_id = row[0]
                    await conn.execute(text(f'delete from `typePressure` where id = {type_id}'))
                await conn.commit()
            return res

    def setup_dustiness(self):
        @self.router.get('/tables/dustiness_detector/get_data/{isImage}', tags=self.tags[1])
        async def get_dustiness_data(isImage:bool):
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('select * from `Datchik zapilennosti` limit 0,500'))).all()
            return get_image_from_table(res, isImage)

        @self.router.get('/tables/dustiness_detector/get_headers', tags=self.tags[1])
        async def get_dustiness_headers():
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('show columns from `Datchik zapilennosti`'))).all()
                res = [[el[0], el[1]] for el in res]
            return res

        @self.router.get('/tables/dustiness_detector/get_by_element/{name_elem}/{value_elem}/{isImage}', tags=self.tags[1])
        async def get_dustiness_by_elem(name_elem: str, value_elem: int | float | str, isImage:bool):
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                res = (
                    await conn.execute(text(f'select * from `Datchik zapilennosti` where {name_elem}={value_elem}'))).all()
            return get_image_from_table(res, isImage)

        @self.router.post('/tables/dustiness_detector/send_data', tags=self.tags[1])
        async def post_dustiness_data(dustiness_data: DustinessSchema):
            async with self.async_engine.connect() as conn:
                stmt = insert(detector_dustiness).values([{
                    'dustiness': dustiness_data.dustiness,
                    'energy': dustiness_data.energy
                }]).returning(detector_dustiness.c.id)

                last_id = (await conn.execute(stmt)).scalar()
                sensor_id = (await conn.execute(text('select * from `sensor` order by id desc limit 1'))).first()[0]

                stmt = insert(type_dustiness).values([{
                    'Datchik zapilennosti_id': last_id,
                    'sensor_id': sensor_id,
                    'type_dustiness': dustiness_data.type_dustiness
                }])
                await conn.execute(stmt)

                await conn.commit()
            return {'isSuccess': True, 'code': 200}

        @self.router.delete('/tables/dustiness_detector/delete_by_element/{name_elem}/{value_elem}', tags=self.tags[1])
        async def delete_dustiness_by_elem(name_elem: str, value_elem: str | int | float):
            res = (await get_dustiness_by_elem(name_elem, value_elem))
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                await conn.execute(text(f'delete from `Datchik zapilennosti` where {name_elem}={value_elem}'))
                for row in res:
                    type_id = row[0]
                    await conn.execute(text(f'delete from `typeDust` where id = {type_id}'))
                await conn.commit()
            return res

    def setup_temp(self):
        @self.router.get('/tables/temp_detector/get_data/{isImage}', tags=self.tags[2])
        async def get_temp_data(isImage:bool):
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('select * from `Datchik temp` limit 0,500'))).all()
            return get_image_from_table(res, isImage)

        @self.router.get('/tables/temp_detector/get_headers', tags=self.tags[2])
        async def get_temp_headers():
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('show columns from `Datchik temp`'))).all()
                res = [[el[0], el[1]] for el in res]
            return res

        @self.router.get('/tables/temp_detector/get_by_element/{name_elem}/{value_elem}/{isImage}', tags=self.tags[2])
        async def get_temp_by_elem(name_elem: str, value_elem: int | float | str, isImage:bool):
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                res = (
                    await conn.execute(
                        text(f'select * from `Datchik temp` where {name_elem}={value_elem}'))).all()
            return get_image_from_table(res, isImage)

        @self.router.post('/tables/temp_detector/send_data', tags=self.tags[2])
        async def post_temp_data(temp_data: TempSchema):
            async with self.async_engine.connect() as conn:
                stmt = insert(detector_temp).values([{
                    'Temp': temp_data.temp
                }]).returning(detector_temp.c.id)

                last_id = (await conn.execute(stmt)).scalar()
                sensor_id = (await conn.execute(text('select * from `sensor` order by id desc limit 1'))).first()[0]

                stmt = insert(type_temp).values([{
                    'Datchik temp_id': last_id,
                    'sensor_id': sensor_id,
                    'type_temp': temp_data.type_temp,
                    'title_temp': temp_data.title_temp
                }])
                await conn.execute(stmt)

                await conn.commit()
            return {'isSuccess': True, 'code': 200}

        @self.router.delete('/tables/temp_detector/delete_by_element/{name_elem}/{value_elem}', tags=self.tags[2])
        async def delete_temp_by_elem(name_elem: str, value_elem: str | int | float):
            res = (await get_temp_by_elem(name_elem, value_elem))
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                await conn.execute(text(f'delete from `Datchik temp` where {name_elem}={value_elem}'))
                for row in res:
                    type_id = row[0]
                    await conn.execute(text(f'delete from `typeTemp` where id = {type_id}'))
                await conn.commit()
            return res

    def setup_so2(self):
        @self.router.get('/tables/so2_detector/get_data/{isImage}', tags=self.tags[3])
        async def get_so2_data(isImage: bool):
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('select * from `Datchik SO2` limit 0,500'))).all()
            return get_image_from_table(res, isImage)

        @self.router.get('/tables/so2_detector/get_headers', tags=self.tags[3])
        async def get_so2_headers():
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('show columns from `Datchik SO2`'))).all()
                res = [[el[0], el[1]] for el in res]
            return res

        @self.router.get('/tables/so2_detector/get_by_element/{name_elem}/{value_elem}/{isImage}', tags=self.tags[3])
        async def get_so2_by_elem(name_elem: str, value_elem: int | float | str, isImage: bool):
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                res = (
                    await conn.execute(
                        text(f'select * from `Datchik SO2` where {name_elem}={value_elem}'))).all()
            return get_image_from_table(res, isImage)

        @self.router.post('/tables/so2_detector/send_data', tags=self.tags[3])
        async def post_so2_data(so2_data: SO2Schema):
            async with self.async_engine.connect() as conn:
                stmt = insert(detector_so2).values([{
                    'maxConcentration': so2_data.maxConcentration
                }]).returning(detector_so2.c.id)

                last_id = (await conn.execute(stmt)).scalar()
                sensor_id = (await conn.execute(text('select * from `sensor` order by id desc limit 1'))).first()[0]

                stmt = insert(type_so2).values([{
                    'Datchik SO2_id': last_id,
                    'sensor_id': sensor_id,
                    'type_so2': so2_data.type_so2,
                    'title_so2': so2_data.title_so2
                }])
                await conn.execute(stmt)
                await conn.commit()
            return {'isSuccess': True, 'code': 200}

        @self.router.delete('/tables/so2_detector/delete_by_element/{name_elem}/{value_elem}', tags=self.tags[3])
        async def delete_so2_by_elem(name_elem: str, value_elem: str | int | float):
            res = (await get_so2_by_elem(name_elem, value_elem))
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                await conn.execute(text(f'delete from `Datchik SO2` where {name_elem}={value_elem}'))
                for row in res:
                    type_id = row[0]
                    await conn.execute(text(f'delete from `typeSO2` where id = {type_id}'))
                await conn.commit()
            return res