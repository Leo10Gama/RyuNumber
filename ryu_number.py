import game
import game_character
import maintenance
import mysql.connector
import queries
import random

# Will return an array of the pattern Character-Game-Character-Game-... where the last element will always be Ryu
def getPathFromCharacter(name):
    # Connect to the db
    dbCreds = open("db.txt", "r").read().splitlines()
    mydb = mysql.connector.connect(
        host        =dbCreds[0],
        user        =dbCreds[1],
        password    =dbCreds[2],
        database    =dbCreds[3]
    )
    cursor = mydb.cursor()
    # Get our first character
    path = []
    try:
        path.append(game_character.getByName(name)[0])
        if name == "Ryu": return path
        while (path[-1].name != "Ryu"):
            cursor.execute(queries.getGameFromCharacter(path[-1].name))
            myGame = random.choice(cursor.fetchall())
            path.append(game.getByTitleExact(myGame[0]))
            cursor.execute(queries.getCharacterFromGame(path[-1].title))
            myCharacter = random.choice(cursor.fetchall())
            path.append(game_character.getByNameExact(myCharacter[0]))
        return path
    except:
        return None