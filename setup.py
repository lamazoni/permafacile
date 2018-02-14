#!/usr/local/bin/python
from sys import exit
from database import *

from datetime import date,time,timedelta,datetime
from random import randrange
import copy

import json

init_db()

Session = sessionmaker(autocommit=False,autoflush=False,bind=engine)
db_session = Session()
from models import User,Profile,SlotType,Slot,Attender,RolesOnSlottypes


try :
	PROS1 = RolesOnSlottypes("legume","distributeur")
	# p1.rolesOnSlottypes.append(PROS1)
	# db_session.commit()
	PROS2 = RolesOnSlottypes("legume","accueil-pointage")
	# p2.rolesOnSlottypes.append(copy.deepcopy(PROS1))
	# p2.rolesOnSlottypes.append(PROS2)
	PROS3 = RolesOnSlottypes("legume","admin")
	# p3.rolesOnSlottypes.append(PROS3)

	p1 = Profile('distributeur-legume',[PROS1])
	db_session.add(p1)
	p2 = Profile('accueil-pointage-legume',[RolesOnSlottypes("legume","distributeur"),RolesOnSlottypes("legume","accueil-pointage")])
	# p2 = Profile('accueil-pointage-legume',[copy.deepcopy(PROS1),PROS2])
	db_session.add(p2)
	p3 = Profile('admin-legume',[PROS3])
	db_session.add(p3)
	db_session.commit()
	#
	u1 = User('udefault', 'default')
	u1.profile = p1
	db_session.add(u1)
	u1 = User("sasuke", "sasuke")
	u1.profile=p2
	db_session.add(u1)
	u1 = User('molly', 'molly')
	u1.profile=p2
	db_session.add(u1)
	u1 = User('uadmin', 'admin')
	u1.profile = p3
	db_session.add(u1)
	attendersEXPL=["martins","miamlegume","JulieEtNico","FamilleSuper","Lesgolas","Rutabaga","FamilleCosmic","Tartenpion","RadisEtCompagnie"]
	for attender in attendersEXPL :
		u2 = User(attender, attender)
		u2.profile = p1
		db_session.add(u2)
		db_session.commit()

	st1 = SlotType("legume","green",{'roles':[{"name":"distributeur","number":4},{"name":"accueil-pointage","number":1}]})
	db_session.add(st1)

	def createRandomAttenders():
		bunchOfAttender = []
		num=randrange(4)
		for i in range(num) :
			bunchOfAttender.append(Attender(name=attendersEXPL[randrange(len(attendersEXPL))],role="distributeur"))
		if randrange(1) :
			bunchOfAttender.append(Attender(name=attendersEXPL[randrange(len(attendersEXPL))],role="accueil-pointage"))
		return bunchOfAttender

	def createArandomSlot() :
		adate=date(2017,randrange(1,12),randrange(1,28))
		atimeStart=time(hour=randrange(1,21), minute=randrange(1,60))
		adatetimeStart=datetime.combine(adate, atimeStart)
		atimedelta=timedelta(minutes=randrange(60)+60)
		adatetimeStop=adatetimeStart+atimedelta
		# attenders=json.dumps({'attenders':createRandomAttenders()})
		# attenders={'attenders':createRandomAttenders()}
		attenders=createRandomAttenders()
		return Slot(adate,"legume",atimeStart,adatetimeStop.time(),attenders)

	for i in range(2) :
		s1 = createArandomSlot()
		db_session.add(s1)

	def createRandomAttendersDistributor():
		bunchOfAttenderDistributor = []
		num=randrange(4)
		for i in range(num) :
			bunchOfAttenderDistributor.append(Attender(name=attendersEXPL[randrange(len(attendersEXPL))],role="distributeur"))
		return bunchOfAttenderDistributor

	# s1=Slot(date(2017,1,1),"legume",time(hour=18),time(hour=19,minute=30),{'attenders':[{"name":"sasuke","role":"distributeur"},{"name":"miamlegume","role":"distributeur"},{"name":"JulieEtNico","role":"distributeur"},{"name":"RadisEtCompagnie","role":"accueil-pointage"}]})
	t1=date.today()
	bunchOfAttenders=[Attender(name="molly",role="accueil-pointage")]

	s22=Slot(t1,"legume",time(hour=18),time(hour=19,minute=30),copy.deepcopy(bunchOfAttenders)+createRandomAttendersDistributor())
	db_session.add(s22)
	print(bunchOfAttenders)
	step = 1
	for delay in range(10) :
		s22=Slot(t1 + timedelta(days=step),"legume",time(hour=18),time(hour=19,minute=30),copy.deepcopy(bunchOfAttenders)+createRandomAttendersDistributor())
		db_session.add(s22)
		s22=Slot(t1 - timedelta(days=step),"legume",time(hour=18),time(hour=19,minute=30),copy.deepcopy(bunchOfAttenders)+createRandomAttendersDistributor())
		db_session.add(s22)
		step += 2
	# s23=Slot(date(2017,12,2),"legume",time(hour=18),time(hour=19,minute=30),copy.deepcopy(bunchOfAttenders))
	# db_session.add(s23)
	# s24=Slot(date(2017,12,3),"legume",time(hour=18),time(hour=19,minute=30),copy.deepcopy(bunchOfAttenders)
	# db_session.add(s24)
	# s22=Slot(date(2017,12,1),"legume",time(hour=18),time(hour=19,minute=30),copy.deepcopy(bunchOfAttenders))
	# db_session.add(s22)
	# s23=Slot(date(2017,12,2),"legume",time(hour=18),time(hour=19,minute=30),copy.deepcopy(bunchOfAttenders))
	# db_session.add(s23)
	# s24=Slot(date(2017,12,3),"legume",time(hour=18),time(hour=19,minute=30),copy.deepcopy(bunchOfAttenders))

	bunchOfAttenders=[Attender(name="sasuke",role="accueil-pointage")]

	print(bunchOfAttenders)
	step = 2
	for delay in range(10) :
		s22=Slot(t1 + timedelta(days=step),"legume",time(hour=18),time(hour=19,minute=30),copy.deepcopy(bunchOfAttenders)+createRandomAttendersDistributor())
		db_session.add(s22)
		s22=Slot(t1 - timedelta(days=step),"legume",time(hour=18),time(hour=19,minute=30),copy.deepcopy(bunchOfAttenders)+createRandomAttendersDistributor())
		db_session.add(s22)
		step += 2

	db_session.commit()
except Exception as e :
	print("error,cannot clean")
	print(str(e)+str(e.args))
	exit(1)
