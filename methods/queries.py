"""Module for storing query strings for interacting with the database.

All methods within the class return a string that, when executed as an
SQL query, perform the task specified by the method signature and
docstring.

All method parameters will relate either directly to a field in the
database, or be self-explanatory. For those that are not self-
explanatory, refer to them below:

cname -- The `name` field of either the `game_character` table, or the
         `cname` field of the `appears_in` table.
gtitle -- The `title` field of either the `game` table, or the `gtitle`
          field of the `appears_in` table.
rn -- The `ryu_number` of either the `game` or `game_character` table.

Each method takes the form of <action><object>[specifications], where
<action> includes (insert, get, remove, update), <object> includes
(Character, Game, Relation, etc.), and specifications are things like 
(ByName, ByGame, ByRyu, etc.).
"""

from typing import Tuple


ALL_GAME_CHARACTER = "name, ryu_number"
ALL_GAME = "title, ryu_number, release_date"
ALL_APPEARS_IN = "cname, gtitle"

def sanitizeInput(data: str) -> str:
    """Return the data after being prepped for SQL insertion.
    
    This allows for data to be entered with apostrophes, which would 
    ordinarily allow for incorrect syntax or code injection.
    """
    return data.replace("'", "''")

#===================#
# CHARACTER QUERIES #
#===================#
def insertCharacter(cname: str) -> str: 
    """Return a query to insert a character into the database."""
    return (f"INSERT IGNORE INTO game_character (name) "
            f"VALUES ('{sanitizeInput(cname)}');"
    )

def getCharacterLikeName(cname: str) -> str: 
    """Return a query to get a character whose name resembles the passed arg.
    
    The resulting tuple gets fields from, and in order of 
    `ALL_GAME_CHARACTER`.
    """
    return (f"SELECT {ALL_GAME_CHARACTER} "
            f"FROM game_character "
            f"WHERE name LIKE '%{sanitizeInput(cname)}%' "
            f"ORDER BY ryu_number ASC, name ASC;"
    )

def getCharacterByName(cname: str) -> str: 
    """Return a query to retrieve a character in the database.
    
    The resulting tuple gets fields from, and in order of 
    `ALL_GAME_CHARACTER`.
    """
    return (f"SELECT {ALL_GAME_CHARACTER} "
            f"FROM game_character "
            f"WHERE name='{sanitizeInput(cname)}';"
    )

def getCharactersByNames(cnames: Tuple) -> str: 
    """Return a query to retrieve multiple characters in the database.
    
    The resulting tuple gets fields from, and in order of 
    `ALL_GAME_CHARACTER`.
    """
    return (f"SELECT {ALL_GAME_CHARACTER} "
            f"FROM game_character "
            f"WHERE name IN {tuple(sanitizeInput(name) for name in cnames)} "
            f"ORDER BY ryu_number ASC;"
    )

def getCharactersByGame(gtitle: str) -> str: 
    """Return a query to retrieve all characters who appear in the given game.

    The resulting tuple gets fields from, and in order of 
    `ALL_GAME_CHARACTER`.
    """
    return (f"SELECT {ALL_GAME_CHARACTER} "
            f"FROM game_character, appears_in "
            f"WHERE appears_in.cname=game_character.name AND appears_in.gtitle='{sanitizeInput(gtitle)}';"
    )

def getCharacterByRyu(rn: int) -> str: 
    """Return a query to get all characters who have the given Ryu Number.
    
    The resulting tuple gets fields from, and in order of 
    `ALL_GAME_CHARACTER`.
    """
    return (f"SELECT {ALL_GAME_CHARACTER} "
            f"FROM game_character "
            f"WHERE ryu_number={rn};"
    )

def removeCharacter(cname: str) -> str: 
    """Return a query to remove a given character from the database."""
    return (f"DELETE FROM game_character "
            f"WHERE name='{sanitizeInput(cname)}';"
    )

def updateCharacterName(old_name: str, new_name: str) -> str: 
    """Return a query to update a given character's name."""
    return (f"UPDATE game_character "
            f"SET name='{sanitizeInput(new_name)}' "
            f"WHERE name='{sanitizeInput(old_name)}';"
    )

def getNumCharacters() -> str:
    """Return a query to retrieve the count of all characters in the database.
    
    The resulting tuple is of the form: `(COUNT(*): int,)`
    """
    return f"SELECT COUNT(*) FROM game_character;"


#==============#
# GAME QUERIES #
#==============#
def insertGame(gtitle: str, release_date: str="0000-00-00") -> str: 
    """Return a query to insert a game into the database."""
    return (f"INSERT IGNORE INTO game (title, release_date) "
            f"VALUES ('{sanitizeInput(gtitle)}', '{release_date}');"
    )

def getGameLikeTitle(gtitle: str) -> str: 
    """Return a query to get games whose titles are similar to the passed arg.
    
    The resulting tuple gets fields from, and in order of `ALL_GAME`.
    """
    return (f"SELECT {ALL_GAME} "
            f"FROM game "
            f"WHERE title LIKE '%{sanitizeInput(gtitle)}%' "
            f"ORDER BY release_date ASC, ryu_number ASC;"
    )

def getGameByTitle(gtitle: str) -> str: 
    """Return a query to get a specific game from the database.

    The resulting tuple gets fields from, and in order of `ALL_GAME`.
    """
    return (f"SELECT {ALL_GAME} "
            f"FROM game "
            f"WHERE title='{gtitle}';"
    )

def getGamesByTitles(gtitles: Tuple) -> str: 
    """Return a query to get games from a given tuple of titles.
    
    The resulting tuple gets fields from, and in order of `ALL_GAME`.
    """
    return (f"SELECT {ALL_GAME} "
            f"FROM game "
            f"WHERE title IN {tuple(sanitizeInput(title) for title in gtitles)} "
            f"ORDER BY ryu_number ASC;"
    )

def getGamesByCharacter(cname: str) -> str: 
    """Return a query to get all the games a given character appears in.
    
    The resulting tuple gets fields from, and in order of `ALL_GAME`.
    """
    return (f"SELECT {ALL_GAME} "
            f"FROM appears_in, game "
            f"WHERE appears_in.cname='{sanitizeInput(cname)}' AND appears_in.gtitle=game.title "
            f"ORDER BY release_date ASC;"
    )

def getGamesByRyu(rn: int) -> str: 
    """Return a query to get all games with a given Ryu Number.
    
    The resulting tuple gets fields from, and in order of `ALL_GAME`.
    """
    return (f"SELECT {ALL_GAME} "
            f"FROM game "
            f"WHERE ryu_number={rn};"
    )

def removeGame(gtitle: str) -> str: 
    """Return a query to remove a given game from the database."""
    return (f"DELETE FROM game "
            f"WHERE title='{sanitizeInput(gtitle)}';"
    )

def updateGameTitle(old_title: str, new_title: str) -> str: 
    """Return a query to update the title of a given game."""
    return (f"UPDATE game "
            f"SET title='{sanitizeInput(new_title)}' "
            f"WHERE title='{sanitizeInput(old_title)}';"
    )

def updateGameReleaseDate(gtitle: str, new_rdate: str) -> str: 
    """Return a query to update the release date of a given game."""
    return (f"UPDATE game "
            f"SET release_date='{new_rdate}' "
            f"WHERE title='{sanitizeInput(gtitle)}';"
    )

def getNumGames() -> str:
    """Return a query to retrieve the count of all games in the database.
    
    The resulting tuple is of the form: `(COUNT(*): int,)`
    """
    return "SELECT COUNT(*) FROM game;"


#==================#
# RELATION QUERIES #
#==================#
def insertRelation(cname: str, gtitle: str) -> str: 
    """Return a query to insert an `appears_in` relation to the database."""
    return (f"INSERT IGNORE INTO appears_in (cname, gtitle) "
            f"VALUES ('{sanitizeInput(cname)}', '{sanitizeInput(gtitle)}');"
    )

def getRelationsByCharacter(cname: str) -> str: 
    """Return a query to get all relations for a given character.
    
    The resulting tuple gets fields from, and in order of 
    `ALL_APPEARS_IN`.
    """
    return (f"SELECT {ALL_APPEARS_IN} "
            f"FROM appears_in "
            f"WHERE cname='{sanitizeInput(cname)}';"
    )

def getRelationsByGame(gtitle: str) -> str: 
    """Return a query to get all relations for a given game.
    
    The resulting tuple gets fields from, and in order of 
    `ALL_APPEARS_IN`.
    """
    return (f"SELECT {ALL_APPEARS_IN} "
            f"FROM appears_in "
            f"WHERE gtitle='{sanitizeInput(gtitle)}';"
    )

def getRelationsAndRNByCharacter(cname: str, rn: int) -> str: 
    """Return a query to get the relation and Ryu Number of a character.
    
    The query retrieves the character's name, as well as the title and Ryu
    Number of all games that the character appears in with a Ryu Number 
    greater than or equal to the passed value.

    The resulting tuple takes the following form for appears_in as AI and
    game as G: `(AI.cname: str, AI.gtitle: str, G.ryu_number: int)`
    """
    return (f"SELECT AI.cname, AI.gtitle, G.ryu_number "
            f"FROM appears_in AS AI "
            f"JOIN game AS G ON G.title=AI.gtitle "
            f"WHERE cname='{sanitizeInput(cname)}' AND G.ryu_number>={rn};"
    )

def getRelationsAndRNByGame(gtitle: str, rn: int) -> str: 
    """Return a query to get the relation and Ryu Number of a game.
    
    The query retrieves the game's title, as well as the name and Ryu
    Number of all characters who appear in that game and have a Ryu Number 
    greater than or equal to the passed value minus one.

    The resulting tuple takes the following form for appears_in as AI and
    game_character as C: `(AI.cname: str, AI.gtitle: str, C.ryu_number: int)`
    """
    return (f"SELECT AI.cname, AI.gtitle, C.ryu_number "
            f"FROM appears_in AS AI "
            f"JOIN game_character AS C ON C.name=AI.cname "
            f"WHERE gtitle='{sanitizeInput(gtitle)}' AND C.ryu_number>={rn}-1;"
    )

def removeCharacterRelations(cname: str) -> str: 
    """Return a query to remove all of a character's relations."""
    return (f"DELETE FROM appears_in "
            f"WHERE cname='{sanitizeInput(cname)}';"
    )

def removeGameRelations(gtitle: str) -> str: 
    """Return a query to remove all of a game's relations."""
    return (f"DELETE FROM appears_in "
            f"WHERE gtitle='{sanitizeInput(gtitle)}';"
    )

def removeRelation(cname: str, gtitle: str) -> str: 
    """Return a query to remove a specific relation."""
    return (f"DELETE FROM appears_in "
            f"WHERE cname='{sanitizeInput(cname)}' AND gtitle='{sanitizeInput(gtitle)}';"
    )


#====================#
# RYU NUMBER QUERIES #
#====================#
def getGameFromCharacter(cname: str) -> str: 
    """Return a query to get games with equal Ryu Number to a character.
    
    The query will retrieve the title and Ryu Number of a game whose Ryu 
    Number is exactly equal to the Ryu Number of the character whose name is
    passed. This is used primarily for path-finding towards Ryu.

    The resulting query takes the following form for game as G:
    `(G.title: str, G.ryu_number: int)`
    """
    return (f"SELECT DISTINCT G.title, G.ryu_number "
            f"FROM appears_in "
            f"INNER JOIN game_character AS C ON cname=C.name "
            f"INNER JOIN game AS G ON gtitle=G.title "
            f"WHERE cname LIKE '{sanitizeInput(cname)}' AND G.ryu_number=C.ryu_number;"
    )

def getCharacterFromGame(gtitle: str) -> str: 
    """Return a query to get characters with lower Ryu Number to a game.
    
    The query will retrieve the name and Ryu Number of a character whose Ryu
    Number is exactly one less than the Ryu Number of the game whose title
    is passed. This is used primarily for path-finding towards Ryu.

    The resulting query takes the following form for game_character as C:
    `(C.name: str, C.ryu_number: int)`
    """
    return (f"SELECT DISTINCT C.name, C.ryu_number "
            f"FROM appears_in "
            f"INNER JOIN game_character AS C ON cname=C.name "
            f"INNER JOIN game AS G ON gtitle=G.title "
            f"WHERE gtitle LIKE '{sanitizeInput(gtitle)}' AND C.ryu_number=G.ryu_number-1;"
    )

def getNumCharactersWithRN(rn: int) -> str: 
    """Return a query to get the count of characters with a given Ryu Number.
    
    The resulting query takes the form: `(COUNT(*): int)`
    """
    return (f"SELECT COUNT(*) FROM game_character "
            f"WHERE ryu_number={rn};"
    )

def getNumGamesWithRN(rn: int) -> str: 
    """Return a query to get the count of games with a given Ryu Number.
    
    The resulting query takes the form: `(COUNT(*): int)`
    """
    return (f"SELECT COUNT(*) FROM game "
            f"WHERE ryu_number={rn};"
    )