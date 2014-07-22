from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base

class Shapefile(Base):
    __tablename__ = 'shapefile'
    id = Column(Integer, index=True, primary_key=True)
    name = Column(String)
    path = Column(String, unique=True)
    children = relationship("Shape")

    def __init__(self, name, path, children):
        self.name = name
        self.path = path
        self.children = children


    def __repr__(self):
        return '<Name: %s ID: %r Path: %s>' % (self.name, self.id, self.path)