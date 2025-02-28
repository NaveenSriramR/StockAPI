from flask_pymongo import PyMongo
from flask_cors import CORS


mongo = PyMongo()  # Initialize PyMongo instance
cors = CORS()