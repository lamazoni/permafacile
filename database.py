from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from _config import *

path = SQLALCHEMY_DATABASE_URI
engine = create_engine(path, convert_unicode=True,pool_pre_ping=True)
session_factory = sessionmaker(autocommit=False,autoflush=False,bind=engine)


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
	import models
	models.Base.metadata.create_all(bind=engine)
