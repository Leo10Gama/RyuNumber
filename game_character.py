import mysql.connector
import queries
import game

class game_character:
    def __init__ (self, name, ryu_number, appears_in = []):
        self.name, self.ryu_number = name, ryu_number
        if appears_in:
            self.appears_in = appears_in
        else:
            self.appears_in = []
    def __str__ (self):
        returnStr = "(%d) %s\n" % (self.ryu_number, self.name)
        for g in self.appears_in:
            returnStr += "\t%s\n" % g
        return returnStr
    def printSelf(self, limit=-1):
        if limit == -1: limit = len(self.appears_in)
        if limit < 0: limit = 0
        returnStr = "(%d) %s\n" % (self.ryu_number, self.name)
        for i in range(min(limit, len(self.appears_in))):
            returnStr += "\t%s\n" % self.appears_in[i]
        if limit < len(self.appears_in):
            returnStr += "\t... and %d more" % (len(self.appears_in) - limit)
        return returnStr

class game_character_simple:
    def __init__ (self, name, ryu_number):
        self.name, self.ryu_number = name, ryu_number
    def __str__ (self):
        return "(%d) %s\n" % (self.ryu_number, self.name)


def insertCharacter(name):
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
    cursor.execute(queries.insertCharacter(name))
    mydb.commit()
    mydb.close()
    return True


def insertCharactersToGame(names, title):
    names = list(names)
    # Connect to the db
    dbCreds = open("db.txt", "r").read().splitlines()
    mydb = mysql.connector.connect(
        host        =dbCreds[0],
        user        =dbCreds[1],
        password    =dbCreds[2],
        database    =dbCreds[3]
    )
    cursor = mydb.cursor()

    # Run the commands
    for n in names:
        cursor.execute(queries.insertCharacter(n))
        cursor.execute(queries.insertRelation(n, title))
    mydb.commit()
    mydb.close()
    return True
    

def getByName(name):
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
    cursor.execute(queries.getCharacterByName(str(name)))
    for row in cursor.fetchall():
        result.append(game_character(row[0], row[1]))
    # Get games character is in as well
    for c in result:
        cursor.execute(queries.getGamesByCharacter(str(c.name)))
        for row in cursor.fetchall():
            c.appears_in.append(game.game(row[0], row[1], row[2]))
    return result


def getByNameExact(name):
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
    cursor.execute(queries.getCharacterByNameExact(str(name)))
    for row in cursor.fetchall():
        result = game_character(row[0], row[1])
    # Get games character is in as well
    if result:
        cursor.execute(queries.getGamesByCharacter(str(result.name)))
        for row in cursor.fetchall():
            result.appears_in.append(game.game(row[0], row[1], row[2]))
    return result


def getManyByNames(names):
    # Make sure the passed value is a tuple
    if not isinstance(names, tuple):
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
    cursor.execute(queries.getCharactersByNames(str(names)))
    for row in cursor.fetchall():
        result.append(game_character(row[0], row[1]))
    # Get the games characters are in as well
    for c in result:
        cursor.execute(queries.getGamesByCharacter(str(c.name)))
        for row in cursor.fetchall():
            c.appears_in.append(game.game(row[0], row[1], row[2]))
    return result


def getCharactersByGame(title):
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
    cursor.execute(queries.getCharactersByGame(str(title)))
    for row in cursor.fetchall():
        result.append(game_character(row[0], row[1]))
    # Get the games characters are in as well
    for c in result:
        cursor.execute(queries.getGamesByCharacter(str(c.name)))
        for row in cursor.fetchall():
            c.appears_in.append(game.game(row[0], row[1], row[2]))
    return result


def getCharactersByRyuNumber(rn):
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
    cursor.execute(queries.getCharacterByRyu(int(rn)))
    for row in cursor.fetchall():
        result.append(game_character(row[0], row[1]))
    # Get the games characters are in as well
    for c in result:
        cursor.execute(queries.getGamesByCharacter(str(c.name)))
        for row in cursor.fetchall():
            c.appears_in.append(game.game(row[0], row[1], row[2]))
    return result


def main():
    print(insertCharactersToGame(("Sonic", "Mario"), "Smash Bros"))

if __name__=="__main__":
    main()
