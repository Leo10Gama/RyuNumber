import mysql.connector
import queries

class game:
    def __init__ (self, title, ryu_number, release_date):
        self.title, self.ryu_number, self.release_date = title, ryu_number, release_date
    def __str__ (self):
        return str(self.__dict__)


def insertGame(title, release_date):
    # Connect to the db
    dbCreds = open("db.txt", "r").read().splitlines()
    mydb = mysql.connector.connect(
        host        =dbCreds[0],
        user        =dbCreds[1],
        password    =dbCreds[2],
        database    =dbCreds[3]
    )
    cursor = mydb.cursor()

    # Run the command
    cursor.execute(queries.insertGame(title, release_date))
    mydb.commit()
    mydb.close()
    return True


def getByTitle(title):
    # Connect to the db
    dbCreds = open("db.txt", "r").read().splitlines()
    mydb = mysql.connector.connect(
        host        =dbCreds[0],
        user        =dbCreds[1],
        password    =dbCreds[2],
        database    =dbCreds[3]
    )
    cursor = mydb.cursor()

    # Query and retrieve result
    result = None
    cursor.execute(queries.getGameByTitle(str(title)))
    for row in cursor.fetchall():
        result = game(row[0], row[1], row[2])
    return result


def getManyByTitles(titles):
    # Make sure the passed value is a tuple
    if not isinstance(titles, tuple):
        return "Error: passed value is not a tuple"
    # Connect to the db
    dbCreds = open("db.txt", "r").read().splitlines()
    mydb = mysql.connector.connect(
        host        =dbCreds[0],
        user        =dbCreds[1],
        password    =dbCreds[2],
        database    =dbCreds[3]
    )
    cursor = mydb.cursor()

    # Query and retrieve results
    result = []
    cursor.execute(queries.getGamesByTitles(str(titles)))
    for row in cursor.fetchall():
        result.append(game(row[0], row[1], row[2]))
    return result


def getGamesByCharacter(name):
    # Connect to the db
    dbCreds = open("db.txt", "r").read().splitlines()
    mydb = mysql.connector.connect(
        host        =dbCreds[0],
        user        =dbCreds[1],
        password    =dbCreds[2],
        database    =dbCreds[3]
    )
    cursor = mydb.cursor()

    # Query and retrieve result
    result = []
    cursor.execute(queries.getGamesByCharacter(str(name)))
    for row in cursor.fetchall():
        result.append(game(row[0], row[1], row[2]))
    return result


def getGamesByRyuNumber(rn):
    # Connect to the db
    dbCreds = open("db.txt", "r").read().splitlines()
    mydb = mysql.connector.connect(
        host        =dbCreds[0],
        user        =dbCreds[1],
        password    =dbCreds[2],
        database    =dbCreds[3]
    )
    cursor = mydb.cursor()

    # Query and retrieve result
    result = []
    cursor.execute(queries.getGamesByRyu(int(rn)))
    for row in cursor.fetchall():
        result.append(game(row[0], row[1], row[2]))
    return result   
