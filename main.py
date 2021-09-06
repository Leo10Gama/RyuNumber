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
| (r/R) Reset the database (include all details) |\n\
| (p/P) Get a path from a character to Ryu       |\n\
| (q/Q) Close the database and quit              |\n\
|                                                |\n\
|   (Note: brackets in desc. = capital letter)   |\n\
+------------------------------------------------+\n"

def queryCharacter(exact = False):
    limiter = 4     # Limiter will limit how many "appears_in" games show
    charToQuery = input("Please enter a character's name%s" % (" exactly: " if exact else ": "))
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

def insertGame():
    path = "Games List"
    # newGame contains the name of the game to be inserted
    # Parse it with characters that can be used in text file names
    illegalCharacters = ["/", "\\", ":", "*", "?", "\"", "'", "<", ">", "|", "'", "`"]
    newGame = input("Enter the game's name: ")
    for c in illegalCharacters:
        newGame.replace(c, "")
    if game.getByTitleExact(newGame):
        print("That game already exists in the database!")
    else:
        # Get release date
        releaseDate = None
        while not releaseDate:
            releaseDate = input("Enter the game's release date (YYYY-MM-DD): ")
            # Verify format
            if len(releaseDate) == 10:
                if releaseDate[0:4].isnumeric() and releaseDate[5:7].isnumeric() and releaseDate[8:10].isnumeric() and releaseDate[4] == "-" and releaseDate[7] == "-":
                    break
            releaseDate = None
            print("Format invalid. Please enter the release date in the proper format!")
        # Get characters
        charactersToAdd = []
        c2add = None
        while not c2add:
            # Receive input
            c2add = input("Enter character name, or enter '.' to cancel the insert (enter nothing to finish):\n")
            # Query if character already exists
            if c2add == ".":
                return
            if c2add:
                possibleCharacters = game_character.getByName(c2add)
                # If character exists, prompt to pick one of them or the entered value, or some other value entirely
                if possibleCharacters:
                    print("Found %d character(s) with similar name:\n" % len(possibleCharacters))
                    for i in range(len(possibleCharacters)):
                        print("(%d) %s" % (i, possibleCharacters[i].name))
                    print("\nWhat would you like to do?\n[num] Use that character name\n[n/N] Use what I wrote\n[anything else] Enter another name")
                    whatDo = input()
                    # Number is inputted, use that value
                    if whatDo.isnumeric() and int(whatDo) < len(possibleCharacters):
                        charactersToAdd.append(possibleCharacters[int(whatDo)].name)
                    # Use the value I inserted
                    elif whatDo.lower() == "n":
                        charactersToAdd.append(c2add)
                else:
                    charactersToAdd.append(c2add)
                c2add = None
            else:
                c2add = "owo"
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
        priorityInserts = [x.name for x in game_character.getManyByNames(tuple(charactersToAdd))]
        for x in priorityInserts:
            if x in charactersToAdd:
                charactersToAdd.remove(x)
        game_character.insertCharactersToGame(priorityInserts, newGame)
        game_character.insertCharactersToGame(charactersToAdd, newGame)
        print("Done")

def resetDatabase(detailed = False):
    response = input("This command will take a while to execute.\nAre you sure you want to reset the database? (y/n): ")
    if response.lower() in ["y", "yes", "yea", "ye", "ok", "okay"]:
        maintenance.reset_db(not detailed, detailed)
    else:
        print("Cancelling...")

def getPath():
    limiter = 4     # Limit how many "appears_in" games are displayed
    charToPath = input("Enter the character's name (as accurately as possible): ")
    p = ryu_number.getPathFromCharacter(charToPath) # Get the path
    if p:       # If the path actually exists
        for elem in p:
            if isinstance(elem, game_character.game_character):
                print("%s" % (elem.printSelf(limiter)))
            else:
                print("(%d) %s" % (elem.ryu_number, elem.title))
        print("\nNote: if this isn't the character you meant to search, try querying that character first and use that name!")
    else:
        print("No character by that name could be found")

def main():
    command = ""
    while (command != "Q" and command != "q"):
        print(MENU)
        command = input().strip()
        if command == "c" or command == "C":
            queryCharacter(True if command == "C" else False)
        elif command == "g" or command == "G":
            queryGame(True if command == "G" else False)
        elif command == "i" or command == "I":
            insertGame()
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