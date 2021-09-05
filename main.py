import game
import game_character
import maintenance
import ryu_number

MENU = "\n+------------------RYU DATABASE------------------+\n\
|         Enter a letter to get started.         |\n\
|                                                |\n\
| (c/C) Query a character (exactly)              |\n\
| (g/G) Query a game (exactly)                   |\n\
| (r/R) Reset the database (include all details) |\n\
| (p/P) Get a path from a character to Ryu       |\n\
| (q/Q) Close the database and quit              |\n\
|                                                |\n\
|   (Note: brackets in desc. = capital letter)   |\n\
+------------------------------------------------+\n"

def queryCharacter(exact = False):
    charToQuery = input("Please enter a character's name%s" % (" exactly: " if exact else ": "))
    myCharacters = game_character.getByNameExact(charToQuery) if exact else game_character.getByName(charToQuery)
    if exact:
        if myCharacters:
            print(myCharacters)
        else:
            print("No characters by that name could be found")
    else:
        if myCharacters:
            for i in range(len(myCharacters)):
                print("(Result %d): %s" % (i + 1, myCharacters[i]))
        else:
            print("No characters by that name could be found")

def queryGame(exact = False):
    gameToQuery = input("Please enter a game name%s" % (" exactly: " if exact else ": "))
    myGames = game.getByTitleExact(gameToQuery) if exact else game.getByTitle(gameToQuery)
    if exact:
        if myGames:
            print(myGames)
        else:
            print("No games by that name could be found")
    else:
        if myGames:
            for i in range(len(myGames)):
                print("(Result %d): %s" % (i + 1, myGames[i]))
        else:
            print("No games by that name could be found")

def resetDatabase(detailed = False):
    response = input("This command will take a while to execute.\nAre you sure you want to reset the database? (y/n): ")
    if response.lower() in ["y", "yes", "yea", "ye", "ok", "okay"]:
        maintenance.reset_db(not detailed, detailed)
    else:
        print("Cancelling...")

def getPath():
    charToPath = input("Enter the character's name (as accurately as possible): ")
    p = ryu_number.getPathFromCharacter(charToPath)
    if p:
        for elem in p:
            if isinstance(elem, game_character.game_character):
                print("(%d) Name: %s" % (elem.ryu_number, elem.name))
                for g in elem.appears_in:
                    print("\t%s" % g.title)
            else:
                print("(%d) Title: %s" % (elem.ryu_number, elem.title))
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