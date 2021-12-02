from random import choice

from game import game, tupleToGame
from game_character import game_character, tupleToCharacter
from ryu_connector import RyuConnector
import queries

# Gets one step of the path
def stepTowardsRyu(item):
    with RyuConnector() as rdb:
        if type(item) is game:
            # We're looking for the next character down (RN = this - 1)
            rdb.execute(queries.getCharacterFromGame(item.title))
            cs = rdb.fetchall()
            chars = []
            for c in cs:
                chars.append(c[0])
            return chars
        elif type(item) is game_character:
            # Base case
            if item.name == "Ryu": return None
            # We're looking for the next game down (RN = this)
            rdb.execute(queries.getGameFromCharacter(item.name))
            gs = rdb.fetchall()
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
        with RyuConnector() as rdb:
            rdb.execute(queries.getCharacterByName(name))
            c = tupleToCharacter(rdb.fetchone())
            path.append(c)
            if name == "Ryu": return path
            x = c
            while (path[-1].name != "Ryu"):
                rdb.execute(queries.getGameByTitle(choice(stepTowardsRyu(x))))
                g = rdb.fetchone()
                path.append(tupleToGame(g))
                x = path[-1]
                rdb.execute(queries.getCharacterByName(choice(stepTowardsRyu(x))))
                c = rdb.fetchone()
                path.append(tupleToCharacter(c))
                x = path[-1]
            return path
    except:
        return None