from typing import Optional, List, Tuple
from random import choice

from classes.nodes import Node, game, game_character, tupleToGame, tupleToCharacter
from classes.ryu_connector import RyuConnector
from methods import queries


default_error = lambda e: f"Error: {e}" # The default error message, which simply prints the passed Exception


#============================#
# CHARACTER DATABASE METHODS #
#============================#
# INSERT
def insertCharacter(name):
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.insertCharacter(name))
            return True
    except Exception as e:
        print(default_error(e))
        return False

def insertCharactersToGame(names: List[str], title):
    try:
        with RyuConnector() as rdb:
            for n in names:
                rdb.execute(queries.insertCharacter(n))
                rdb.execute(queries.insertRelation(n, title))
            return True
    except Exception as e:
        print(default_error(e))
        return False

# REMOVE
def removeCharacter(name):
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.removeCharacter(name))
            return True
    except Exception as e:
        print(default_error(e))
        return False

def removeCharacterFromGame(name, title):
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.removeRelation(name, title))
            return True
    except Exception as e:
        print(default_error(e))
        return False

# RETRIEVE
def getCharacterByName(name):
    result = None
    try:
        with RyuConnector() as rdb:
            # Get the character
            rdb.execute(queries.getCharacterByName(name))
            for row in rdb.fetchall():
                result = game_character(row[0], row[1])
            # Get games character is in as well
            if result:
                rdb.execute(queries.getGamesByCharacter(str(result.name)))
                mygames = rdb.fetchall()
                for row in mygames:
                    result.appears_in.append(row[0])
            return result
    except Exception as e:
        print(default_error(e))
        return None

def getCharactersLikeName(name):
    result = []
    try:
        with RyuConnector() as rdb:
            # Get the character(s)
            rdb.execute(queries.getCharacterLikeName(name))
            for row in rdb.fetchall():
                result.append(game_character(row[0], row[1]))
            # Get games character is in as well
            for c in result:
                rdb.execute(queries.getGamesByCharacter(str(c.name)))
                for row in rdb.fetchall():
                    c.appears_in.append(row[0])
            return result
    except Exception as e:
        print(default_error(e))
        return []

def getCharactersByNames(names: Tuple[str]):
    result = []
    try:
        with RyuConnector() as rdb:
            # Get the characters
            rdb.execute(queries.getCharactersByNames(names))
            for row in rdb.fetchall():
                result.append(game_character(row[0], row[1]))
            # Get the games that the characters are in as well
            for c in result:
                rdb.execute(queries.getGamesByCharacter(c.name))
                for row in rdb.fetchall():
                    c.appears_in.append(row[0])
            return result
    except Exception as e:
        print(default_error(e))
        return []

def getCharactersByGame(title):
    result = []
    try:
        with RyuConnector() as rdb:
            # Get the characters
            rdb.execute(queries.getCharactersByGame(title))
            for row in rdb.fetchall():
                result.append(game_character(row[0], row[1]))
            # Get the games that the characters are in as well
            for c in result:
                rdb.execute(queries.getGamesByCharacter(c.name))
                for row in rdb.fetchall():
                    c.appears_in.append(row[0])
            return result
    except Exception as e:
        print(default_error(e))
        return []

def getCharactersByRyuNumber(rn):
    result = []
    try:
        with RyuConnector() as rdb:
            # Get the characters
            rdb.execute(queries.getCharacterByRyu(int(rn)))
            for row in rdb.fetchall():
                result.append(game_character(row[0], row[1]))
            # Get the games that the characters are in as well
            for c in result:
                rdb.execute(queries.getGamesByCharacter(c.name))
                for row in rdb.fetchall():
                    c.appears_in.append(row[0])
            return result
    except Exception as e:
        print(default_error(e))
        return []

def getNumCharacters():
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getNumCharacters)
            for row in rdb.fetchall():
                return int(row[0])
    except Exception as e:
        print(default_error(e))
        return None

def getNumCharactersWithRN(rn):
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getNumCharactersWithRN(rn))
            for row in rdb.fetchall():
                return int(row[0])
    except Exception as e:
        print(default_error(e))
        return None

# UPDATE
def updateCharacterName(oldName, newName):
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.updateCharacterName(oldName, newName))
            return True
    except Exception as e:
        print(default_error(e))
        return False


#=======================#
# GAME DATABASE METHODS #
#=======================#
# INSERT
def insertGame(title, release_date="0000-00-00"):
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.insertGame(title, release_date))
            return True
    except Exception as e:
        print(default_error(e))
        return False

# REMOVE
def removeGame(title):
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.removeGame(title))
            return True
    except Exception as e:
        print(default_error(e))
        return False

# RETRIEVE
def getGameByTitle(title):
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getGameByTitle(title))
            for row in rdb:
                return game(row[0], row[1], row[2])
            return None
    except Exception as e:
        print(default_error(e))
        return None

def getGamesLikeTitle(title):
    result = []
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getGameLikeTitle(title))
            for row in rdb.fetchall():
                result.append(game(row[0], row[1], row[2]))
            return result
    except Exception as e:
        print(default_error(e))
        return []

def getGamesByTitles(titles: Tuple[str]):
    result = []
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getGamesByTitles(titles))
            for row in rdb.fetchall():
                result.append(game(row[0], row[1], row[2]))
            return result
    except Exception as e:
        print(default_error(e))
        return []

def getGamesByCharacter(name):
    result = []
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getGamesByCharacter(name))
            for row in rdb.fetchall():
                result.append(game(row[0], row[1], row[2]))
            return result
    except Exception as e:
        print(default_error(e))
        return []

def getGamesByRyuNumber(rn):
    result = []
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getGamesByRyu(rn))
            for row in rdb.fetchall():
                result.append(game(row[0], row[1], row[2]))
            return result
    except Exception as e:
        print(default_error(e))
        return []

def getNumGames():
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getNumGames)
            for row in rdb.fetchall():
                return int(row[0])
    except Exception as e:
        print(default_error(e))
        return None

def getNumGamesWithRN(rn):
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getNumGamesWithRN(rn))
            for row in rdb.fetchall():
                return int(row[0])
    except Exception as e:
        print(default_error(e))
        return None

# UPDATE
def updateGameTitle(oldTitle, newTitle):
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.updateGameTitle(oldTitle, newTitle))
            return True
    except Exception as e:
        print(default_error(e))
        return False

def updateGameReleaseDate(title, release_date):
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.updateGameReleaseDate(title, release_date))
            return True
    except Exception as e:
        print(default_error(e))
        return False


#====================#
# RYU NUMBER METHODS #
#====================#
# Gets one step of the path
def stepTowardsRyu(item: Node) -> Optional[List[Node]]:
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
def getPathFromCharacter(name: str) -> List[Node]:
    # Get our first character
    path: List[Node] = []
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