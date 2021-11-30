class game:
    def __init__ (self, title, ryu_number, release_date):
        self.title, self.ryu_number, self.release_date = title, ryu_number, release_date
    def __str__ (self):
        return "%s (%s)" % (self.title, self.release_date)
    def printSelf(self, limit = -1, withRn = False):
        if withRn: return str(self) + " [%d]" % self.ryu_number
        else: return str(self)