from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from api import get_main_router
import config

async_engine = create_async_engine(config.db_url)

mainRouter = get_main_router(async_engine)

app = FastAPI(title='MySQL API')
app.include_router(mainRouter)





