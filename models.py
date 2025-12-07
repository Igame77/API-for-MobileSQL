from sqlalchemy import Table, Column, Integer, Float, MetaData, VARCHAR, Date, ForeignKey, DateTime
from pydantic import BaseModel
from datetime import date as date_
from datetime import datetime as datetime_

metadata_obj = MetaData()

warning_valve = Table(
    'Warning valve',
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column('Power', Float),
    Column('maxPressure', Float),
    Column('maxTemp', Integer),
)

warning_relay = Table(
    'Warning Relay',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('maxDust', Float),
    Column('maxConcentration', Float)
)

user_dev = Table(
    'user_dev',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('isValve', Integer),
    Column('isRelay', Integer),
    Column('Warning Relay_id', Integer, ForeignKey('Warning Relay.id')),
    Column('Warning valve_id', Integer, ForeignKey('Warning valve.id'))
)

sensor = Table(
    'sensor',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('accuracy', Float),
    Column('date', Date),
    Column('user_dev_id', Integer, ForeignKey('user_dev.id'))
)

absortion_tower = Table(
    'absortion tower',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('accuracy', Float)
)

ciclon = Table(
    'Ciclon',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('Pressure', Float),
    Column('Concentration', Float)
)

furn = Table(
    'Furn',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('loss', Float),
    Column('date_create', DateTime)
)

detector_temp = Table(
    'Datchik temp',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('Temp', Integer)
)

detector_so2 = Table(
    'Datchik SO2',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('maxConcentration', Float)
)

detector_pressure = Table(
    'Datchik davleniya',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('Pressure', Float),
    Column('maxLoss', Float)
)

detector_dustiness = Table(
    'Datchik zapilennosti',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('dustiness', Float),
    Column('energy', Float)
)

type_pressure = Table(
    'typePressure',
    metadata_obj,
    Column('Datchik davleniya_id', Integer, ForeignKey('Datchik davleniya.id')),
    Column('sensor_id', Integer, ForeignKey('sensor.id')),
    Column('type_press', VARCHAR(45)),
    Column('title_press', VARCHAR(100))
)

type_dustiness = Table(
    'typeDust',
    metadata_obj,
    Column('Datchik zapilennosti_id', Integer, ForeignKey('Datchik zapilennosti.id')),
    Column('sensor_id', Integer, ForeignKey('sensor.id')),
    Column('type_dustiness', VARCHAR(45))
)

type_temp = Table(
    'typeTemp',
    metadata_obj,
    Column('Datchik temp_id', Integer, ForeignKey('Datchik temp.id')),
    Column('sensor_id', Integer, ForeignKey('sensor.id')),
    Column('type_temp', VARCHAR(45)),
    Column('title_temp', VARCHAR(100))
)

type_so2 = Table(
    'typeSO2',
    metadata_obj,
    Column('Datchik SO2_id', Integer, ForeignKey('Datchik SO2.id')),
    Column('sensor_id', Integer, ForeignKey('sensor.id')),
    Column('type_so2', VARCHAR(45)),
    Column('title_so2', VARCHAR(100))
)

production_unit = Table(
    'Production_unit',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('absortion tower_id', Integer, ForeignKey('absortion tower.id')),
    Column('Ciclon_id', Integer, ForeignKey('Ciclon.id')),
    Column('Furn_id', Integer, ForeignKey('Furn.id')),
    Column('sensor_type_id', Integer, ForeignKey('sensor.id')),
    Column('description', VARCHAR(100)),
    Column('object', VARCHAR(45))
)

ore = Table(
    'Ore',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('weight', Float),
    Column('content', Float),
    Column('waste', Float),
    Column('Production_unit_id', Integer, ForeignKey('Production_unit.id'))
)

class OreSchema(BaseModel):
    weight: float
    content: float
    waste: float
    production_unit_id: int

class ProductionSchema(BaseModel):
    description: str
    object_: str

class DustinessSchema(BaseModel):
    dustiness: float
    energy: float
    type_dustiness: str

class PressureSchema(BaseModel):
    pressure: float
    maxLoss: float
    type_pressure: str
    title_pressure: str

class SO2Schema(BaseModel):
    maxConcentration: float
    type_so2: str
    title_so2: str

class TempSchema(BaseModel):
    temp: int
    type_temp: str
    title_temp: str

class FurnSchema(BaseModel):
    loss: float
    date_create: datetime_

class CiclonSchema(BaseModel):
    pressure: float
    concentration: float

class AbsortionSchema(BaseModel):
    accuracy: float

class SensorSchema(BaseModel):
    accuracy: float
    date: date_

class UserDevSchema(BaseModel):
    isValve: bool
    isRelay: bool

class SchemaRelay(BaseModel):
    maxDust: float
    maxConcentration: float

class ValveSchema(BaseModel):
    power: float
    maxPressure: float
    maxTemp: int