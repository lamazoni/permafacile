
from flask import Flask, render_template, request, session, flash, redirect, url_for, g, jsonify
import sqlite3
from functools import wraps

#my modules
from database import session_factory

from models import *
from utils import *

from datetime import date
import json
import sys,traceback

from time import sleep

app = Flask(__name__)
app.config.from_object("_config")
from form import RegistrationForm, LoginForm

from flask_sqlalchemy_session import flask_scoped_session
db_session=flask_scoped_session(session_factory, app)


def login_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged_in' in session :
			return test(*args, **kwargs)
		else:
			flash('You need to log in first.')
			return redirect(url_for('login'))
	return wrap

@app.route('/',methods=['GET','POST'])
def login():
	error=None
	status_code=200
	form3=LoginForm(request.form)
	if request.method =='POST':
		if not form3.validate() :
			error = 'Invalid Credentials.Please try	again.'
			status_code	= 401
		else :
			auser=db_session.query(User).filter_by(name = form3.username.data).filter_by( password = form3.password.data).first()
			if auser == None:
				error = 'User not found.Please try	again.'
				status_code	= 401
			else :
				session['logged_in']=True
				session['user_id']=auser.id
				session['name']=auser.name
				return redirect(url_for('main'))
	return render_template('login.html',form=form3,error=error),status_code

@app.route('/createlogin',methods=['GET','POST'])
def createlogin():
	status_code=200
	form2=RegistrationForm(request.form)
	if request.method =='POST':
		if not form2.validate() :
			flash("The entry is not valid, plz retry")
		else :
			# user=User(name=form2.username.data,password=form2.password.data)
			# db_session.add(user)
			# print((request.form['username'],request.form['password']))
			# db_session.commit()
			# flash("User created successfully")
			return redirect(url_for('login'))
	return render_template('createlogin.html',form2=form2,error=None),status_code

@app.route('/main')
@login_required
def main():
	if 'user_id' in session :
		curentUser = db_session.query(User).filter_by(id=session['user_id']).first()
		# return render_template('main.html',name=curentUser.name,error=None)
		return render_template('main.html',name=session['name'],profile=curentUser.profile.serializer,error=None)
	else :
		return render_template('main.html',name=None,error=None)

@app.route('/initializeBB', methods=['GET'])
@login_required
def initializeBB():
	if 'user_id' in session :
		curentUser = db_session.query(User).filter_by(id=session['user_id']).first()
		return jsonify({'name':curentUser.name})
	else :
		return jsonify({}),404

@app.route('/schedule', methods=['GET'])
@login_required
def scheduleAll():
	if request.method =='GET':
		results=[]
		try:
			for slot in db_session.query(Slot).order_by(Slot.date).order_by(Slot.start).all():
				results.append({'id':slot.id,'date':slot.date.strftime("%Y%m%d")})
			return jsonify({'schedule': results})
		except Exception as e:
			return jsonify({'msg':'error '+str(e)}),404

@app.route('/schedule/<string:adate>', methods=['GET','PUT'])
@login_required
def schedule(adate):
	if request.method =='GET':
		results=[]
		try:
			checkInputAsDate(adate)
			thedate=date(int(adate[:4]),int(adate[4:6]),int(adate[6:]))
			for slot in db_session.query(Slot).filter_by(date=thedate).all() :
				results.append({'id':slot.id,'date':slot.date.strftime("%Y%m%d")})
			return jsonify({'schedule': results})
		except Exception as e:
			return jsonify({'msg':'error '+str(e)}),404

@app.route('/slot/<string:an_id>', methods=['GET','PUT'])
@login_required
def slotapi(an_id):
	try :
		if request.method =='GET':
			try :
				checkInputId(an_id)
				return jsonify(db_session.query(Slot).filter_by(id=an_id).one().serializer)
			except Exception as e:
				return jsonify({'msg':'error '+str(e)}),404
		elif request.method =='PUT':
			curentUser=db_session.query(User).filter_by(id=session['user_id']).first()
			updatedSlot=request.get_json()
			checkSlot(updatedSlot)
			result=updateAttendersLockInSlot(db_session,curentUser,updatedSlot)
			if result[0] == True :
				db_session.commit()
				return jsonify(result[1].serializer)
			else :
				return jsonify({'msg':result[1]}),403

			# raise Exception('other than legume, distributeur or accueil-pointage not implemented')
	except Exception as e :
		print(sys.exc_info()[0])
		print(sys.exc_info()[1])
		print(sys.exc_info()[2])
		traceback.print_tb(sys.exc_info()[2])
		return jsonify({'msg':'error '+str(e)+str(e.args)}),400

@app.route('/slot/search', methods=['GET'])
@login_required
def slotapiSearch():
	try :
		name = request.args.get('name', '')
		role = request.args.get('role', '')
		special = request.args.get('special','')
		results=[]
		if special == 'all':
			for slot in db_session.query(Slot).order_by(Slot.date).order_by(Slot.start).all() :
				results.append(slot.serializer)
			return jsonify(results)
		else :
			if (len(name) > 0 and len(role) > 0) and len(special)==0:
			# if (len(name) > 0 and len(role) > 0) :
				# for slot in db_session.query(Slot).filter({'name':name,'role':role} in Slot.attenders.get("attenders")).order_by(Slot.date).order_by(Slot.start).all() :
				aAttender= Attender(name=name,role=role)
				# print("aAttender"+str(aAttender))
				# print("name:"+name)
				# print("role:"+role)
				for s,a in db_session.query(Slot,Attender).filter(Slot.id==Attender.slot_id).filter(Attender.name==name).filter(Attender.role == role).order_by(Slot.date).order_by(Slot.start).all() :
					results.append(s.serializer)
				return jsonify(results)
			elif (len(name) > 0 and len(role) > 0) and special=='pointage' :
				aAttender= Attender(name=name,role=role)
				for s,a in db_session.query(Slot,Attender).filter(Slot.id==Attender.slot_id).filter(Attender.name==name).filter(Attender.role == role).filter(Slot.date <= date.today()).order_by(Slot.date).order_by(Slot.start).all() :
					results.append(s.serializer)
				return jsonify(results)

		return jsonify({'msg':'bad request'}),400
	except Exception as e :
		traceback.print_tb(sys.exc_info()[2])
		return jsonify({'msg':'error '+str(e)+str(e.args)}),400

@app.route('/attender/search', methods=['GET'])
@login_required
def attendersearch():
	try :
		role = request.args.get('role', '')
		slottype_name = request.args.get('slottype_name', '')
		results = []
		if len(role)!=0 and len(slottype_name) !=0:
			for u,p,r in db_session.query(User, Profile, RolesOnSlottypes).filter(User.profile_id==Profile.id).filter(RolesOnSlottypes.profile_id==Profile.id).filter(RolesOnSlottypes.role == role).filter(RolesOnSlottypes.slottype_name == slottype_name).order_by(User.name).all() :
				# print ("u"+str(u.serializer))
				results.append(u.serializer)
			return jsonify({'listofname':results})
		return jsonify({'msg':'bad request'}),400
	except Exception as e :
		traceback.print_tb(sys.exc_info()[2])
		return jsonify({'msg':'error '+str(e)+str(e.args)}),400

@app.route('/clocking', methods=['GET'])
@login_required
def clocking():
	return render_template('clocking.html',name=session['name'],profile="unknown",error=None)

@app.route('/summary', methods=['GET'])
@login_required
def summary():
	return render_template('summary.html',name=session['name'],profile="unknown")

@app.route('/summary/search', methods=['GET'])
@login_required
def summarysearch():
	try :
		rows=db_session.execute("""
		select name,
		       SUM(participationDone) as participationDone,
		       SUM(participationPlaned) as participationPlaned
		from
		  (select ns1.name as name,
		          count(id) as participationDone,
		          0 as participationPlaned
		   from
		     (select attenders.name as name,
		             slots.id as id
		      from attenders
		      inner join slots on slots.id=attenders.slot_id
		      and slots.date <= NOW()::date
		      order by attenders.name asc) as ns1
		   group by name
		   union select ns2.name as name,
		                0 as participationDone,
		                count(id) as participationPlaned
		   from
		     (select attenders.name as name,
		             slots.id as id
		      from attenders
		      inner join slots on slots.id=attenders.slot_id
		      and slots.date > NOW()::date
		      order by attenders.name asc) as ns2
		   group by name) as alldata
		group by name
		order by name asc
		""")

		entries = [];
		total_entries = 0
		for row in rows :
			entries.append({'name':row[0],'participationDone':int(row[1]),'participationPlaned':int(row[2])})
			total_entries =+ 1

		total_pages = int(total_entries/10)
		if (total_pages - (total_entries/10)) != 0 :
			total_pages =+ 1
		meta={"per_page": 10, "total_entries": total_entries, "total_pages": total_pages, "page": 1}
		print("{0!s}".format(entries))
		return jsonify([meta,entries])
	except Exception as e :
		traceback.print_tb(sys.exc_info()[2])
		return jsonify({'msg':'error '+str(e)+str(e.args)}),400

@app.route('/log', methods=['GET'])
@login_required
def log():
	return render_template('log.html',name=session['name'],profile="unknown")

@app.route('/log/search', methods=['GET'])
@login_required
def logsearch():
	try :
		entries = [];
		# total_entries = 0
		for log in db_session.query(Log).order_by(Log.when.desc()).all() :
			entries.append(log.todisplay)
			# total_entries =+ 1
		total_entries = db_session.query(Log).count()
		total_pages = int(total_entries/10)
		if (total_pages - (total_entries/10)) != 0 :
			total_pages =+ 1
		meta={"per_page": 10, "total_entries": total_entries, "total_pages": total_pages, "page": 1}
		return jsonify([meta,entries])

	except Exception as e :
		traceback.print_tb(sys.exc_info()[2])
		return jsonify({'msg':'error '+str(e)+str(e.args)}),400

@app.route('/profile', methods=['GET'])
@login_required
def profile():
	if 'user_id' in session :
		curentUser = db_session.query(User).filter_by(id=session['user_id']).first()
		return render_template('profile.html',name=curentUser.name,profile="{0!s}".format(curentUser.profile),error=None)
	else :
		return render_template('profile.html',name="unknown",profile="unknown",error="Unexpected error")

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	session.pop('user_id', None)
	flash('You were logged out')
	return redirect(url_for('login'))

@app.route('/toto1', methods=['GET'])
@login_required
def toto1():
	return render_template('clocking1.html',name=session['name'],error=None)

@app.route('/toto2', methods=['GET'])
@login_required
def toto2():
	return render_template('clocking2.html',name=session['name'],error=None)

@app.route('/toto3', methods=['GET'])
@login_required
def toto3():
	return render_template('clocking3.html',name=session['name'],error=None)

@app.teardown_appcontext
def teardown_db(exception=None):
	pass
