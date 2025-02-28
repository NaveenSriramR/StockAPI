import os

xyz = 'abc'
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://naveen:dbpasscode@cluster0.faokq.mongodb.net/Findata?retryWrites=true&w=majority&appName=Cluster0')
    STOCK_API_KEY = os.getenv('STOCK_API_KEY', 'T9PY2F9AFERMO5XH')
    API_URL = os.getenv('API_URL', 'https://www.alphavantage.co/query?')
