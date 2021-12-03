from typing import Tuple

from node import Node
from ryu_connector import RyuConnector
import queries

class game_character(Node):
    def __init__ (self, name, ryu_number, appears_in = []):
        super().__init__(name, ryu_number)
        self.name = self.primary_key
        if appears_in:
            self.appears_in = appears_in
        else:
            self.appears_in = []
    def __str__ (self):
        returnStr = "(%d) %s\n" % (self.ryu_number, self.name)
        for g in self.appears_in:
            returnStr += "\t%s\n" % g
        return returnStr
    def printSelf(self, limit = -1, withRn = False):
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

def tupleToCharacter(t: Tuple[str, int]):
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