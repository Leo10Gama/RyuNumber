"""Module for employing queries in conjunction with actual objects.

There are methods employed for inserting, removing, retrieving, and
updating both characters and games. In addition, there are also methods
to retrieve paths from a given character towards Ryu, and its related
helper method.

All parameters of methods are named in such a way that they are either
self-explanatory, or relate directly to a given field of a table. 

Most methods takes a form similar to <action><object>[specification], 
where <action> can include (insert, remove, get, update), <object> can
include (Character, Game, etc.), and [specification] can be things such
as (FromGame, ByName, LikeTitle, etc.), with the exceptions of Ryu
Number methods.
"""

from typing import Optional, List, Tuple
from random import choice

from classes.nodes import Node, game, game_character
from classes.ryu_connector import RyuConnector
from methods import queries


ERROR_MESSAGES = {
    "default_error": lambda e: f"Error: {e}"    # The default error message, which simply prints the passed Exception
}


def sanitizeInput(data: str) -> str:
    """Return the data after being prepped for SQL insertion."""
    return data.replace("'", "''")

def tupleToCharacter(t: Tuple[str, int]) -> Optional[game_character]:
    """Return a game_character object directly related to a tuple.
    
    The anticipated tuple input is the result of a query for a character.
    That is, it is expected to be (name, ryu_number). If the passed tuple is
    invalid or errors occur during connection, nothing is returned.
    """
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getGamesByCharacter(sanitizeInput(t[0])))
            gamesList = rdb.fetchall()
            ai = []
            for g in gamesList:
                ai.append(g[0])
            return game_character(t[0], t[1], ai)
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def tupleToGame(t: Tuple[str, int, str]) -> Optional[game]:
    """Return a game object directly related to a tuple.
    
    The anticipated tuple input is the result of a query for a game.
    That is, it is expected to be (title, ryu_number, release_date). If the
    passed tuple is invalid, nothing is returned.
    """
    try:
        return game(t[0], t[1], t[2])
    except Exception as e:
        print(f"ERROR: {e}")
        return None

#============================#
# CHARACTER DATABASE METHODS #
#============================#
# INSERT
def insertCharacter(name: str) -> bool:
    """Insert a character to the database.
    
    The method will return a boolean value as to whether or not the 
    character has been successfully inserted.
    """
    try:
        with RyuConnector() as rdb:
            name = sanitizeInput(name)
            rdb.execute(queries.insertCharacter(name))
            return True
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return False

def insertCharactersToGame(names: List[str], title: str) -> bool:
    """Insert a list of characters into a game.
    
    The method will return a boolean value as to whether or not all
    characters have been successfully inserted.
    """
    try:
        with RyuConnector() as rdb:
            title = sanitizeInput(title)
            names = [sanitizeInput(n) for n in names]
            for n in names:
                rdb.execute(queries.insertCharacter(n))
                rdb.execute(queries.insertRelation(n, title))
            return True
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return False

# REMOVE
def removeCharacter(name: str) -> bool:
    """Remove a character from the database.
    
    The method will return a boolean value as to whether or not the
    character has been successfully removed.
    """
    try:
        with RyuConnector() as rdb:
            name = sanitizeInput(name)
            rdb.execute(queries.removeCharacter(name))
            return True
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return False

def removeCharacterFromGame(name: str, title: str) -> bool:
    """Remove a character's appears_in relation from a given game.
    
    The method will return a boolean value as to whether or not the
    relation has been successfully removed.
    """
    try:
        with RyuConnector() as rdb:
            name = sanitizeInput(name)
            title = sanitizeInput(title)
            rdb.execute(queries.removeRelation(name, title))
            return True
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return False

# RETRIEVE
def getCharacterByName(name: str) -> Optional[game_character]:
    """Get a character from the database using their name."""
    result: Optional[game_character] = None
    try:
        with RyuConnector() as rdb:
            # Get the character
            name = sanitizeInput(name)
            rdb.execute(queries.getCharacterByName(name))
            for row in rdb.fetchall():
                result = game_character(row[0], row[1])
            # Get games character is in as well
            if result:
                name = sanitizeInput(result.name)
                rdb.execute(queries.getGamesByCharacter(name))
                mygames = rdb.fetchall()
                for row in mygames:
                    result.appears_in.append(row[0])
            return result
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return None

def getCharactersLikeName(name: str) -> Optional[List[game_character]]:
    """Get characters from the database whose names are similar to the arg.
    
    Returns an empty array if no characters can be found, but returns None 
    if any sorts of errors occur.
    """
    result: List[game_character] = []
    try:
        with RyuConnector() as rdb:
            # Get the character(s)
            name = sanitizeInput(name)
            rdb.execute(queries.getCharacterLikeName(name))
            for row in rdb.fetchall():
                result.append(game_character(row[0], row[1]))
            # Get games character is in as well
            for c in result:
                name = sanitizeInput(c.name)
                rdb.execute(queries.getGamesByCharacter(name))
                for row in rdb.fetchall():
                    c.appears_in.append(row[0])
            return result
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return None

def getCharactersByNames(names: Tuple[str]) -> Optional[List[game_character]]:
    """Get characters from the database whose names are in the passed tuple.
    
    Returns an empty array if no characters can be found, but returns None
    if any sorts of errors occur.
    """
    result: List[game_character] = []
    try:
        with RyuConnector() as rdb:
            # Get the characters
            names = tuple(sanitizeInput(n) for n in names)
            rdb.execute(queries.getCharactersByNames(names))
            for row in rdb.fetchall():
                result.append(game_character(row[0], row[1]))
            # Get the games that the characters are in as well
            for c in result:
                name = sanitizeInput(c.name)
                rdb.execute(queries.getGamesByCharacter(name))
                for row in rdb.fetchall():
                    c.appears_in.append(row[0])
            return result
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return None

def getCharactersByGame(title: str) -> Optional[List[game_character]]:
    """Get a list of all characters who appear in a given game.
    
    Returns an empty array if no characters exist in the game, or if the
    game doesn't exist, and returns None if errors occur.
    """
    result: List[game_character] = []
    try:
        with RyuConnector() as rdb:
            # Get the characters
            title = sanitizeInput(title)
            rdb.execute(queries.getCharactersByGame(title))
            for row in rdb.fetchall():
                result.append(game_character(row[0], row[1]))
            # Get the games that the characters are in as well
            for c in result:
                name = sanitizeInput(c.name)
                rdb.execute(queries.getGamesByCharacter(name))
                for row in rdb.fetchall():
                    c.appears_in.append(row[0])
            return result
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return None

def getCharactersByRyuNumber(rn: int) -> Optional[List[game_character]]:
    """Get a list of all characters who have a given Ryu Number.
    
    Returns an empty array if no characters can be found, but returns None
    if any sorts of errors occur.
    """
    result: List[game_character] = []
    try:
        with RyuConnector() as rdb:
            # Get the characters
            rdb.execute(queries.getCharacterByRyu(int(rn)))
            for row in rdb.fetchall():
                result.append(game_character(row[0], row[1]))
            # Get the games that the characters are in as well
            for c in result:
                name = sanitizeInput(c.name)
                rdb.execute(queries.getGamesByCharacter(name))
                for row in rdb.fetchall():
                    c.appears_in.append(row[0])
            return result
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return None

def getNumCharacters() -> Optional[int]:
    """Get the total number of characters in the database."""
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getNumCharacters)
            for row in rdb.fetchall():
                return int(row[0])
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return None

def getNumCharactersWithRN(rn: int) -> Optional[int]:
    """Get the number of characters in the database with a given Ryu Number."""
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getNumCharactersWithRN(rn))
            for row in rdb.fetchall():
                return int(row[0])
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return None

# UPDATE
def updateCharacterName(oldName: str, newName: str) -> bool:
    """Update the name of a character in the database.
    
    The method will return a boolean value as to whether or not the
    character's name has been successfully updated.
    """
    try:
        with RyuConnector() as rdb:
            oldName = sanitizeInput(oldName)
            newName = sanitizeInput(newName)
            rdb.execute(queries.updateCharacterName(oldName, newName))
            return True
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return False


#=======================#
# GAME DATABASE METHODS #
#=======================#
# INSERT
def insertGame(title: str, release_date: str="0000-00-00") -> bool:
    """Insert a game to the database.
    
    The method will return a boolean value as to whether or not the
    game has been successfully inserted.
    """
    try:
        with RyuConnector() as rdb:
            title = sanitizeInput(title)
            rdb.execute(queries.insertGame(title, release_date))
            return True
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return False

# REMOVE
def removeGame(title: str) -> bool:
    """Remove a game from the database
    
    The method will return a boolean value as to whether or not the
    game has been successfully removed.
    """
    try:
        with RyuConnector() as rdb:
            title = sanitizeInput(title)
            rdb.execute(queries.removeGame(title))
            return True
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return False

# RETRIEVE
def getGameByTitle(title: str) -> Optional[game]:
    """Get a game from the database using its title."""
    try:
        with RyuConnector() as rdb:
            title = sanitizeInput(title)
            rdb.execute(queries.getGameByTitle(title))
            for row in rdb:
                return game(row[0], row[1], row[2])
            return None
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return None

def getGamesLikeTitle(title: str) -> Optional[List[game]]:
    """Get games from the database whose titles are similar to the arg.
    
    Returns an empty array if no games can be found, but returns None if any
    sorts of errors occur.
    """
    result: List[game] = []
    try:
        with RyuConnector() as rdb:
            title = sanitizeInput(title)
            rdb.execute(queries.getGameLikeTitle(title))
            for row in rdb.fetchall():
                result.append(game(row[0], row[1], row[2]))
            return result
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return None

def getGamesByTitles(titles: Tuple[str]) -> Optional[List[game]]:
    """Get games from the database whose titles are in the passed tuple.
    
    Returns an empty array if no games can be found, but returns None if any
    sorts of errors occur.
    """
    result: List[game] = []
    try:
        with RyuConnector() as rdb:
            titles = tuple(sanitizeInput(t) for t in titles)
            rdb.execute(queries.getGamesByTitles(titles))
            for row in rdb.fetchall():
                result.append(game(row[0], row[1], row[2]))
            return result
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return None

def getGamesByCharacter(name: str) -> Optional[List[game]]:
    """Get a list of all the games a given character appears in.
    
    Returns an empty array if the character does not exist in any games, and
    returns None if errors occur.
    """
    result: List[game] = []
    try:
        with RyuConnector() as rdb:
            name = sanitizeInput(name)
            rdb.execute(queries.getGamesByCharacter(name))
            for row in rdb.fetchall():
                result.append(game(row[0], row[1], row[2]))
            return result
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return None

def getGamesByRyuNumber(rn: int) -> Optional[List[game]]:
    """Get a list of all games that have a given Ryu Number.
    
    Returns an empty array if no games can be found, but returns None if any
    sorts of errors occur.
    """
    result: List[game] = []
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getGamesByRyu(rn))
            for row in rdb.fetchall():
                result.append(game(row[0], row[1], row[2]))
            return result
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return None

def getNumGames() -> Optional[int]:
    """Get the total number of games in the database."""
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getNumGames)
            for row in rdb.fetchall():
                return int(row[0])
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return None

def getNumGamesWithRN(rn: int) -> int:
    """Get the number of games in the database with a given Ryu Number."""
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getNumGamesWithRN(rn))
            for row in rdb.fetchall():
                return int(row[0])
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return None

# UPDATE
def updateGameTitle(oldTitle: str, newTitle: str) -> bool:
    """Update the title of a game in the database.
    
    The method will return a boolean value as to whether or not the
    game's title has been successfully updated.
    """
    try:
        with RyuConnector() as rdb:
            oldTitle = sanitizeInput(oldTitle)
            newTitle = sanitizeInput(newTitle)
            rdb.execute(queries.updateGameTitle(oldTitle, newTitle))
            return True
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return False

def updateGameReleaseDate(title: str, release_date: str) -> bool:
    """Update the release date of a game in the database.
    
    The method will return a boolean value as to whether or not the
    game's release date has been successfully updated.
    """
    try:
        with RyuConnector() as rdb:
            title = sanitizeInput(title)
            rdb.execute(queries.updateGameReleaseDate(title, release_date))
            return True
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return False


#====================#
# RYU NUMBER METHODS #
#====================#
def stepTowardsRyu(item: Node) -> Optional[List[Node]]:
    """Get one step of a path towards Ryu.
    
    If the passed item is a game, then a list of all characters with a Ryu 
    Number exactly one less than the game's is returned (if possible).
    If the passed item is a character, then a list of all games with a Ryu 
    Number exactly equal to the character's is returned (if possible).
    """
    with RyuConnector() as rdb:
        if type(item) is game:
            # We're looking for the next character down (RN = this - 1)
            rdb.execute(queries.getCharacterFromGame(sanitizeInput(item.primary_key)))
            cs = rdb.fetchall()
            chars: List[str] = []
            for c in cs:
                chars.append(c[0])
            return chars
        elif type(item) is game_character:
            # Base case
            if item.primary_key == "Ryu": return None
            # We're looking for the next game down (RN = this)
            rdb.execute(queries.getGameFromCharacter(sanitizeInput(item.primary_key)))
            gs = rdb.fetchall()
            games: List[str] = []
            for g in gs:
                games.append(g[0])
            return games
        else:
            # Something got borked
            return None

def getPathFromCharacter(name: str) -> Optional[List[Node]]:
    """Get a list of characters and games, including the passed one, to Ryu.
    
    The method repeatedly calls the above `stepTowardsRyu()`, looping the
    given character with games they appear in, and the characters in that
    game, until Ryu (whose Ryu Number is 0) is reached.

    The returned list is in alternating form of the pattern Character-Game-
    Character-Game-...-Ryu. The length of the list is dependent on the Ryu
    Number of the character queried. For a queried character with a Ryu
    Number of `n`, the list will be of size `2n+1`.
    """
    # Get our first character
    path: List[Node] = []
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getCharacterByName(sanitizeInput(name)))
            c: game_character = tupleToCharacter(rdb.fetchone())
            path.append(c)
            if name == "Ryu": return path
            x: Node = c
            while (path[-1].ryu_number != 0):
                rdb.execute(queries.getGameByTitle(choice(stepTowardsRyu(x))))
                g = rdb.fetchone()
                path.append(tupleToGame(g))
                x = path[-1]
                rdb.execute(queries.getCharacterByName(choice(stepTowardsRyu(x))))
                c = rdb.fetchone()
                path.append(tupleToCharacter(c))
                x = path[-1]
            return path
    except Exception as e:
        print(ERROR_MESSAGES["default_error"](e))
        return None