from sqlalchemy import Column, Integer, String, ForeignKey

from database import Base

class Shape(Base):
    __tablename__ = 'shape'
    id = Column(Integer, index=True, primary_key=True)
    name = Column(String)
    geometry = Column(String)
    bounding_box = Column(String)
    shapefile_id = Column(Integer, ForeignKey('shapefile.id'))
    record_number = Column(Integer)


    def __init__(self, record_number, name):
        self.record_number = record_number
        self.name = name


    def __repr__(self):
        return '<Name: %s ID: %r>' % (self.name, self.id)