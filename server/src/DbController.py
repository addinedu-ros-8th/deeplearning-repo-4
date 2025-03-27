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
        
def main():
    dbCon = DbController("localhost", "root", "5315", "mysql")
    dbCon.connect()
    dbCon.setCursor(True)
    
    dbCon.myCursor.execute("DELETE FROM mysql.db WHERE User='readonly_user';")
    dbCon.mydb.commit()
    dbCon.myCursor.execute("DELETE FROM mysql.user WHERE User='readonly_user';")
    dbCon.mydb.commit()
    dbCon.myCursor.execute("DELETE FROM mysql.proxies_priv WHERE User='readonly_user';")
    dbCon.mydb.commit()
    dbCon.myCursor.execute("FLUSH PRIVILEGES;")
    dbCon.myCursor.execute(f"Create user 'readonly_user'@'192.168.0.153' identified by '0000'")
    dbCon.mydb.commit()
    dbCon.myCursor.execute(f"GRANT SELECT ON tfdb.* TO 'readonly_user'@'192.168.0.147';")
    dbCon.mydb.commit()
    dbCon.myCursor.execute("FLUSH PRIVILEGES;")
    dbCon.close()
    
if __name__ == "__main__":
    main()
    