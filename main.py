import file_manager as fm
import game
import game_character
import maintenance
import os
import ryu_database as rdb
import ryu_number


### BEGIN CONSTANTS ###

MENU = "\n+------------------RYU DATABASE------------------+\n\
|         Enter a letter to get started.         |\n\
|                                                |\n\
+---QUERY COMMANDS-------------------------------+\n\
|                                                |\n\
| (c/C) Query a character (exactly)              |\n\
| (g/G) Query a game (exactly)                   |\n\
| (p/P) Get a path from a character to Ryu       |\n\
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
| (v/V) Toggle view to be compact or descriptive |\n\
| (r/R) Reset the database (include all details) |\n\
| (q/Q) Close the database and quit              |\n\
|                                                |\n\
+------------------------------------------------+\n\
|   (Note: brackets in desc. = capital letter)   |\n\
+------------------------------------------------+\n"

MENU_COMPACT = "\n+------------------RYU DATABASE------------------+\n\
|         Enter a letter to get started.         |\n\
|                                                |\n\
| (c/C) Query a character (exactly)              |\n\
| (g/G) Query a game (exactly)                   |\n\
| (p/P) Get a path from a character to Ryu       |\n\
| (n/N) See stats about the database             |\n\
| (i/I) Insert a game and characters into the DB |\n\
| (a/A) Add characters to an existing game       |\n\
| (x/X) Remove an item from the database         |\n\
| (u/U) Update a character or game               |\n\
| (v/V) Toggle view to be compact or descriptive |\n\
| (r/R) Reset the database (include all details) |\n\
| (q/Q) Close the database and quit              |\n\
|                                                |\n\
+------------------------------------------------+\n\
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
    totalPages = int(len(results) / resultsPerPage)
    if len(results) % resultsPerPage != 0: totalPages += 1
    while cmd:
        # Print results
        print("======================== RESULT  VIEWER ========================")
        print("\t%d results:\n" % len(results))
        for i in range((page - 1) * resultsPerPage, min(((page - 1) * resultsPerPage) + resultsPerPage, len(results))):
            if type(results[i]) is game_character.game_character or type(results[i]) is game.game:
                print("(%d) %s" % (i + 1, results[i].printSelf(limit=limiter, withRn=False)))
            else:
                print("(%d) %s" % (i + 1, results[i]))
        else:
            print()
        # Print nav bar
        # Print prefix part
        print("<(p) ", end="")
        if page > 2:
            print("1 ", end="")
        # Print prefix dots (maybe)
        if page > 3:
            print("... ", end="")
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
        # Print suffix dots (maybe)
        if page < totalPages - 2:
            print("... ", end="")
        # Print suffix part
        if (page + 1) <= totalPages - 1:
            print(" %d " % totalPages, end="")
        print("(n)>\n================================================================\n")
        # Prompt next action
        cmd = input(prompt).lower()
        print()
        if cmd != "" and not canSelect: cmd = cmd[0]
        if cmd.isnumeric() and canSelect:
            cmd = int(cmd)
            if cmd >= 1 and cmd <= len(results):
                print("Selected option (%d): %s\n" % (cmd, results[cmd - 1].name if isinstance(results[cmd - 1], game_character.game_character) else results[cmd - 1].title if isinstance(results[cmd - 1], game.game) else results[cmd - 1]))
                return results[cmd - 1]
        if cmd != "p" and cmd != "n": cmd = ""
        if cmd == "p":
            if page > 1: page -= 1
            else: print("This is the first page; cannot go back\n")
        elif cmd == "n":
            if page + 1 <= totalPages: page += 1
            else: print("This is the last page; cannot go further\n")
    return None

def optionPicker(prompt, choices):
    print("%s\n" % prompt)
    for option in choices:
        print("(%s) %s" % (option, choices[option]))
    print("(*) Cancel\n")
    return input().lower()

# QUERY FUNCTIONS

def queryCharacter(exact = False, limiter = -1):
    charToQuery = removeIllegalChars(input("Please enter a character's name%s" % (" exactly: " if exact else ": ")))
    print()
    if charToQuery:
        if exact:       # Querying by exact name (myCharacters is a game_character object)
            myCharacters = rdb.getCharacterByName(charToQuery)
            if myCharacters:
                print(myCharacters.printSelf(limiter, withRn = True))
            else:
                print("No characters by that name could be found")        
        else:           # Querying by generalized name (myCharacters is a list of game_character objects)
            myCharacters = rdb.getCharactersLikeName(charToQuery)  
            if myCharacters:
                myChar = resultViewer(myCharacters, canSelect = True)
                if myChar:
                    print(myChar.printSelf(withRn = True))
            else:
                print("No characters by that name could be found")
    else:
        print("Nothing has been entered. Cancelling query...")

def queryGame(exact = False):
    gameToQuery = removeIllegalChars(input("Please enter a game name%s" % (" exactly: " if exact else ": ")))
    print()
    if gameToQuery:
        g = None
        if exact:           # Querying by exact title (myGames is a game object)
            g = rdb.getGameByTitle(gameToQuery)
            if g:
                print(g.printSelf(withRn = True))
            else:
                print("No games by that name could be found")
                return
        else:               # Querying by generalized title (myGames is a list of game objects)
            myGames = rdb.getGamesLikeTitle(gameToQuery)
            if myGames:
                g = resultViewer(myGames, canSelect = True, resultsPerPage=20)
                if g:
                    print(g.printSelf(withRn = True))
                else:
                    return
            else:
                print("No games by that name could be found")
                return
        # Prompt to see characters
        if input("\nSee characters from this game? (y/n) ").lower() == "y":
            resultViewer([c.name for c in rdb.getCharactersByGame(g.title)], resultsPerPage=20, limiter=0)
    else:
        print("Nothing has been entered. Cancelling query...")

def getPath(limiter = defaultLimiter):
    def printPath(path):
        print("%s has a Ryu Number of %d\n" % (path[0].name, path[0].ryu_number))
        if path:       # If the path actually exists
            for elem in path:
                if isinstance(elem, game.game):
                    print("(↓) %s" % (elem.printSelf(limiter)))
                else:
                    print("(%d) %s" % (elem.ryu_number, elem.printSelf(limiter)))
        else:
            print("Something went *really* wrong. Like, super wrong. Like, you shouldn't be able to see this text at all. If you are, CONTACT ME PLEASE")

    # Get query
    charToPath = removeIllegalChars(input("Enter the character's name: "))
    print()
    if charToPath:
        characterToQuery = rdb.getCharactersLikeName(charToPath)
        if not characterToQuery:
            print("No character by that name could be found in the database.")
            return
        # Get selection
        myChar = resultViewer(characterToQuery, True)
        if myChar:
            # Decide how to get path
            choice = optionPicker("How would you like to get path?", {"r": "Randomly", "c": "Choose my path"})
            print()
            if choice == "r":
                # Randomly get path
                p = ryu_number.getPathFromCharacter(myChar.name)
                printPath(p)
            elif choice == "c":
                x = myChar
                p = []
                p.append(x)
                # Choose my path
                while True:
                    x = rdb.getGameByTitle(resultViewer(ryu_number.stepTowardsRyu(x), True, resultsPerPage=20))
                    if x:
                        p.append(x)
                    else:
                        print("Cancelling...")
                        break
                    x = rdb.getCharacterByName(resultViewer(ryu_number.stepTowardsRyu(x), True, resultsPerPage=20))
                    if x:
                        p.append(x)
                        if type(x) is game_character.game_character and x.name == "Ryu":
                            printPath(p)
                            break
                    else:
                        print("Cancelling...")
                        break
            else:
                print("Cancelling...")
        else:
            print("No character selected. Cancelling...")
    else:
        print("Nothing entered. Cancelling the operation...")

def getStats():
    statsToSee = optionPicker("Which stats would you like to see?", {"g": "Games", "c": "Characters", "a": "All"})
    print()
    def getGames():
        rn = 1
        val = rdb.getNumGamesWithRN(rn)
        while val:
            print("Games with Ryu Number %d: %d" % (rn, val))
            rn += 1
            val = rdb.getNumGamesWithRN(rn)
        print("\nTotal number of games in database: %d" % rdb.getNumGames())
    def getCharacters():
        rn = 0
        val = rdb.getNumCharactersWithRN(rn)
        while val:
            print("Characters with Ryu Number %d: %d" % (rn, val))
            rn += 1
            val = rdb.getNumCharactersWithRN(rn)
        print("\nTotal number of characters in database: %d" % rdb.getNumCharacters())

    if statsToSee == "g":
        # See games
        getGames()
    elif statsToSee == "c":
        # See characters
        getCharacters()
    elif statsToSee == "a":
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
        # Cancel the insert
        if c2add == ".":
            return []
        # Actually add a character
        if c2add:
            possibleCharacters = rdb.getCharactersLikeName(c2add)
            # If character exists, prompt to pick one of them or the entered value, or some other value entirely
            if possibleCharacters:
                whatDo = optionPicker("Found %d character(s) with similar name to '%s'. What would you like to do?" % (len(possibleCharacters), c2add), {"e": "Pick an existing character", "n": "Use what I wrote"})
                chosenCharacter = None
                while whatDo == "e" or chosenCharacter:
                    chosenCharacter = resultViewer(possibleCharacters, True)
                    if not chosenCharacter:
                        whatDo = optionPicker("Found %d character(s) with similar name to '%s'. What would you like to do?" % (len(possibleCharacters), c2add), {"e": "Pick an existing character", "n": "Use what I wrote"})
                    else:
                        break
                # Use existing character
                if chosenCharacter:
                    if chosenCharacter.name in charactersToAdd:
                        print("That character is already in this game!\n")
                    else:
                        print("Adding '%s'...\n" % chosenCharacter.name)
                        charactersToAdd.append(chosenCharacter.name)
                # Use the value I inserted
                elif whatDo == "n":
                    if c2add in charactersToAdd:
                        print("That character is already in this game!")
                    else:
                        print("Adding '%s'...\n" % c2add)
                        charactersToAdd.append(c2add)
                else:
                    print("Cancelling that insert...\n")
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
    if rdb.getGameByTitle(newGame):
        print("That game already exists in the database!")
        return
    else:
        # Get release date
        releaseDate = None
        while not releaseDate:
            releaseDate = input("Enter the game's release date (YYYY-MM-DD) (or q to cancel): ")
            print()
            # Verify format
            if validDate(releaseDate):
                break
            if releaseDate.lower == "q": 
                print("Cancelling insertion...")
                return
            releaseDate = None
            print("Format invalid. Please enter the release date in the proper format!")
        # Get characters
        charactersToAdd = addCharacters([])
        if not charactersToAdd: return
        # Write the file
        print("Creating file for game...", end="")
        if fm.writeGameFile(newGame, releaseDate, charactersToAdd): print("Done")
        else:
            print(f"\nAn error occurred during file creation.\nPlease check the {path} folder or try again later.\n")
            return
        # Insert into the database
        print("Adding to database...", end="")
        rdb.insertGame(newGame, releaseDate)
        priorityInserts = []    # Characters who already exist in the db should get priority (aides in the dynamic calculation of RN)
        if len(charactersToAdd) > 1: priorityInserts = [x.name for x in rdb.getCharactersByNames(tuple(charactersToAdd))]
        for x in priorityInserts:
            if x in charactersToAdd:
                charactersToAdd.remove(x)
        if priorityInserts: rdb.insertCharactersToGame(priorityInserts, newGame)
        if charactersToAdd: rdb.insertCharactersToGame(charactersToAdd, newGame)
        print("Done")

def addToGame():
    # Get game to add to
    gameToAddTo = removeIllegalChars(input("Enter game title: "))
    print()
    if gameToAddTo:
        # Verify game in DB and cross-check with user
        gameToAddTo = rdb.getGamesLikeTitle(gameToAddTo)
        if not gameToAddTo:
            print("That game does not exist in the database! Try inserting the game yourself.")
        else:
            gameToAddTo = resultViewer(gameToAddTo, True)
            if gameToAddTo:
                gameToAddTo = gameToAddTo.title
                # Start receiving character input
                charactersToAdd = [x.name for x in rdb.getCharactersByGame(gameToAddTo)]
                charactersToAdd = addCharacters(charactersToAdd)
                if not charactersToAdd: return
                # Write the file
                print("Writing to file...", end="")
                currChars = [x.name for x in rdb.getCharactersByGame(gameToAddTo)]
                for c in currChars:
                    if c in charactersToAdd:
                        charactersToAdd.remove(c)
                if fm.appendGameFile(gameToAddTo, charactersToAdd): print("Done")
                else:
                    print(f"\nAn error occurred during file insertion.\nPlease check {gameToAddTo}.txt in {path} or try again later.")
                    return
                # Insert into the database
                print("Adding to database...", end="")
                priorityInserts = []
                if len(charactersToAdd) > 1: priorityInserts = [x.name for x in rdb.getCharactersByNames(tuple(charactersToAdd))]
                for x in priorityInserts:
                    if x in charactersToAdd:
                        charactersToAdd.remove(x)
                if priorityInserts: rdb.insertCharactersToGame(priorityInserts, gameToAddTo)
                if charactersToAdd: rdb.insertCharactersToGame(charactersToAdd, gameToAddTo)
                print("Done")
            else:
                print("Invalid input. Cancelling action...")
    else:
        print("Nothing entered. Cancelling action...")

def removeFromDatabase():
    # Remove character
    def removeCharacter():
        # Remove from select game
        def removeFromGame(cName, gTitle):
            if fm.removeCharacterFromGame(cName, gTitle):   # Remove from local files
                rdb.removeCharacterFromGame(cName, gTitle)  # Remove from db
                print("Removed '%s' from '%s'" % (cName, gTitle))
            else:
                print(f"An error occurred during file removal.\nPlease check {path}/{gTitle} and try again.")

        # Select character
        c = removeIllegalChars(input("Enter character name: "))
        c = resultViewer(rdb.getCharactersLikeName(c), True)
        if c:
            # Select where to remove
            option = optionPicker("Where would you like to remove the character?", {"g": "From one game", "a": "From all games (the entire database)"})
            print()
            if option == "g":
                # Remove from a select game
                print("Select a game to remove '%s' from:\n" % c.name)
                g = resultViewer(c.appears_in, True)
                if g:
                    confirmDelete = input("You are about to remove '%s'\nfrom the game '%s'\n\nAre you sure you want to proceed? (y/n): " % (c.name, g)).lower()
                    print()
                    if confirmDelete == "y":
                        removeFromGame(c.name, g)
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
                        removeFromGame(c.name, g)
                    rdb.removeCharacter(c.name)
                else:
                    print("Cancelling...")
            else:
                print("Cancelling...")
        else:
            print("No character selected. Cancelling...")

    # Remove game
    def removeGame():
        g = removeIllegalChars(input("Enter game title: "))
        g = resultViewer(rdb.getGamesLikeTitle(g), True)
        if g:
            confirmDelete = input("You are about to remvove the game:\n'%s'\nAre you sure you want to proceed? (y/n): " % g.title).lower()
            if confirmDelete == "y":
                if fm.removeGame(g.title):  # Remove from local files
                    rdb.removeGame(g.title) # Remove from db
                    print("'%s' successfully removed" % g.title)
                else:
                    print(f"An error occurred during file removal.\nPlease check {path}/{g.title} and try again later.")
        else:
            print("No game selected. Cancelling...")

    # Select what to remove
    option = optionPicker("What would you like to remove?", {"c": "Character", "g": "Game"})
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
                c = rdb.getCharacterByName(oldName)
                if not fm.updateCharacterName(c, newName):
                    print(f"An error occurred during file updating.\nPlease check {path} and try again later.")
                    return

            newName = removeIllegalChars(input("Enter new name: "))
            print()
            existing = rdb.getCharacterByName(newName)
            if existing:    # Overwriting character
                confirmUpdate = input("A character with that name already exists:\n\n%s\n\nThis will merge that character with '%s'.\nProceed? (y/n): " % (existing.printSelf(), oldName))
                print()
                if confirmUpdate.lower() == "y":
                    updateFiles(oldName, existing.name)
                    c = rdb.getCharacterByName(oldName)
                    for g in c.appears_in:
                        rdb.insertCharactersToGame([oldName], g)
                    else:
                        rdb.removeCharacter(oldName)
                    print("Changes made successfully.\n(NOTE: Some Ryu Numbers may not have updated accordingly.\n To fix this, you may need to reset the database.)")
                else:
                    print("Update cancelled.")
            else:           # Not overwriting character
                confirmUpdate = input("You are about to change the following character's name:\n\n%s\n\t↓\n%s\n\nConfirm update? (y/n): " % (oldName, newName))
                print()
                if confirmUpdate.lower() == "y":
                    updateFiles(oldName, newName)
                    rdb.updateCharacterName(oldName, newName)
                    print("Changes made successfully.")
                else:
                    print("Update cancelled.")

        # Query character
        c = removeIllegalChars(input("Enter character name: "))
        print()
        results = rdb.getCharactersLikeName(c)
        # Select character
        c = resultViewer(results, True)
        if c:
            # Decide what to update and what to change it to
            # NOTE: Right now, the only attribute characters have is `name`, but more functionality could be possible in the future
            attribute = optionPicker("What would you like to update?", {"n": "Name"})
            print()
            if attribute == "n":    # Update name
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
            if rdb.getGameByTitle(newTitle):
                print("A game with that name already exists! Cancelling the action...")
            else:
                confirmUpdate = input("You are about to change the following game's title:\n\n%s\n\t↓\n%s\n\nConfirm update? (y/n): " % (oldTitle, newTitle))
                if confirmUpdate.lower() == "y":
                    if fm.updateGameTitle(oldTitle, newTitle):  # Update in local files
                        rdb.updateGameTitle(oldTitle, newTitle) # Update in db
                        print("Changes made successfully.")         
                    else:
                        print(f"An error occurred during file operations.\nPlease check {path} and try again later.")          
                else:
                    print("Update cancelled.")

        # Update release date
        def updateReleaseDate(gameTitle):
            newRDate = input("Enter new release date (YYYY-MM-DD): ")
            print()
            if validDate(newRDate):
                confirmUpdate = input("You are about to change the release date for:\n\n%s\n\nTo the following:\n\n%s\n\t↓\n%s\n\nConfirm update? (y/n): " % (gameTitle, g.release_date, newRDate))
                if confirmUpdate.lower() == "y":
                    if fm.updateGameReleaseDate(gameTitle, newRDate):   # Update in local files
                        rdb.updateGameReleaseDate(gameTitle, newRDate)  # Update in db
                        print("Changes made successfully.")
                    else:
                        print(f"An error occurred during file operations.\nPlease check {path} and try again later.")
                else:
                    print("Update cancelled.")
            else:
                print("Date entered is invalid. Cancelling the update...")

        # Query game
        g = removeIllegalChars(input("Enter game title: "))
        print()
        results = rdb.getGamesLikeTitle(g)
        # Select game
        g = resultViewer(results, True)
        if g:
            # Decide what to update and what to change it to
            attribute = optionPicker("What would you like to update?", {"t": "Title", "r": "Release Date"})
            print()
            if attribute== "t":         # Update title
                updateTitle(g.title)
            elif attribute == "r":      # Update release date
                updateReleaseDate(g.title)                    
            else:
                print("No valid option selected. Cancelling the operation...")
        else:
            print("No game selected. Cancelling the operation...")

    # Decide what to do
    action = optionPicker("Which would you like to update?", {"c": "Character", "g": "Game"})
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
    response = input("This command may take some time to execute.\nAre you sure you want to reset the database? (y/n): ")
    print()
    if response.lower() in ["y", "yes", "yea", "ye"]:
        maintenance.reset_db(not detailed, detailed)
    else:
        print("Cancelling...")

### END FUNCTIONS ###

def main():
    command = ""
    menuStyle = "default"
    while (command != "Q" and command != "q"):
        print(MENU_COMPACT if menuStyle == "compact" else MENU)
        command = input().strip()
        print()
        if command != "":
            if command.lower() == "c":
                queryCharacter(True if command == "C" else False)
            elif command.lower() == "g":
                queryGame(True if command == "G" else False)
            elif command.lower() == "p":
                getPath(int(command[1:]) if command[1:] else defaultLimiter)
            elif command.lower() == "n":
                getStats()
            elif command.lower() == "i":
                insertGame()
            elif command.lower() == "a":
                addToGame()
            elif command.lower() == "x":
                removeFromDatabase()
            elif command.lower() == "u":
                updateData()
            elif command.lower() == "v":
                menuStyle = toggleView(menuStyle)
            elif command.lower() == "r":
                resetDatabase(True if command == "R" else False)
            elif command.lower() == "q":
                print("Thank you for using the Ryu Database! :)")
            else:
                print("Command not recognized. Please try again")
    quit()


if __name__ == "__main__":
    main()