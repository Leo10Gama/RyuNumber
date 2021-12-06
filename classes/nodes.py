"""Classes for the node objects in the database, and their related methods.

These "nodes" in the database are set to represent the important tables
of the database.

Classes
-------
Node(ABC)
    An abstract representation of a node in the Ryu database.
game_character(Node)
    A class meant to represent a character table in the database.
game(Node)
    A class meant to represent the game table in the database.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

from classes.ryu_connector import RyuConnector
from methods import queries

class Node(ABC):
    """An abstract representation of a node in the Ryu database.
    
    This Node is meant to be inherited by `game` and `game_character` tables
    to better represent them.

    Attributes
    ----------
    primary_key: str
        An attribute representing the primary key field of the table.
    ryu_number: int
        The Ryu Number of the table.
    
    Methods
    -------
    printSelf(self, int, bool) -> str
        An abstract method representing printing the contents of the node. Must
        be overridden by child classes.
    """
    def __init__(self, pk: str, rn: int) -> None:
        self.primary_key = pk
        self.ryu_number = rn

    @abstractmethod
    def printSelf(self, limit: int=-1, withRn: bool=False) -> str:
        """Return a string representation of the node object.
        
        This method is intended to be overridden by child classes to better
        suit their attributes.

        Parameters
        ----------
        limit: int
            The limit of how many 'multiple' results to show. 
        withRn: bool
            Whether or not to include the node's Ryu Number when printing.
        """
        pass


class game_character(Node):
    """A class meant to represent a character table in the database.
    
    The character object has related attributes for all fields it has in the
    database, as well as a few others.

    Attributes
    ----------
    name: str
        The name of the character, directly related to the `name` field in the
        database. This also doubles as the primary_key.
    ryu_number: int
        The character's Ryu Number, directly related to the `ryu_number` field
        in the database.
    appears_in: List[str]
        A list of the titles of games that the character appears in. This is 
        meant to illustrate the `appears_in` table in the database.
    """
    def __init__ (self, name: str, ryu_number: int, appears_in: List[str]=[]) -> None:
        super().__init__(name, ryu_number)
        self.name = self.primary_key
        if appears_in:
            self.appears_in = appears_in
        else:
            self.appears_in = []

    def __str__ (self) -> str:
        returnStr = "(%d) %s\n" % (self.ryu_number, self.name)
        for g in self.appears_in:
            returnStr += "\t%s\n" % g
        return returnStr

    def printSelf(self, limit: int=-1, withRn: bool=False) -> str:
        """Return a string representation of the character object.
        
        This method has been overridden from its abstract parent Node.

        Parameters
        ----------
        limit: int
            The limit of how many 'appears_in' results to show. When set to -1, all
            values will be printed.
        withRn: bool
            Whether or not to include the node's Ryu Number when printing. If true,
            the Ryu Number will appear in square braces after the character's name.
        """
        if limit == -1: limit = len(self.appears_in)
        elif limit < 0: limit = 0
        returnStr = "%s" % self.name
        if withRn: returnStr += " [%d]" % self.ryu_number
        for i in range(min(limit, len(self.appears_in))):
            returnStr += "\n\t%s" % self.appears_in[i]
        if limit < len(self.appears_in) and limit != 0:
            returnStr += "\n\t... and %d more" % (len(self.appears_in) - limit)
        elif limit == 0:
            returnStr += "\n\t(Appears in %d game%s)" % (len(self.appears_in), "" if len(self.appears_in) == 1 else "s")
        return returnStr


class game(Node):
    """A class meant to represent the game table in the database.
    
    The game object has related attributes for all fields it has in the
    database.

    Attributes
    ----------
    title: str
        The title of the game, directly related to the `title` field in the
        database. This also doubles as the primary_key.
    ryu_number: int
        The game's Ryu Number, directly related to the `ryu_number` field in the
        database.
    release_date: str
        The date (in YYYY-MM-DD format) that the game was released.
    """
    def __init__ (self, title: str, ryu_number: int, release_date: str) -> None:
        super().__init__(title, ryu_number)
        self.title, self.release_date = self.primary_key, release_date

    def __str__ (self) -> str:
        return "%s (%s)" % (self.title, self.release_date)

    def printSelf(self, limit: int=-1, withRn: bool=False) -> str:
        """Return a string representation of the game object.
        
        This method has been overridden from its abstract parent Node.

        Parameters
        ----------
        limit: int
            The limit of how many 'multiple' results to show. In the case of games,
            this field goes unused.
        withRn: bool
            Whether or not to include the node's Ryu Number when printing. If true,
            the Ryu Number will appear in square braces after the game's title.
        """
        if withRn: return str(self) + " [%d]" % self.ryu_number
        else: return str(self)


def tupleToCharacter(t: Tuple[str, int]) -> Optional[game_character]:
    """Return a game_character object directly related to a tuple.
    
    The anticipated tuple input is the result of a query for a character.
    That is, it is expected to be (name, ryu_number). If the passed tuple is
    invalid or errors occur during connection, nothing is returned.
    """
    try:
        with RyuConnector() as rdb:
            rdb.execute(queries.getGamesByCharacter(t[0]))
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