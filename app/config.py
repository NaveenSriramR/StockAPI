import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STOCK_API_KEY = os.getenv('STOCK_API_KEY', 'T9PY2F9AFERMO5XH')
    API_URL = os.getenv('API_URL', 'https://www.alphavantage.co/query?')
