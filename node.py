from abc import ABC, abstractmethod

class Node(ABC):
    def __init__(self, pk: str, rn: int):
        self.primary_key = pk
        self.ryu_number = rn

    @abstractmethod
    def printSelf(self, limit = -1, withRn = False):
        pass