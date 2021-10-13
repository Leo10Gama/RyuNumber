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
| (x/X) Remove an item from the database         |\n\
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
| (x/X) Remove an item from the database         |\n\
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

# Replaces a given line in a file with another line
def replaceLine(oldLine, newLine, filePath, end = '\n'):
    with open(filePath, "r+") as f:
        lines = f.readlines()
        for i in range(len(lines)):
            if lines[i].strip('\n') == oldLine:
                if i < len(lines) - 1:
                    lines[i] = "%s%s" % (newLine, end)
                else:
                    lines[i] = "%s" % newLine
                    if end == '':
                        lines[i-1] = lines[i-1].strip('\n')
        f.seek(0)
        f.truncate()
        f.seek(0)
        f.writelines(lines)

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
                    print("(%d) %s (%s)" % (i, possibleCharacters[i].name, possibleCharacters[i].appears_in[0].title if len(possibleCharacters[i].appears_in) > 0 else "No games"))
                whatDo = input("\nWhat would you like to do?\n[num] Use that character name\n[n/N] Use what I wrote\n[anything else] Enter another name\n")
                # Number is inputted, use that value
                if whatDo.isnumeric() and int(whatDo) < len(possibleCharacters):
                    if possibleCharacters[int(whatDo)].name in charactersToAdd:
                        print("That character is already in this game!\n")
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

def removeFromDatabase():
    # Remove character
    def removeCharacter():
        # Remove from select game
        def removeFromGame(cName, gTitle):
            # Update in DB
            game_character.removeFromGame(cName, gTitle)
            # Update in local files
            replaceLine(cName, "", "%s/%s.txt" % (path, gTitle), end = "")
            print("Removed '%s' from '%s'" % (cName, gTitle))

        # Select character
        c = removeIllegalChars(input("Enter character name: "))
        c = resultViewer(game_character.getByName(c), True)
        if c:
            # Select where to remove
            option = input("Where would you like to remove the character?\n\n(g) From one game\n(a) From all games (the entire database)\n(*) Cancel\n\n").lower()
            print()
            if option == "g":
                # Remove from a select game
                print("Select a game to remove '%s' from:\n" % c.name)
                g = resultViewer(c.appears_in, True)
                if g:
                    confirmDelete = input("You are about to remove '%s'\nfrom the game '%s'\n\nAre you sure you want to proceed? (y/n): " % (c.name, g.title)).lower()
                    print()
                    if confirmDelete == "y":
                        removeFromGame(c.name, g.title)
                    else:
                        print("Cancelling...")
                else:
                    print("No game selected. Cancelling...")
            elif option == "a":
                # Remove from all games
                confirmDelete = input("You are about to remove:\n'%s'\nFrom the database. Proceed? (y/n): " % (c.name)).lower()
                print()
                if confirmDelete == "y":
                    for g in c.appears_in:
                        removeFromGame(c.name, g.title)
                    game_character.removeCharacter(c.name)
                else:
                    print("Cancelling...")
            else:
                print("Cancelling...")
        else:
            print("No character selected. Cancelling...")

    # Remove game
    def removeGame():
        g = removeIllegalChars(input("Enter game title: "))
        g = resultViewer(game.getByTitle(g), True)
        if g:
            confirmDelete = input("You are about to remvove the game:\n'%s'\nAre you sure you want to proceed? (y/n): " % g.title).lower()
            if confirmDelete == "y":
                # Remove from db
                game.removeGame(g.title)
                # Remove from local files
                if os.path.exists("%s/%s.txt" % (path, g.title)):
                    os.remove("%s/%s.txt" % (path, g.title))
                print("'%s' successfully removed")
        else:
            print("No game selected. Cancelling...")

    # Select what to remove
    option = input("What would you like to remove?\n\n(c) Character\n(g) Game\n(*) Cancel\n\n").lower()
    print()
    if option == "c":
        removeCharacter()
    elif option == "g":
        removeGame()
    else:
        print("Cancelling...")

def updateData():
    # Update Character
    def updateCharacter():
        # Update name
        def updateName(oldName):
            # This function acts as a helper, since its code is duplicated otherwise
            def updateFiles(oldName, newName):
                c = game_character.getByNameExact(oldName)
                for g in c.appears_in:
                    replaceLine(oldName, newName, "%s/%s.txt" % (path, g.title))

            newName = removeIllegalChars(input("Enter new name: "))
            print()
            existing = game_character.getByNameExact(newName)
            if existing:    # Overwriting character
                confirmUpdate = input("A character with that name already exists:\n\n%s\n\nThis will merge that character with '%s'.\nProceed? (y/n): " % (existing.printSelf(), oldName))
                if confirmUpdate.lower() == "y":
                    updateFiles(oldName, existing.name)
                    c = game_character.getByNameExact(oldName)
                    for g in c.appears_in:
                        game_character.insertCharactersToGame([oldName], g.title)
                    else:
                        game_character.removeCharacter(oldName)
                    print("Changes made successfully.\n(NOTE: Some Ryu Numbers may not have updated accordingly.\nTo fix this, you may need to reset the database.)")
                else:
                    print("Update cancelled.")
            else:           # Not overwriting character
                confirmUpdate = input("You are about to change the following character's name:\n\n%s\n\t↓\n%s\n\nConfirm update? (y/n): " % (oldName, newName))
                if confirmUpdate.lower() == "y":
                    updateFiles(oldName, newName)
                    game_character.updateCharacterName(oldName, newName)
                    print("Changes made successfully.")
                else:
                    print("Update cancelled.")

        # Query character
        c = removeIllegalChars(input("Enter character name: "))
        print()
        results = game_character.getByName(c)
        # Select character
        c = resultViewer(results, True)
        if c:
            # Decide what to update and what to change it to
            # NOTE: Right now, the only attribute characters have is `name`, but more functionality could be possible in the future
            attribute = input("What would you like to update?\n\n(n) Name\n(*) Cancel\n\n")
            print()
            if attribute.lower() == "n":    # Update name
                updateName(c.name)
            else:
                print("No valid option selected. Cancelling the operation...")
        else:
            print("No character selected. Cancelling the operation...")

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
            if attribute.lower() == "t":     # Update title
                updateTitle(g.title)
            elif attribute.lower() == "r":   # Update release date
                updateReleaseDate(g.title)                    
            else:
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
                if removeFromDatabase():
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