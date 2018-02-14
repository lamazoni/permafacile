from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Time, ARRAY,JSON,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_method
from marshmallow import Schema, fields, ValidationError, pre_load
from datetime import datetime,date,timedelta

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

import json
from _config import *

##### MODELS #####
class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	name = Column(String(30))
	password = Column(String(120))
	profile_id = Column(Integer, ForeignKey('profiles.id'))

	def __init__(self, name=None, password=None):
		self.name = name
		self.password = password
		# self.profile_name = profile_name
		# self.role = role

	def __repr__(self):
		return '<name {0!r} password {1!r} profile_id {2!r} profile {3!r} >'.format(self.name,self.password,self.profile_id,self.profile)

	@property
	def serializer(self) :
		return { 'name': self.name }

class RolesOnSlottypes(Base):
	__tablename__ = 'rolesonslotypes'
	id = Column(Integer, primary_key=True)
	slottype_name = Column(String(30))
	role = Column(String(30))
	profile_id = Column(Integer, ForeignKey('profiles.id'))
	profile = relationship("Profile", back_populates="rolesOnSlottypes")
	def __init__ (self,slottype_name=None,role=None):
		self.slottype_name = slottype_name
		self.role = role
	def __repr__(self):
		return '< slottype_name {0!r} role {1!r}>'.format(self.slottype_name, self.role)

	@property
	def serializer(self) :
		return { 'slottype_name': self.slottype_name, 'role': self.role }

class Profile(Base):
	__tablename__ = 'profiles'
	id = Column(Integer, primary_key=True)
	name = Column(String(30))
	# {'main':"rwx",'legume':"rwxrwxrwx"}
	# tagFct_rights = Column(postgresql.HSTORE)
	rolesOnSlottypes = relationship("RolesOnSlottypes", back_populates="profile")
	users = relationship("User", backref="profile")

	def __init__(self, name='distributeur-legume',rolesOnSlottypes=[]):
		self.name = name
		self.rolesOnSlottypes = rolesOnSlottypes

	def __repr__(self):
		return '<Profile {0!r} rolesOnSlottypes {1!r} >'.format(self.name, self.rolesOnSlottypes)

	def getRolesOnASlottype(self,aSlottype_name):
		alist = []
		for roleAndSlotype in self.rolesOnSlottypes :
			if roleAndSlotype.serializer['slottype_name'] == aSlottype_name :
				alist.append(roleAndSlotype.serializer['role'])
		return alist

	@property
	def serializer(self):
		aSerializeProfile = {'name':self.name}
		alist = []
		for roleAndSlotype in self.rolesOnSlottypes :
			alist.append(roleAndSlotype.serializer)
		aSerializeProfile.update({'rolesOnSlottypes':alist})
		return aSerializeProfile

class SlotType(Base):
	__tablename__ = 'slottypes'
	name = Column(String(12),primary_key=True)
	color = Column(String(12))
	slots = relationship("Slot", backref="slottype")
	#roles =
	#{'roles':[{"name":"distributeur","number":4},{"name":"accueil-pointage","number":1}]}
	roles = Column(JSON)

	def __init__ (self,name=None,color=None,roles=[]):
		self.name = name
		self.color = color
		self.roles = roles

	def __repr__(self):
		return '<name {0!r}>'.format(self.name)

	@property
	def serializer(self):
		aSerializedSlotType = {'name': self.name, 'color':self.color}
		aSerializedSlotType.update(self.roles)
		return aSerializedSlotType

class Attender(Base):
	__tablename__ = 'attenders'
	id = Column(Integer, primary_key=True)
	slot_id = Column(Integer, ForeignKey('slots.id'))
	name = Column(String(30))
	role = Column(String(30))
	slot = relationship("Slot", back_populates="attenders")
	def __init__ (self,name=None,role=None):
		self.name = name
		self.role = role
	def __repr__(self):
		return '<name {0!r} role {1!r}>'.format(self.name, self.role)

	@property
	def serializer(self) :
		return { 'name': self.name, 'role': self.role }

class Slot(Base):
	__tablename__ = 'slots'
	id = Column(Integer,primary_key=True)
	# hash = Column(Integer)
	date = Column(Date)
	slottype_name = Column(String(12), ForeignKey('slottypes.name'))
	start = Column(Time)
	end = Column(Time)
	attenders = relationship("Attender", back_populates="slot")
	lock = Column(Boolean)
	lockCancelAttender = Column(Boolean)
	#attenders = Column(JSON)
	#attenders = {[{"name":"toto","role":"distributeur"},{"name":"tutu","role":"accueil-pointage"}]}

	def __init__ (self,date=None,slottype_name=None,start=None,end=None,attenders=[],lock=False,lockCancelAttender=False) :
		print("initialize"+str(date))
		self.date = date
		self.slottype_name = slottype_name
		self.start = start
		self.end = end
		# self.attenders = self.validateAttendersRole(attenders)
		self.attenders = attenders
		self.lock = lock
		self.lockCancelAttender = lockCancelAttender

	def __repr__ (self) :
		return '<Id {0!r} hash {1!r} date {2!r} start {3!r} end {4!r} attender {5!r} lock {6!r} lockCancelAttender {7!r}>'.format(self.id, self.date, self.start, self.end, self.attenders, self.lock, self.lockCancelAttender)

	# NOK NOK NOK
	def validateAttendersRole(self,attenders):
		attendersToCheck=attenders.get("attenders")
		# NOK NOK NOK
		roles = self.slottype.roles.get("roles")
		names = []
		numberByName = {}
		for role in roles :
			names.append(role.name)
			numberByName.update({role.name : role.number})
		for attender in attendersToCheck :
			if not 'name' in attender.keys() :
				raise Exception("validateAttendersRole: name field missing")
			if not 'role' in attender.keys() :
				raise Exception("validateAttendersRole: role field missing")
			if attender.get('role') not in names :
				raise Exception("validateAttendersRole: role unknown")

		#TODO:validate the number of role
		# curNumberByName = {}
		# for attender in attendersToCheck :
		# 	curNumberByName.update({attender.get('role'):0})
		# for attender in attendersToCheck :
		# 	curNumberByName.update({attender.get('role'):curNumberByName.get(attender.get('role')+1)})

		#TODO:validate the role
		#check that the user have a validate role
		return attenders

	def computeLockCancelAttender(self):
		if  not self.lockCancelAttender :
			if ( date.today() <= self.date and(self.date - timedelta(days=FORBID_CANCEL_ATTENDER_DELAY) < date.today()) ) :
				return True
			else :
				return False
		else :
			return True

	# def computeLock(self):
	# 	if  not self.lock :
	# 		if ( self.date > (date.today()+ timedelta(days=9)) {
	# 			return True
	# 		} else {
	# 			return False
	# 		}
	# 	else :
	# 		return True


	@property
	def serializer(self):
		"""Return object data in easily serializeable format"""
		aSerializeSlot= { 'id': str(self.id), 'date': str(self.date), 'start': str(self.start), 'end':str(self.end), 'lock':self.lock,'lockCancelAttender':self.computeLockCancelAttender()}
		aSerializeSlot.update({'slottype':self.slottype.serializer})
		# aSerializeSlot.update(json.loads(self.attenders))
		alist = []
		for attender in self.attenders :
			alist.append(attender.serializer)
		aSerializeSlot.update({'attenders':alist})
		# print("aSerializeSlot:"+str(aSerializeSlot))
		return aSerializeSlot

	@property
	def serializerAttenders(self):
		alist = []
		for attender in self.attenders :
			alist.append(attender.serializer)
		return alist

class Log(Base):
	__tablename__ = 'logs'
	id = Column(Integer,primary_key=True)
	when = Column(DateTime)
	who = Column(String(30))
	where_slotdate = Column(Date)
	where_slotname = Column(String(20))
	what = Column(ARRAY(String(300)))
	detailedChange = Column(JSON)

	def __init__ (self,alog={}) :
		self.when = alog['when']
		self.who = alog['who']
		self.where_slotname = alog['where_slotname']
		self.where_slotdate = alog['where_slotdate']
		self.what = alog['what']
		self.detailedChange = alog['detailedChange']

	def __repr__ (self) :
		return '<Id {0!r} when {1!r} who {2!r} where {3!r} {4!r} what {5!r} detailedChange {6!r} >'.format(self.id, self.when, self.who, self.what, self.where_slotname, self.where_slotdate, self.detailedChange)

	@property
	def todisplay(self):
		whatconcat = ""
		for aaction in self.what :
			whatconcat += aaction +"\n"
		# return {'when':self.when.,'who':self.who, 'where_slotdate':self.where_slotdate.strftime("%Y-%m-%d"), 'where_slotname':self.where_slotname,'what':whatconcat}
		return {'id': self.id,'when':self.when.isoformat(),'who':self.who.rstrip(), 'where_slotdate':self.where_slotdate.isoformat(), 'where_slotname':self.where_slotname,'what':whatconcat}

###SCHEMA###
class SlotTypeSchema(Schema):
	name = fields.Str()
	color = fields.Str()

class AttenderSchema(Schema):
	id = fields.Int(dump_only=True)
	first = fields.Str()
	last = fields.Str()

class SlotSchema(Schema):
	id = fields.Int(dump_only=True)
	date = fields.Date()
	slottype = fields.Nested(SlotTypeSchema)
	start = fields.Time()
	end = fields.Time(Time)
	attenders = fields.Nested(AttenderSchema, many=True)
