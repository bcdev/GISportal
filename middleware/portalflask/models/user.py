import datetime

from sqlalchemy.orm import relationship, backref
from database import Base


class User(Base):
   __tablename__ = 'user'
   id = Column(Integer, index=True, primary_key=True)
   username = Column(String(60), index=True, unique=True)
   email = Column(String(120), index=True, unique=True)
   openid = Column(String(200), index=True, unique=True)
   last_login = Column(DateTime, unique=False)

   states = relationship('State', backref=backref('user', lazy='joined'), lazy='dynamic')
   graphs = relationship('Graph', backref=backref('user', lazy='joined'), lazy='dynamic')
   quickregions = relationship('QuickRegions', uselist=False, backref=backref('user', lazy='joined'))
   roi = relationship('ROI', backref=backref('user', lazy='joined'), lazy='dynamic')
   layergroups = relationship('LayerGroup', backref=backref('user', lazy='joined'), lazy='dynamic')
   groups = relationship('UserGroup')

   def __init__(self, email=None, openid=None, username=None):
      self.email = email
      self.openid = openid
      self.username = username
      self.last_login = datetime.datetime.now()

   def __repr__(self):
      return '<User OpenID %r>' % self.openid