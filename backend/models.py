from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

class Road(Base):
    __tablename__ = "roads"
    id = Column(Integer, primary_key=True)
    road_id = Column(String, unique=True, nullable=False)
    road_name = Column(String)
    city = Column(String)
    road_weight = Column(Float)
    geom = Column(Geometry("LINESTRING", srid=4326))
