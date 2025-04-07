import mysql.connector
import json

class DbController:
    def __init__(self, host=None, user=None, password=None, database=None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        
    def connect(self):
        if self.host and self.user and self.password and self.database:
            self.mydb = mysql.connector.connect(
                host = self.host,
                user = self.user,
                password = self.password,
                port = 3306,
                database = self.database
            )
        else:
            print("Failed connection")
            
    def close(self):
        if self.mydb:
            self.mydb.close()
            
    def setCursor(self, buffered=None):
        if not buffered == None:
            self.myCursor = self.mydb.cursor()
        else:
            self.myCursor = self.mydb.cursor(buffered=buffered)
        
    def getData(self, query):
        if self.myCursor:
            self.myCursor.execute(query)
            return self.myCursor.fetchall()
    