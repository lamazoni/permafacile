from copy import deepcopy
from dictdiffer import diff
from models import *
from pprint import pformat
import sys
from datetime import datetime,date,time
import json

def checkInputId(an_id):
	if not (an_id.isnumeric()) :
		raise Exception('id must be numeric')
	if not isinstance(int(an_id), int) :
		raise Exception('id must be a int')
	if not (int(an_id) <10000 and int(an_id) > 0 ):
		raise Exception('id must be lower')

def checkInputAsDate(adate) :
	try :
		if not (adate.isnumeric()) :
			raise
		if not (not int(adate) > 20200000) :
			raise
		if not (not int(adate) < 20170000) :
			raise
	except Exception as e:
		raise Exception('error date format expect YYYYMMDD',e)

def checkSlot(updatedSlot):
	if not isinstance(updatedSlot, dict):
		raise Exception('wrong update slot')
	keys = updatedSlot.keys()

	for element in ["id", "date", "start", "end", "attenders","slottype","lock","lockCancelAttender"]:
		if element not in keys:
			raise Exception('wrong formated slot, missing element')
	if not len(keys) == 8 :
		raise Exception('wrong formated slot')
	checkInputId(updatedSlot['id'])
	if not isinstance(updatedSlot['date'], str) :
		raise Exception('wrong update slot')
	if not isinstance(updatedSlot['start'], str) :
		raise Exception('wrong update slot')
	if not isinstance(updatedSlot['end'], str) :
		raise Exception('wrong update slot')
	if not isinstance(updatedSlot['lock'], bool) :
		raise Exception('wrong update slot, bool expected')
	if not isinstance(updatedSlot['lockCancelAttender'], bool) :
		raise Exception('wrong update slot, bool expected')
	if not isinstance(updatedSlot['attenders'], list):
		raise Exception('wrong update slot')
	for attender in updatedSlot['attenders'] :
		if not isinstance(attender, dict):
			raise Exception('attender not class dict')
		for element in ['name','role'] :
			if element not in attender.keys() :
				raise Exception('attender missing name or role')
		if not len(attender.keys()) == 2 :
			raise Exception('attender wrong formated slot')

def evalAttendersChange(attendersDB, attendersUpdated) :
	theChanges = {'sup':[],'add':[]}
	#step1 : check for any difference
	for attender in attendersDB :
		if attender not in attendersUpdated :
			theChanges['sup'].append(attender)
	for attender in attendersUpdated :
		if attender not in attendersDB :
			theChanges['add'].append(attender)

	#step2 : check for muliple change on difference
	adiferIte=diff(attendersDB,attendersUpdated)
	for adiff in adiferIte :
		print("evalAttendersChange adiff"+str(adiff))
		if adiff[0]=='change' :
			for achange in adiff[2] :
				# what.append("changement de {0!s} en {1!s} ".format(achange[0],achange[1]))
				pass
		if adiff[0]=='remove' and len(adiff[1])==0 :
			for armv in adiff[2] :
				if armv[1] not in theChanges['sup'] :
					theChanges['sup'].append(attender)
		if adiff[0]=='add' and len(adiff[1])==0:
			for aadd in adiff[2] :
				if aadd[1] not in theChanges['add'] :
					theChanges['add'].append(attender)

	#step3 : remove double entry
	# Remove a attender entry if add/sup
	for attender in theChanges['add'] :
		if attender in theChanges['sup'] :
			theChanges['sup'].remove(attender)
			theChanges['add'].remove(attender)

	# Remove a attender entry if it is a change/shift (this removal has already been seen at step1)
	for attender in theChanges['sup'] :
		if attendersDB.count(attender) == attendersUpdated.count(attender) :
			theChanges['sup'].remove(attender)
	for attender in theChanges['add'] :
		if attendersDB.count(attender) == attendersUpdated.count(attender) :
			theChanges['add'].remove(attender)
	return theChanges

def makeLog(theChanges,name):
	alog = {}
	alog['when'] = datetime.now()
	alog['who'] = name
	alog['what'] = []
	# Display
	for key in theChanges.keys() :
		if key == 'add' and len(theChanges["add"]) > 0:
			alog['what'].append("Ajout de ")
			for attender in theChanges["add"] :
				alog['what'].append(attender['name'] + "("+attender['role']+") ")
		if key == 'sup' and len(theChanges["sup"]) > 0 :
			alog['what'].append("Suppression de ")
			for attender in theChanges["sup"] :
				alog['what'].append(attender['name'] + "("+attender['role']+") ")
	print(pformat(alog))
	return alog

def checkAttenders(attendersDB, attendersUpdated):
	difer=list(diff(attendersDB,attendersUpdated))
	print("checkAttenders DIFER:"+pformat(difer))
	accept= True
	for adiff in difer :
		if adiff[0]=='change' and len(adiff[1]) != 2 :
			accept = False
		if adiff[0]=='remove' and len(adiff[1]) != 0 :
			accept = False
		if adiff[0]=='add' and len(adiff[1]) != 0 :
			accept = False
	return accept

def updateAttendersLockInSlot(db_session, curentUser, updatedSlot):

	if db_session.query(Slot).filter_by(id=updatedSlot.get('id')).count() != 1 :
		raise Exception("Slot not found")

	dbSlot=db_session.query(Slot).filter_by(id=updatedSlot.get('id')).one()

	if not checkAttenders(dbSlot.serializerAttenders,updatedSlot.get('attenders')) :
		return False,'other than viewer or modification not reconized'

	# print("DB attenders:"+pformat(dbSlot.serializerAttenders))
	# print("PUT attenders:"+pformat(updatedSlot['attenders']))
	theChanges=evalAttendersChange(dbSlot.serializerAttenders, updatedSlot.get('attenders'))
	allowedChange = False

	userRolesForThisSlot=curentUser.profile.getRolesOnASlottype(dbSlot.slottype.name)
	#The user change himself check
	if len(theChanges['sup']) + len(theChanges['add']) == 1 :
		if len(theChanges['sup']) == 1 :
			theChangedName=theChanges['sup'][0]['name']
			theChangedRole=theChanges['sup'][0]['role']
		else :
			theChangedName=theChanges['add'][0]['name']
			theChangedRole=theChanges['add'][0]['role']
		if not dbSlot.lock and (theChangedName == curentUser.name and theChangedRole in userRolesForThisSlot ):
			allowedChange= True

	#A admin or accueil-pointage change somebody else check
	#TODO: put more check here
	if len(theChanges['sup']) + len(theChanges['sup']) != 1 :
		if 'admin' in userRolesForThisSlot or 'accueil-pointage' in userRolesForThisSlot :
			allowedChange= True

	if not allowedChange :
		return False,'change not allowed'

	alog=makeLog(theChanges,curentUser.name)
	alog['where_slotname']=dbSlot.slottype.name
	alog['where_slotdate']=dbSlot.date
	alog['detailedChange']=json.dumps(list(diff(dbSlot.serializerAttenders,updatedSlot.get('attenders'))))
	db_session.add(Log(alog))
	
	bunchOfAttenders=[]
	for attender in updatedSlot.get('attenders'):
		bunchOfAttenders.append(Attender(name=attender.get("name"),role=attender.get("role")))
	dbSlot.attenders = bunchOfAttenders

	if updatedSlot.get('lock') != dbSlot.lock :
		dbSlot.lock = updatedSlot.get('lock')
		if dbSlot.lock == True :
			alog['what'].append("Participations verifiees.")
		else :
			alog['what'].append("Deverrouillage des participations.")
	return True,dbSlot
