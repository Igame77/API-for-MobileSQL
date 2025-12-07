from .warning_valve import ValveManager
from .warning_relay import RelayManager
from .user_dev import UserDevManager
from .sensor import SensorsManager
from .absortion_tower import AbsortManager
from .ciclon import CiclonManager
from .furn import FurnManager
from .detectors import DetectorsManager
from .production_unit import ProductionManager
from .ore import OreManager
from .custom_query import CustomQueryManager

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncEngine


def get_main_router(engine: AsyncEngine):
    mainRouter = APIRouter()

    valve_manager = ValveManager(engine, mainRouter)
    relay_manager = RelayManager(engine, mainRouter)
    user_manager = UserDevManager(engine, mainRouter)
    sensor_manager = SensorsManager(engine, mainRouter)
    absort_manager = AbsortManager(engine, mainRouter)
    ciclon_manager = CiclonManager(engine, mainRouter)
    furn_manager = FurnManager(engine, mainRouter)
    detectors_manager = DetectorsManager(engine, mainRouter)
    production_manager = ProductionManager(engine, mainRouter)
    ore_manager = OreManager(engine, mainRouter)
    custom_manager = CustomQueryManager(engine, mainRouter)

    valve_manager.setup()
    relay_manager.setup()
    user_manager.setup()
    sensor_manager.setup()
    absort_manager.setup()
    ciclon_manager.setup()
    furn_manager.setup()
    detectors_manager.setup_pressure()
    detectors_manager.setup_dustiness()
    detectors_manager.setup_temp()
    detectors_manager.setup_so2()
    production_manager.setup()
    ore_manager.setup()
    custom_manager.setup()

    return mainRouter