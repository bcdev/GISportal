from sqlalchemy import Column, Integer, String

from database import Base

class UserGroup(Base):
   __tablename__ = 'user_group'
   id = Column(Integer, index=True, primary_key=True)
   group_name = Column(String, unique=True)

   def __init__(self, group_name=None):
      self.group_name = group_name

   def __repr__(self):
      return '<Group Name: %s ID %r>' % (self.group_name, self.id)