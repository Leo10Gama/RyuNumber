import game
import game_character
import maintenance
import mysql.connector
import queries
import random

# Gets one step of the path
def stepTowardsRyu(item):
    # Connect to the db
    dbCreds = open("db.txt", "r").read().splitlines()
    mydb = mysql.connector.connect(
        host        =dbCreds[0],
        user        =dbCreds[1],
        password    =dbCreds[2],
        database    =dbCreds[3]
    )
    cursor = mydb.cursor()
    # Check what we're doing
    if type(item) is game.game:
        # We're looking for the next character down (RN = this - 1)
        cursor.execute(queries.getCharacterFromGame(item.title))
        cs = cursor.fetchall()
        chars = []
        for c in cs:
            chars.append(c[0])
        return chars
    elif type(item) is game_character.game_character:
        # Base case
        if item.name == "Ryu": return None
        # We're looking for the next game down (RN = this)
        cursor.execute(queries.getGameFromCharacter(item.name))
        gs = cursor.fetchall()
        games = []
        for g in gs:
            games.append(g[0])
        return games
    else:
        # Something got borked
        return None


# Will return an array of the pattern Character-Game-Character-Game-... where the last element will always be Ryu
def getPathFromCharacter(name):
    # Get our first character
    path = []
    try:
        c = game_character.getByNameExact(name)
        path.append(c)
        if name == "Ryu": return path
        x = c
        while (path[-1].name != "Ryu"):
            path.append(game.getByTitleExact(random.choice(stepTowardsRyu(x))))
            x = path[-1]
            path.append(game_character.getByNameExact(random.choice(stepTowardsRyu(x))))
            x = path[-1]
        return path
    except:
        return None