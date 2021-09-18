import game
import game_character
import maintenance
import ryu_number

### BEGIN CONSTANTS ###

MENU = "\n+------------------RYU DATABASE------------------+\n\
|         Enter a letter to get started.         |\n\
|                                                |\n\
+---QUERY COMMANDS-------------------------------+\n\
|                                                |\n\
| (c/C) Query a character (exactly)              |\n\
|       [num] Limit visible games                |\n\
|             Default = 4; All = -1;             |\n\
| (g/G) Query a game (exactly)                   |\n\
| (i/I) Insert a game and characters into the DB |\n\
|                                                |\n\
+---ALTER DATABASE COMMANDS----------------------+\n\
|                                                |\n\
| (a/A) Add characters to an existing game       |\n\
| (x/X) Remove a character from the db entirely  |\n\
|                                                |\n\
+---MAINTENANCE----------------------------------+\n\
|                                                |\n\
| (p/P) Get a path from a character to Ryu       |\n\
|       [num] Limit visible games                |\n\
|             Default = 4; All = -1;             |\n\
| (r/R) Reset the database (include all details) |\n\
| (q/Q) Close the database and quit              |\n\
|                                                |\n\
+------------------------------------------------+\n\
|   (Note: brackets in desc. = capital letter)   |\n\
+------------------------------------------------+\n"
illegalCharacters = ["/", "\\", ":", "*", "?", "\"", "'", "<", ">", "|", "'", "`", "%"]
path = "Games List"
defaultLimiter = 4

### END CONSTANTS ###

def queryCharacter(exact = False, limiter = defaultLimiter):
    charToQuery = input("Please enter a character's name%s" % (" exactly: " if exact else ": "))
    print()
    if exact:       # Querying by exact name (myCharacters is a game_character object)
        myCharacters = game_character.getByNameExact(charToQuery)
        if myCharacters:
            print(myCharacters.printSelf(limiter))
        else:
            print("No characters by that name could be found")        
    else:           # Querying by generalized name (myCharacters is a list of game_character objects)
        myCharacters = game_character.getByNameExact(charToQuery) if exact else game_character.getByName(charToQuery)  
        if myCharacters:
            for i in range(len(myCharacters)):
                print("(Result %d): %s\n" % (i + 1, myCharacters[i].printSelf(limiter)))
        else:
            print("No characters by that name could be found")

def queryGame(exact = False):
    gameToQuery = input("Please enter a game name%s" % (" exactly: " if exact else ": "))
    myGames = game.getByTitleExact(gameToQuery) if exact else game.getByTitle(gameToQuery)
    print()
    if exact:           # Querying by exact title (myGames is a game object)
        if myGames:
            print(myGames)
        else:
            print("No games by that name could be found")
    else:               # Querying by generalized title (myGames is a list of game objects)
        if myGames:
            for i in range(len(myGames)):
                print("(Result %d): %s\n" % (i + 1, myGames[i]))
        else:
            print("No games by that name could be found")

def addCharacters(charactersToAdd = []):
    c2add = None
    while not c2add:
        # Receive input
        c2add = input("Enter character name, or enter '.' to cancel the insert (enter nothing to finish):\n")
        print()
        for c in illegalCharacters:
            c2add = c2add.replace(c, "")
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
                print("\nWhat would you like to do?\n[num] Use that character name\n[n/N] Use what I wrote\n[anything else] Enter another name\n")
                whatDo = input()
                # Number is inputted, use that value
                if whatDo.isnumeric() and int(whatDo) < len(possibleCharacters):
                    if possibleCharacters[int(whatDo)].name in charactersToAdd:
                        print("That character is already in this game!")
                    else:
                        print("Adding '%s'..." % possibleCharacters[int(whatDo)].name)
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
    newGame = input("Enter the game's name: ")
    print()
    for c in illegalCharacters:
        newGame = newGame.replace(c, "")
    if game.getByTitleExact(newGame):
        print("That game already exists in the database!")
    else:
        # Get release date
        releaseDate = None
        while not releaseDate:
            releaseDate = input("Enter the game's release date (YYYY-MM-DD): ")
            print()
            # Verify format
            if len(releaseDate) == 10:
                if releaseDate[0:4].isnumeric() and releaseDate[5:7].isnumeric() and releaseDate[8:10].isnumeric() and releaseDate[4] == "-" and releaseDate[7] == "-":
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
    gameToAddTo = input("Enter game title: ")
    print()
    # Verify game in DB and cross-check with user
    gameToAddTo = game.getByTitle(gameToAddTo)
    if not gameToAddTo:
        print("That game does not exist in the database! Try inserting the game yourself.")
    else:
        for i in range(len(gameToAddTo)):
            print("(%d) %s" % (i, gameToAddTo[i]))
        gameIndex = input("\nPlease select which game to add to (int): ")
        if gameIndex.isnumeric() and int(gameIndex) < len(gameToAddTo):
            gameToAddTo = gameToAddTo[int(gameIndex)].title
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
                charToRemove = myChars[charIndex]
                for myGame in charToRemove.appears_in:
                    myGame = myGame.title
                    print("Opening %s/%s.txt" % (path, myGame))
                    with open("%s/%s.txt" % (path, myGame), "r+") as f:
                        lines = f.readlines()
                        print(lines)
                        f.seek(0)
                        for line in lines:
                            print("%s vs %s" % (line.strip("\n"), charToRemove.name))
                            if line.strip("\n") != charToRemove.name:
                                f.write(line)
                        f.truncate()
                print("'%s' removed successfully.\nNOTE: This change will only be noticed when the database is reset." % charToRemove.name)
        else:
            print("Number not in range. Cancelling...")
    else:
        print("You have not entered a number. Cancelling...")

def resetDatabase(detailed = False):
    response = input("This command will take *a while* to execute.\nAre you sure you want to reset the database? (y/n): ")
    print()
    if response.lower() in ["y", "yes", "yea", "ye", "ok", "okay"]:
        maintenance.reset_db(not detailed, detailed)
    else:
        print("Cancelling...")

def getPath(limiter = defaultLimiter):
    charToPath = input("Enter the character's name: ")
    print()
    characterToQuery = game_character.getByName(charToPath)
    if not characterToQuery:
        print("No character by that name could be found in the database.")
        return
    for i in range(len(characterToQuery)): 
        print("(%d) %s" % (i, characterToQuery[i].name))
    charIndex = input("\nWhich character are you referring to? (int)\n")
    print()
    if charIndex.isnumeric() and int(charIndex) < len(characterToQuery):
        print("Input was %d" % int(charIndex))
        print("Retrieving %s" % characterToQuery[int(charIndex)].name)
        p = ryu_number.getPathFromCharacter(characterToQuery[int(charIndex)].name) # Get the path
        if p:       # If the path actually exists
            for elem in p:
                if isinstance(elem, game_character.game_character):
                    print("%s" % (elem.printSelf(limiter)))
                else:
                    print("(%d) %s" % (elem.ryu_number, elem.title))
        else:
            print("Something went *really* wrong. Like, super wrong. Like, you shouldn't be able to see this text at all. If you are, CONTACT ME PLEASE")
    else:
        print("Invalid input. Cancelling...")

def main():
    command = ""
    while (command != "Q" and command != "q"):
        print(MENU)
        command = input().strip()
        print()
        if command[0].lower() == "c" and (command[1:].isnumeric() or len(command) == 1 or (command[1] == "-" and command[2:].isnumeric())):
            queryCharacter(True if command[0] == "C" else False, int(command[1:]) if command[1:] else defaultLimiter)
        elif command.lower() == "g":
            queryGame(True if command == "G" else False)
        elif command.lower() == "i":
            insertGame()
        elif command.lower() == "a":
            addToGame()
        elif command.lower() == "x":
            removeCharacter()
        elif command.lower() == "r":
            resetDatabase(True if command == "R" else False)
        elif command[0].lower() == "p" and (command[1:].isnumeric() or len(command) == 1 or (command[1] == "-" and command[2:].isnumeric())):
            getPath(int(command[1:]) if command[1:] else defaultLimiter)
        elif command == "q" or command == "Q":
            print("Thank you for using the Ryu Database! :)")
        else:
            print("Command not recognized. Please try again")
    quit()


if __name__ == "__main__":
    main()