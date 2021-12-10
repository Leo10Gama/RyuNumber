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
from typing import List

from methods import queries
from classes.ryu_connector import RyuConnector


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

    def getMissingData(self, rdb: RyuConnector) -> bool:
        """Retrieve any data that may be missing to the class.
        
        This method is intended to connect to the database to fill in any empty
        fields that a Node may be missing. This is intended to abstract-ify the
        data retrieval process, putting the onus on the object itself rather 
        than the class retrieving the object itself.

        Parameters
        ----------
        rdb: RyuConnector.cursor
            A cursor object opened by a RyuConnector.
        """
        return True


class GameCharacter(Node):
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
    aliases: List[str]
        A list of aliases that the character is known by. This is meant to
        illustrate the `alias` table in the database.
    """
    def __init__ (self, name: str, ryu_number: int, appears_in: List[str]=None, aliases: List[str]=None) -> None:
        super().__init__(name, ryu_number)
        self.name = self.primary_key
        if appears_in is not None:
            self.appears_in = appears_in
        else:
            self.appears_in = []
        if aliases is not None:
            self.aliases = aliases
        else:
            self.aliases = []

    def __str__ (self) -> str:
        returnStr = "(%d) %s\n" % (self.ryu_number, self.name)
        if self.aliases:
            returnStr += f"\t(AKA {', '.join(self.aliases)})\n"
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
        if self.aliases:
            returnStr += f"\n\t(AKA {', '.join(self.aliases)})"
        for i in range(min(limit, len(self.appears_in))):
            returnStr += "\n\t%s" % self.appears_in[i]
        if limit < len(self.appears_in) and limit != 0:
            returnStr += "\n\t... and %d more" % (len(self.appears_in) - limit)
        elif limit == 0:
            returnStr += "\n\t(Appears in %d game%s)" % (len(self.appears_in), "" if len(self.appears_in) == 1 else "s")
        return returnStr

    def getMissingData(self, rdb: RyuConnector) -> bool:
        """Retrieve any data that may be missing to the class.
        
        This method is overridden from its parent. The character will connect 
        to the database and fill in the missing `self.appears_in` and 
        `self.aliases` fields.
        
        Parameters
        ----------
        rdb: RyuConnector.cursor
            A cursor object opened by a RyuConnector.
        """
        try:
            # Get appears_in relations
            if not self.appears_in:
                rdb.execute(queries.getGamesByCharacter(self.name))
                mygames = rdb.fetchall()
                for row in mygames:
                    self.appears_in.append(row[0])
            # Get alias relations
            if not self.aliases:
                rdb.execute(queries.getAliasesFromName(self.name))
                myaliases = rdb.fetchall()
                for row in myaliases:
                    self.aliases.append(row[1])
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False


class Game(Node):
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
