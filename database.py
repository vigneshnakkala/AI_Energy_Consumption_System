import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vignesh@2368",
    database="flask_app",
    auth_plugin="mysql_native_password"
)

mycursor = mydb.cursor()

def executionquery(query, values=None):
    mycursor.execute(query, values)
    mydb.commit()

def retrivequery1(query, values=None):
    mycursor.execute(query, values)
    return mycursor.fetchall()

def retrivequery2(query):
    mycursor.execute(query)
    return mycursor.fetchall()
