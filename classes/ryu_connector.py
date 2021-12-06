"""Class containing the connection details to the database.

The single class found in this module encapsulates the connection to the
database in the form of a context manager.
"""

import mysql.connector

class RyuConnector:
    """A context manager that connects to the database (assuming it exists).
    
    This class can be used alongside the `with` keyword, and will return a
    cursor object that can execute queries, commands, and other database
    operations.
    """
    def __init__(self, credentials: str="db.txt") -> None:
        """Initialize the connection to the database.
        
        Parameters
        ----------
        credentials: str
            The name of the file which contains the database credential information.
            The assumed format is that there are four lines in the text file, which
            represent the host, user, password, and database names respectively.
        """
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

    def __exit__(self, type, value, traceback) -> None:
        self.mydb.commit()
        self.mydb.close()