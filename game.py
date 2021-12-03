from typing import Tuple

from node import Node

class game(Node):
    def __init__ (self, title, ryu_number, release_date):
        super().__init__(title, ryu_number)
        self.title, self.release_date = self.primary_key, release_date
    def __str__ (self):
        return "%s (%s)" % (self.title, self.release_date)
    def printSelf(self, limit = -1, withRn = False):
        if withRn: return str(self) + " [%d]" % self.ryu_number
        else: return str(self)

def tupleToGame(t: Tuple[str, int, str]):
    return game(t[0], t[1], t[2])