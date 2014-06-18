import datetime

from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

from database import Base

association_table = Table('association', Base.metadata,
                          Column('user_id', Integer, ForeignKey('user.id')),
                          Column('user_group_id', Integer, ForeignKey('user_group.id'))
)

class User(Base):
   __tablename__ = 'user'
   id = Column(Integer, index=True, primary_key=True)
   username = Column(String(60), index=True, unique=True)
   full_name = Column(String(120), index=True, unique=True)
   email = Column(String(120), index=True, unique=True)
   openid = Column(String(200), index=True, unique=True)
   last_login = Column(DateTime, unique=False)

   states = relationship('State', backref=backref('user', lazy='joined'), lazy='dynamic')
   graphs = relationship('Graph', backref=backref('user', lazy='joined'), lazy='dynamic')
   quickregions = relationship('QuickRegions', uselist=False, backref=backref('user', lazy='joined'))
   roi = relationship('ROI', backref=backref('user', lazy='joined'), lazy='dynamic')
   layergroups = relationship('LayerGroup', backref=backref('user', lazy='joined'), lazy='dynamic')
   groups = relationship('UserGroup', secondary=association_table)


   def __init__(self, email=None, openid=None, username=None, full_name=None, groups=None):
      self.username = username
      self.full_name = full_name
      self.email = email
      self.openid = openid
      self.groups = groups
      self.last_login = datetime.datetime.now()

   def __repr__(self):
      return '<User OpenID %r>' % self.openid