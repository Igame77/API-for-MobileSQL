from fastapi import APIRouter
from models import production_unit, ProductionSchema
from sqlalchemy import insert, text
from sqlalchemy.ext.asyncio import AsyncEngine
from api.getterImages import get_image_from_table
class ProductionManager:
    def __init__(self, engine: AsyncEngine, router: APIRouter):
        self.async_engine = engine
        self.router = router
        self.tags = ['Production unit']
    def setup(self):
        @self.router.get('/tables/production_unit/get_data/{isImage}', tags=self.tags)
        async def get_product_data(isImage:bool):
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('select * from `Production_unit` limit 0,500'))).all()
            return get_image_from_table(res, isImage)

        @self.router.get('/tables/production_unit/get_headers', tags=self.tags)
        async def get_product_header():
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text('show columns from `Production_unit`'))).all()
                res = [[el[0], el[1]] for el in res]
            return res

        @self.router.get('/tables/production_unit/get_by_element/{name_elem}/{value_elem}/{isImage}', tags=self.tags)
        async def get_product_by_elem(name_elem: str, value_elem: str | int | float, isImage:bool):
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                res = (await conn.execute(text(f'select * from `Production_unit` where {name_elem}={value_elem}'))).all()
            return get_image_from_table(res, isImage)

        @self.router.post('/tables/production_unit/send_data', tags=self.tags)
        async def post_product_data(product_data: ProductionSchema):
            async with self.async_engine.connect() as conn:
                absort_id = (await conn.execute(text('select * from `absortion tower` order by id desc limit 1'))).first()[0]
                ciclon_id = (await conn.execute(text('select * from `Ciclon` order by id desc limit 1'))).first()[0]
                furn_id = (await conn.execute(text('select * from `Furn order by id desc limit 1'))).first()[0]
                sensor_id = (await conn.execute(text('select * from `sensor` order by id desc limit 1'))).first()[0]

                stmt = insert(production_unit).values([{
                    'absortion tower_id': absort_id,
                    'Ciclon_id': ciclon_id,
                    'Furn_id': furn_id,
                    'sensor_type_id': sensor_id,
                    'description': product_data.description,
                    'object': product_data.object_
                }])
                await conn.execute(stmt)
                await conn.commit()
            return {'isSuccess': True, 'code': 200}

        @self.router.delete('/tables/production_unit/delete_by_element/{name_elem}/{value_elem}', tags=self.tags)
        async def delete_product_by_elem(name_elem: str, value_elem: str | int | float):
            res = (await get_product_by_elem(name_elem, value_elem))
            if type(value_elem) == str:
                value_elem = f"'{value_elem}'"
            async with self.async_engine.connect() as conn:
                await conn.execute(text(f'delete from `Production_unit` where {name_elem}={value_elem}'))
                await conn.commit()
            return res