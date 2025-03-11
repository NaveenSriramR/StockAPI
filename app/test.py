# from extensions import mongo
# print(mongo.db)
import mysql.connector
print("hi")
sql = mysql.connector.connect(host='localhost',user = 'root',password='dbpassword')
cursor = sql.cursor()
cursor.execute('CREATE DATABASE findata;') 
print(cursor.execute('SHOW DATABASES;'))