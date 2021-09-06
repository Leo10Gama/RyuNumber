import game
import game_character
import maintenance
import ryu_number

MENU = "\n+------------------RYU DATABASE------------------+\n\
|         Enter a letter to get started.         |\n\
|                                                |\n\
| (c/C) Query a character (exactly)              |\n\
| (g/G) Query a game (exactly)                   |\n\
| (i/I) Insert a game and characters into the DB |\n\
| (a/A) Add characters to an existing game       |\n\
| (r/R) Reset the database (include all details) |\n\
| (p/P) Get a path from a character to Ryu       |\n\
| (q/Q) Close the database and quit              |\n\
|                                                |\n\
|   (Note: brackets in desc. = capital letter)   |\n\
+------------------------------------------------+\n"
illegalCharacters = ["/", "\\", ":", "*", "?", "\"", "'", "<", ">", "|", "'", "`", "%"]

def queryCharacter(exact = False):
    limiter = 4     # Limiter will limit how many "appears_in" games show
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
                print("(Result %d): %s" % (i + 1, myCharacters[i].printSelf(limiter)))
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
                print("(Result %d): %s" % (i + 1, myGames[i]))
        else:
            print("No games by that name could be found")

def addCharacters():
    charactersToAdd = []
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
                    print("Adding '%s'..." % possibleCharacters[int(whatDo)].name)
                    charactersToAdd.append(possibleCharacters[int(whatDo)].name)
                # Use the value I inserted
                elif whatDo.lower() == "n":
                    print("Adding '%s'..." % c2add)
                    charactersToAdd.append(c2add)
                else:
                    print("Cancelling that insert...")
            else:
                whatDo = input("'%s' does not exist in the database yet.\nAdd them anyway? (y/n): " % c2add)
                if whatDo.lower() in ["y", "ye", "yes", "yea"]:
                    print("\nAdding '%s'..." % c2add)
                    charactersToAdd.append(c2add)
                else:
                    print("\nCancelling that insert...")
            c2add = None
        else:
            c2add = "owo"
    return charactersToAdd

def insertGame():
    path = "Games List"
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
    path = "Games List"
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
            charactersToAdd = addCharacters()
            if not charactersToAdd: return
            # Write the file
            print("Writing to file...", end="")
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

def resetDatabase(detailed = False):
    response = input("This command will take *a while* to execute.\nAre you sure you want to reset the database? (y/n): ")
    print()
    if response.lower() in ["y", "yes", "yea", "ye", "ok", "okay"]:
        maintenance.reset_db(not detailed, detailed)
    else:
        print("Cancelling...")

def getPath():
    limiter = 4     # Limit how many "appears_in" games are displayed
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
        if command == "c" or command == "C":
            queryCharacter(True if command == "C" else False)
        elif command == "g" or command == "G":
            queryGame(True if command == "G" else False)
        elif command == "i" or command == "I":
            insertGame()
        elif command == "a" or command == "A":
            addToGame()
        elif command == "r" or command == "R":
            resetDatabase(True if command == "R" else False)
        elif command == "p" or command == "P":
            getPath()
        elif command == "q" or command == "Q":
            print("Thank you for using the Ryu Database! :)")
        else:
            print("Command not recognized. Please try again")
    quit()


if __name__ == "__main__":
    main()