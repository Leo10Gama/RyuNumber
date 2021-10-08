import game
import game_character
import maintenance
import os
import ryu_number

### BEGIN CONSTANTS ###

MENU = "\n+------------------RYU DATABASE------------------+\n\
|         Enter a letter to get started.         |\n\
|                                                |\n\
+---QUERY COMMANDS-------------------------------+\n\
|                                                |\n\
| (c/C) Query a character (exactly)              |\n\
|       [num] Limit visible games                |\n\
|             Default = 3; All = -1;             |\n\
| (g/G) Query a game (exactly)                   |\n\
| (p/P) Get a path from a character to Ryu       |\n\
|       [num] Limit visible games                |\n\
|             Default = 3; All = -1;             |\n\
| (n/N) See stats about the database             |\n\
|                                                |\n\
+---ALTER DATABASE COMMANDS----------------------+\n\
|                                                |\n\
| (i/I) Insert a game and characters into the DB |\n\
| (a/A) Add characters to an existing game       |\n\
| (x/X) Remove a character from the db entirely  |\n\
| (u/U) Update a character or game               |\n\
|                                                |\n\
+---MAINTENANCE----------------------------------+\n\
|                                                |\n\
| (v/V) Toggle view (compact or descriptive)     |\n\
| (r/R) Reset the database (include all details) |\n\
| (q/Q) Close the database and quit              |\n\
|                                                |\n\
+------------------------------------------------+\n\
|   (Note: brackets in desc. = capital letter)   |\n\
+------------------------------------------------+\n"

MENU_COMPACT = "\n+------------------RYU DATABASE------------------+\n\
|         Enter a letter to get started.         |\n\
|                                                |\n\
| (c/C)* Query a character (exactly)             |\n\
| (g/G) Query a game (exactly)                   |\n\
| (p/P)* Get a path from a character to Ryu      |\n\
| (n/N) See stats about the database             |\n\
| (i/I) Insert a game and characters into the DB |\n\
| (a/A) Add characters to an existing game       |\n\
| (x/X) Remove a character from the db entirely  |\n\
| (u/U) Update a character or game               |\n\
| (v/V) Toggle view (compact or descriptive)     |\n\
| (r/R) Reset the database (include all details) |\n\
| (q/Q) Close the database and quit              |\n\
|                                                |\n\
+------------------------------------------------+\n\
|      * = [num] Limit visible games, where      |\n\
|            (Default = 3; All = -1;)            |\n\
|   (Note: brackets in desc. = capital letter)   |\n\
+------------------------------------------------+\n"

illegalCharacters = ["/", "\\", ":", "*", "?", "\"", "'", "<", ">", "|", "'", "`", "%"]
path = "Games List"
defaultLimiter = 3

# Returns whether a string `date` follows the format (####-##-##)
def validDate(date):
    if len(date) == 10:
        return date[0:4].isnumeric() and date[5:7].isnumeric() and date[8:10].isnumeric() and date[4] == "-" and date[7] == "-"
    return False

# Returns a string without any illegal characters
def removeIllegalChars(s):
    if s:
        for c in illegalCharacters:
            s = s.replace(c, "")
    return s

### END CONSTANTS ###

### BEGIN FUNCTIONS ###

# USEFUL HELPER FUNCTIONS

def resultViewer(results, canSelect = False, page = 1, resultsPerPage = 10, limiter = 1):
    # NOTE: `page` is the on-screen number, thus the index should be one fewer (i.e. page 1 = results[0])
    # NOTE: ensure 1 <= `page` <= `totalPages` holds ALWAYS
    prompt = "(p) Previous page\n(n) Next page\n(#) Select this one\n(*) Close view\n\n" if canSelect else "(p) Previous page\n(n) Next page\n(*) Close view\n\n"
    cmd = "."
    totalPages = len(results) / resultsPerPage
    if len(results) % resultsPerPage != 0: totalPages += 1
    while cmd:
        # Print results
        print("======================== RESULT  VIEWER ========================")
        print("\t%d results:\n" % len(results))
        for i in range((page - 1) * resultsPerPage, min(((page - 1) * resultsPerPage) + resultsPerPage, len(results))):
            print("(%d) %s" % (i + 1, results[i].printSelf(limiter)))
        else:
            print()
        # Print nav bar
        # Print prefix part
        print("<(p) ", end="")
        if page > 2:
            print("1 ... ", end="")
        # Print current selection
        if page == 1:
            print("{%d} " % page, end="")
            if page + 1 <= totalPages:
                print("%d " % (page + 1), end="")
        else:
            # Previous and current number
            print("%d {%d} " % (page - 1, page), end="")
            # Next number (if possible)
            if page + 1 <= totalPages:
                print("%d " % (page + 1), end="")
        # Print suffix part
        if (page + 1) <= totalPages - 1:
            print("... %d " % totalPages, end="")
        print("(n)>\n================================================================\n")
        # Prompt next action
        cmd = input(prompt).lower()
        print()
        if cmd != "" and not canSelect: cmd = cmd[0]
        if cmd.isnumeric() and canSelect:
            cmd = int(cmd)
            if cmd >= 1 and cmd <= len(results):
                print("Selected option (%d): %s\n" % (cmd, results[cmd - 1].name if isinstance(results[cmd - 1], game_character.game_character) else results[cmd - 1].title if isinstance(results[cmd - 1], game.game) else results[cmd - 1].printSelf(limit = 0, withRn = False)))
                return results[cmd - 1]
        if cmd != "p" and cmd != "n": cmd = ""
        if cmd == "p":
            if page > 1: page -= 1
            else: print("This is the first page; cannot go back\n")
        elif cmd == "n":
            if page + 1 <= totalPages: page += 1
            else: print("This is the last page; cannot go further\n")
    return None

# QUERY FUNCTIONS

def queryCharacter(exact = False, limiter = -1):
    charToQuery = removeIllegalChars(input("Please enter a character's name%s" % (" exactly: " if exact else ": ")))
    print()
    if exact:       # Querying by exact name (myCharacters is a game_character object)
        myCharacters = game_character.getByNameExact(charToQuery)
        if myCharacters:
            print(myCharacters.printSelf(limiter, withRn = True))
        else:
            print("No characters by that name could be found")        
    else:           # Querying by generalized name (myCharacters is a list of game_character objects)
        myCharacters = game_character.getByName(charToQuery)  
        if myCharacters:
            myChar = resultViewer(myCharacters, canSelect = True)
            if myChar:
                print(myChar.printSelf(withRn = True))
        else:
            print("No characters by that name could be found")

def queryGame(exact = False):
    gameToQuery = removeIllegalChars(input("Please enter a game name%s" % (" exactly: " if exact else ": ")))
    print()
    if exact:           # Querying by exact title (myGames is a game object)
        myGames = game.getByTitleExact(gameToQuery)
        if myGames:
            print(myGames.printSelf(withRn = True))
        else:
            print("No games by that name could be found")
    else:               # Querying by generalized title (myGames is a list of game objects)
        myGames = game.getByTitle(gameToQuery)
        if myGames:
            g = resultViewer(myGames, canSelect = True)
            if g:
                print(g.printSelf(withRn = True))
        else:
            print("No games by that name could be found")

def getPath(limiter = defaultLimiter):
    # Get query
    charToPath = removeIllegalChars(input("Enter the character's name: "))
    print()
    characterToQuery = game_character.getByName(charToPath)
    if not characterToQuery:
        print("No character by that name could be found in the database.")
        return
    # Get selection
    myChar = resultViewer(characterToQuery, True)
    if myChar:
        print("Retrieving %s" % myChar.name)
        p = ryu_number.getPathFromCharacter(myChar.name) # Get the path
        if p:       # If the path actually exists
            for elem in p:
                if isinstance(elem, game.game):
                    print("(↓) %s" % (elem.printSelf(limiter)))
                else:
                    print("(%d) %s" % (elem.ryu_number, elem.printSelf(limiter)))
        else:
            print("Something went *really* wrong. Like, super wrong. Like, you shouldn't be able to see this text at all. If you are, CONTACT ME PLEASE")
    else:
        print("No character selected. Cancelling...")

def getStats():
    statsToSee = input("(g) Games\n(c) Characters\n(a) All \n(*) Back\n\nWhich stats would you like to see?\n")
    print()
    def getGames():
        rn = 1
        val = game.getGamesCountWithRN(rn)
        while val:
            print("Games with Ryu Number %d: %d" % (rn, val))
            rn += 1
            val = game.getGamesCountWithRN(rn)
        print("\nTotal number of games in database: %d" % game.getNumberOfGames())
    def getCharacters():
        rn = 0
        val = game_character.getCharactersCountWithRN(rn)
        while val:
            print("Characters with Ryu Number %d: %d" % (rn, val))
            rn += 1
            val = game_character.getCharactersCountWithRN(rn)
        print("\nTotal number of characters in database: %d" % game_character.getNumberOfCharacters())
    if statsToSee[0].lower() == "g":
        # See games
        getGames()
    elif statsToSee[0].lower() == "c":
        # See characters
        getCharacters()
    elif statsToSee[0].lower() == "a":
        # See all
        getGames()
        print()
        getCharacters()
    else:
        # Do nothing
        print("Not a recognized option. Cancelling query...")

# ALTER DATABASE FUNCTIONS

def addCharacters(charactersToAdd = []):
    c2add = None
    while not c2add:
        # Receive input
        c2add = removeIllegalChars(input("Enter character name, or enter '.' to cancel the insert (enter nothing to finish):\n"))
        print()
        # Query if character already exists
        if c2add == ".":
            return []
        if c2add:
            possibleCharacters = game_character.getByName(c2add)
            # If character exists, prompt to pick one of them or the entered value, or some other value entirely
            if possibleCharacters:
                print("Found %d character(s) with similar name:\n" % len(possibleCharacters))
                for i in range(len(possibleCharacters)):
                    print("(%d) %s (%s)" % (i, possibleCharacters[i].name, possibleCharacters[i].appears_in[0].title))
                whatDo = input("\nWhat would you like to do?\n[num] Use that character name\n[n/N] Use what I wrote\n[anything else] Enter another name\n")
                # Number is inputted, use that value
                if whatDo.isnumeric() and int(whatDo) < len(possibleCharacters):
                    if possibleCharacters[int(whatDo)].name in charactersToAdd:
                        print("That character is already in this game!")
                    else:
                        print("Adding '%s'...\n" % possibleCharacters[int(whatDo)].name)
                        charactersToAdd.append(possibleCharacters[int(whatDo)].name)
                # Use the value I inserted
                elif whatDo.lower() == "n":
                    if c2add in charactersToAdd:
                        print("That character is already in this game!")
                    else:
                        print("Adding '%s'..." % c2add)
                        charactersToAdd.append(c2add)
                else:
                    print("Cancelling that insert...")
            else:
                whatDo = input("'%s' does not exist in the database yet.\nAdd them anyway? (y/n): " % c2add)
                if whatDo.lower() in ["y", "ye", "yes", "yea"]:
                    if c2add in charactersToAdd:
                        print("That character is already in this game!")
                    else:
                        print("Adding '%s'...\n" % c2add)
                        charactersToAdd.append(c2add)
                else:
                    print("Cancelling that insert...\n")
            c2add = None
        else:
            c2add = "owo"
    return charactersToAdd

def insertGame():
    # newGame contains the name of the game to be inserted
    # Parse it with characters that can be used in text file names
    newGame = removeIllegalChars(input("Enter the game's name: "))
    print()
    if game.getByTitleExact(newGame):
        print("That game already exists in the database!")
    else:
        # Get release date
        releaseDate = None
        while not releaseDate:
            releaseDate = input("Enter the game's release date (YYYY-MM-DD): ")
            print()
            # Verify format
            if validDate(releaseDate):
                break
            releaseDate = None
            print("Format invalid. Please enter the release date in the proper format!")
        # Get characters
        charactersToAdd = addCharacters()
        if not charactersToAdd: return
        # Write the file
        print("Creating file for game...", end="")
        with open("%s/%s.txt" % (path, newGame), "w") as f:
            f.write("%s" % releaseDate)
            for c in charactersToAdd:
                f.write("\n%s" % c)
        print("Done")
        # Insert into the database
        print("Adding to database...", end="")
        game.insertGame(newGame, releaseDate)
        priorityInserts = []
        if len(charactersToAdd) > 1: priorityInserts = [x.name for x in game_character.getManyByNames(tuple(charactersToAdd))]
        for x in priorityInserts:
            if x in charactersToAdd:
                charactersToAdd.remove(x)
        if priorityInserts: game_character.insertCharactersToGame(priorityInserts, newGame)
        if charactersToAdd: game_character.insertCharactersToGame(charactersToAdd, newGame)
        print("Done")

def addToGame():
    # Get game to add to
    gameToAddTo = removeIllegalChars(input("Enter game title: "))
    print()
    # Verify game in DB and cross-check with user
    gameToAddTo = game.getByTitle(gameToAddTo)
    if not gameToAddTo:
        print("That game does not exist in the database! Try inserting the game yourself.")
    else:
        gameToAddTo = resultViewer(gameToAddTo, True)
        if gameToAddTo:
            gameToAddTo = gameToAddTo.title
            # Start receiving character input
            charactersToAdd = [x.name for x in game_character.getCharactersByGame(gameToAddTo)]
            charactersToAdd = addCharacters(charactersToAdd)
            if not charactersToAdd: return
            # Write the file
            print("Writing to file...", end="")
            currChars = [x.name for x in game_character.getCharactersByGame(gameToAddTo)]
            for c in currChars:
                if c in charactersToAdd:
                    charactersToAdd.remove(c)
            with open("%s/%s.txt" % (path, gameToAddTo), "a") as f:
                for c in charactersToAdd:
                    f.write("\n%s" % c)
            print("Done")
            # Insert into the database
            print("Adding to database...", end="")
            priorityInserts = []
            if len(charactersToAdd) > 1: priorityInserts = [x.name for x in game_character.getManyByNames(tuple(charactersToAdd))]
            for x in priorityInserts:
                if x in charactersToAdd:
                    charactersToAdd.remove(x)
            if priorityInserts: game_character.insertCharactersToGame(priorityInserts, gameToAddTo)
            if charactersToAdd: game_character.insertCharactersToGame(charactersToAdd, gameToAddTo)
            print("Done")
        else:
            print("Invalid input. Cancelling action...")

def removeCharacter():
    # Query character
    charToRemove = input("Enter the name of the character to remove: ")
    removeIllegalChars(charToRemove)
    myChars = game_character.getByName(charToRemove)
    # Select character to remove
    print()
    for i in range(len(myChars)):
        print("(%d) %s (%s)" % (i, myChars[i].name, myChars[i].appears_in[0].title))
    else:
        print("(%d) Cancel" % len(myChars))
    print()
    charIndex = input("Which character would you like to remove? (int): ")
    # Find and remove that character from each game
    print()
    if charIndex.isnumeric():
        charIndex = int(charIndex)
        if charIndex >= 0 and charIndex <= len(myChars):
            if charIndex == len(myChars):
                print("Cancelling the operation...")
                return
            else:
                confirm = input("Are you sure you want to remove '%s' from the database?\n(y/n): " % myChars[charIndex].name)
                if confirm.lower() == "y":
                    charToRemove = myChars[charIndex]
                    for myGame in charToRemove.appears_in:
                        myGame = myGame.title
                        with open("%s/%s.txt" % (path, myGame), "r+") as f:
                            lines = f.readlines()
                            f.seek(0)
                            for line in lines:
                                if line.strip("\n") != charToRemove.name:
                                    f.write(line)
                            f.truncate()
                    print("'%s' removed successfully.\nNOTE: This change will only be noticed when the database is reset." % charToRemove.name)
                    return True
                else:
                    print("Cancelling the operation...")
        else:
            print("Number not in range. Cancelling...")
    else:
        print("You have not entered a number. Cancelling...")
    return False

def updateData():
    # Update Character
    def updateCharacter():
        pass

    # Update Game
    def updateGame():
        # Update title
        def updateTitle(oldTitle):
            newTitle = removeIllegalChars(input("Enter new title: "))
            print()
            if game.getByTitleExact(newTitle):
                print("A game with that name already exists! Cancelling the action...")
            else:
                confirmUpdate = input("You are about to change the following game's title:\n\n%s\n\t↓\n%s\n\nConfirm update? (y/n): " % (oldTitle, newTitle))
                if confirmUpdate.lower() == "y":
                    # Update file name
                    os.rename("%s/%s.txt" % (path, oldTitle), "%s/%s.txt" % (path, newTitle))
                    # Update database
                    game.updateGameTitle(oldTitle, newTitle)
                    print("Changes made successfully.")
                else:
                    print("Update cancelled.")

        # Update release date
        def updateReleaseDate(gameTitle):
            newRDate = input("Enter new release date (YYYY-MM-DD): ")
            print()
            if validDate(newRDate):
                confirmUpdate = input("You are about to change the release date for:\n\n%s\n\nTo the following:\n\n%s\n\t↓\n%s\n\nConfirm update? (y/n): " % (gameTitle, g.release_date, newRDate))
                if confirmUpdate.lower() == "y":
                    # Update file (line 1 of text file)
                    f = open("%s/%s.txt" % (path, gameTitle), "r")
                    lines = f.readlines()
                    lines[0] = "%s\n" % newRDate
                    f = open("%s/%s.txt" % (path, gameTitle), "w")
                    f.writelines(lines)
                    f.close()
                    # Update database
                    game.updateGameReleaseDate(gameTitle, newRDate)
                    print("Changes made successfully.")
                else:
                    print("Update cancelled.")
            else:
                print("Date entered is invalid. Cancelling the update...")

        # Query game
        g = removeIllegalChars(input("Enter game title: "))
        print()
        results = game.getByTitle(g)
        # Select game
        g = resultViewer(results, True)
        if g:
            # Decide what to update and what to change it to
            attribute = input("What would you like to update?\n\n(t) Title\n(r) Release Date\n(*) Cancel\n\n")
            print()
            if attribute:
                if attribute[0].lower() == "t":     # Update title
                    updateTitle(g.title)
                    return
                elif attribute[0].lower() == "r":   # Update release date
                    updateReleaseDate(g.title)                    
                    return
            print("No valid option selected. Cancelling the operation...")
        else:
            print("No game selected. Cancelling the operation...")

    # Decide what to do
    action = input("Which would you like to update?\n\n(c) Character\n(g) Game\n(*) Cancel\n\n")
    if action:
        if action[0].lower() == "c":
            updateCharacter()
            return
        elif action[0].lower() == "g":
            updateGame()
            return
    print("Invalid input. Cancelling the action...")
    

# MAINTENANCE FUNCTIONS

def toggleView(currStyle):
    currStyle = "default" if currStyle == "compact" else "compact"
    return currStyle

def resetDatabase(detailed = False):
    response = input("This command will take *a while* to execute.\nAre you sure you want to reset the database? (y/n): ")
    print()
    if response.lower() in ["y", "yes", "yea", "ye", "ok", "okay"]:
        maintenance.reset_db(not detailed, detailed)
    else:
        print("Cancelling...")

### END FUNCTIONS ###

def main():
    command = ""
    menuStyle = "default"
    uncommittedChanges = False
    while (command != "Q" and command != "q"):
        print(MENU_COMPACT if menuStyle == "compact" else MENU)
        command = input().strip()
        print()
        if command != "":
            if command[0].lower() == "c" and (command[1:].isnumeric() or len(command) == 1 or (command[1] == "-" and command[2:].isnumeric())):
                queryCharacter(True if command[0] == "C" else False, int(command[1:]) if command[1:] else -1)
            elif command.lower() == "g":
                queryGame(True if command == "G" else False)
            elif command[0].lower() == "p" and (command[1:].isnumeric() or len(command) == 1 or (command[1] == "-" and command[2:].isnumeric())):
                getPath(int(command[1:]) if command[1:] else defaultLimiter)
            elif command.lower() == "n":
                getStats()
            elif command.lower() == "i":
                insertGame()
            elif command.lower() == "a":
                addToGame()
            elif command.lower() == "x":
                if removeCharacter():
                    uncommittedChanges = True
            elif command.lower() == "u":
                updateData()
            elif command.lower() == "v":
                menuStyle = toggleView(menuStyle)
            elif command.lower() == "r":
                resetDatabase(True if command == "R" else False)
                uncommittedChanges = False
            elif command.lower() == "q":
                if uncommittedChanges:
                    confirm = input("You have unsaved changes that have not yet been added to the database.\nClose anyways? (y/n): ")
                    if confirm[0].lower() == "y":
                        print("\nThank you for using the Ryu Database! :)")
                    else:
                        command = ""
                else:
                    print("Thank you for using the Ryu Database! :)")
            else:
                print("Command not recognized. Please try again")
    quit()


if __name__ == "__main__":
    main()