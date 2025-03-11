from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

mongo = PyMongo()  # Initialize PyMongo instance
cors = CORS()
sql = SQLAlchemy()