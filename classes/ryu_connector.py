import mysql.connector

class RyuConnector:

    def __init__(self, credentials="db.txt"):
        self.dbCreds = open(credentials, "r").read().splitlines()
        self.mydb = mysql.connector.connect(
            host        =self.dbCreds[0],
            user        =self.dbCreds[1],
            password    =self.dbCreds[2],
            database    =self.dbCreds[3]
        )
        self.cursor = self.mydb.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, type, value, traceback):
        self.mydb.commit()
        self.mydb.close()