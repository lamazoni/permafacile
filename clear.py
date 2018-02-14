# from database import init_db
#
# init_db()

#from database import db_session
from sys import exit
from database import connection
try :
	rows=connection.execute("""
	drop table if exists rolesonslotypes;
	drop table if exists users ;
	drop table if exists profiles ;
	drop table if exists attenders ;
	drop table if exists slots ;
	drop table if exists slottypes ;
	drop table if exists logs ;
	""");
except Exception as e :
	print("error,cannot clean")
	print(str(e)+str(e.args))
	exit(1)

connection.close()
