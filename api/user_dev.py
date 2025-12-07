from fastapi import APIRouter
from models import UserDevSchema, user_dev
from sqlalchemy import text, insert
from sqlalchemy.ext.asyncio import AsyncEngine
from api.getterImages import get_image_from_table
class UserDevManager:
    def __init__(self, engine: AsyncEngine, router: APIRouter):
        self.async_engine = engine
        self.router = router
        self.tags = ['User Dev']

    def setup(self):
        @self.router.get('/tables/user_dev/get_data/{isImage}', tags=self.tags)
        async def get_user_dev_data(isImage:bool):
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('select * from `user_dev` limit 0,500'))).all()
            return get_image_from_table(res, isImage)

        @self.router.get('/tables/user_dev/get_headers', tags=self.tags)
        async def get_user_dev_headers():
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('show columns from `user_dev`'))).all()
                res = [[el[0], el[1]] for el in res]
            return res

        @self.router.get('/tables/user_dev/get_data_by_element/{name_elem}/{value_elem}/{isImage}',\
                         tags=self.tags)
        async def get_user_dev_by_elem(name_elem: str, value_elem: str | float | int, isImage:bool):
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text(f'select * from `user_dev` where {name_elem} = {value_elem}'))).all()
            return get_image_from_table(res, isImage)

        @self.router.post('/tables/user_dev/send_data', tags=self.tags)
        async def send_user_dev_data(user_dev_data: UserDevSchema):
            async with self.async_engine.connect() as conn:
                id_relay = (await conn.execute(text('select * from `Warning Relay` order by id desc limit 1'))).first()[0]
                id_valve = (await conn.execute(text('select * from `Warning valve` order by id desc limit 1'))).first()[0]
                print(id_relay, id_valve)
                stmt = insert(user_dev).values([{
                    'isValve': user_dev_data.isValve,
                    'isRelay': user_dev_data.isRelay,
                    'Warning Relay_id': id_relay,
                    'Warning valve_id': id_valve

                }])
                await conn.execute(stmt)
                await conn.commit()
            return {'isSuccess': True, 'code': 200}

        @self.router.delete('/tables/user_dev/delete_by_element/{name_elem}/{value_elem}', tags=self.tags)
        async def delete_user_dev_by_elem(name_elem: str, value_elem: str | float | int):
            res = (await get_user_dev_by_elem(name_elem, value_elem))
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                await conn.execute(text(f'delete from `user_dev` where {name_elem} = {value_elem}'))
                await conn.commit()
            return res