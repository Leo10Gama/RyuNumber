"""The main driver method for interacting with the Ryu Database.

This method contains all necessary methods for interacting with the
database. These commands are visible from the `MENU` or `MENU_COMPACT`
interfaces, which provide brief descriptions of each interaction.

The possible ways to interact with the database include querying
characters, querying games, retrieving a path from a character to Ryu,
seeing the stats of the database, inserting characters and games,
appending characters to existing games, removing things from the 
database, updating things in the database, and resetting the database.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, TypeVar

from classes import file_manager as fm
from classes.nodes import Node, game, game_character
import methods.maintenance as maintenance
from methods import ryu_database as rdb

### BEGIN CONSTANTS ###

class MenuStyle(Enum):
    DEFAULT = auto()
    COMPACT = auto()

MENU = (f"\n+------------------RYU DATABASE------------------+\n"
          f"|         Enter a letter to get started.         |\n"
          f"|                                                |\n"
          f"+---QUERY COMMANDS-------------------------------+\n"
          f"|                                                |\n"
          f"| (c/C) Query a character (exactly)              |\n"
          f"| (g/G) Query a game (exactly)                   |\n"
          f"| (p/P) Get a path from a character to Ryu       |\n"
          f"| (n/N) See stats about the database             |\n"
          f"|                                                |\n"
          f"+---ALTER DATABASE COMMANDS----------------------+\n"
          f"|                                                |\n"
          f"| (i/I) Insert a game and characters into the DB |\n"
          f"| (a/A) Add characters to an existing game       |\n"
          f"| (x/X) Remove an item from the database         |\n"
          f"| (u/U) Update a character or game               |\n"
          f"|                                                |\n"
          f"+---MAINTENANCE----------------------------------+\n"
          f"|                                                |\n"
          f"| (v/V) Toggle view to be compact or descriptive |\n"
          f"| (r/R) Reset the database (include all details) |\n"
          f"| (q/Q) Close the database and quit              |\n"
          f"|                                                |\n"
          f"+------------------------------------------------+\n"
          f"|   (Note: brackets in desc. = capital letter)   |\n"
          f"+------------------------------------------------+\n"
)

MENU_COMPACT = (f"\n+------------------RYU DATABASE------------------+\n"
                  f"|         Enter a letter to get started.         |\n"
                  f"|                                                |\n"
                  f"| (c/C) Query a character (exactly)              |\n"
                  f"| (g/G) Query a game (exactly)                   |\n"
                  f"| (p/P) Get a path from a character to Ryu       |\n"
                  f"| (n/N) See stats about the database             |\n"
                  f"| (i/I) Insert a game and characters into the DB |\n"
                  f"| (a/A) Add characters to an existing game       |\n"
                  f"| (x/X) Remove an item from the database         |\n"
                  f"| (u/U) Update a character or game               |\n"
                  f"| (v/V) Toggle view to be compact or descriptive |\n"
                  f"| (r/R) Reset the database (include all details) |\n"
                  f"| (q/Q) Close the database and quit              |\n"
                  f"|                                                |\n"
                  f"+------------------------------------------------+\n"
                  f"|   (Note: brackets in desc. = capital letter)   |\n"
                  f"+------------------------------------------------+\n"
)

PATH = "Games List"

illegalCharacters = ["/", "\\", ":", "*", "?", "\"", "'", "<", ">", "|", "'", "`", "%"]
defaultLimiter = 3

T = TypeVar('T')

### END CONSTANTS ###

### BEGIN FUNCTIONS ###

# USEFUL HELPER FUNCTIONS

def resultViewer(results: List[T], canSelect: bool=False, page: int=1, resultsPerPage: int=10, limiter: int=1) -> Optional[T]:
    """View results in terminal, and return a selected value (if specified).
    
    The function will create a window in the terminal, listing the elements
    of `results`. Each "page" contains only as many elements as specified,
    and they can only be selected if the caller allows. If elements can be
    selected, then when an element's index is entered, it is returned at the
    end of the function. As such, values assigned to be the result of this
    function will take on whatever element is selected by the user.

    Note that `page` represents the on-screen number such that the index of
    the list is exactly one fewer than `page`. In addition, the inequality
    1 <= `page` <= `totalPages` should always hold.

    Parameters
    ----------
    results: List[T]
        A list of all the elements to be selected from.
    canSelect: bool
        Whether or not the user can select a result from the list. 
        (Default is False)
    page: int
        Which page number to show results from. (Default is 1)
    resultsPerPage: int
        How many results to show on a single page. (Default is 10)
    limiter: int
        How many additional lines certain objects take up in the viewer. This
        primarily affects the `appears_in` field of game_character objects.
        (Default is 1)

    Returns
    -------
    T | None
        Either an element selected from the list (if canSelect is True), or None
        if either canSelect is False, or an invalid selection is made.
    """
    prompt: str = "(p) Previous page\n(n) Next page\n(#) Select this one\n(*) Close view\n\n" if canSelect else "(p) Previous page\n(n) Next page\n(*) Close view\n\n"
    cmd: str = "."
    totalPages: int = int(len(results) / resultsPerPage)
    if len(results) % resultsPerPage != 0: totalPages += 1
    while cmd:
        print(f"======================== RESULT  VIEWER ========================")   # Header
        # Print all results
        print(f"\t{len(results)} results:\n")
        for i in range((page - 1) * resultsPerPage, min(((page - 1) * resultsPerPage) + resultsPerPage, len(results))):
            print(f"({i + 1}) {results[i].printSelf(limit=limiter, withRn=False) if issubclass(type(results[i]), Node) else results[i]}")
        else:
            print()
        # NAV BAR AT THE BOTTOM
        # Print prefix part
        print(f"<(p) ", end="")
        if page > 2:
            print(f"1 ", end="")
        if page > 3:    # Print prefix dots (maybe)
            print(f"... ", end="")
        # Print current selection
        if page == 1:   
            print("{%d} " % page, end="")
            if page + 1 <= totalPages:
                print(f"{page + 1} ", end="")
        else:
            print("%d {%d} " % (page - 1, page), end="")    # Previous and current number
            if page + 1 <= totalPages:  # Next number (if possible)
                print(f"{page + 1} ", end="")
        if page < totalPages - 2:   # Print suffix dots (maybe)
            print(f"... ", end="")
        # Print suffix part
        if (page + 1) <= totalPages - 1:
            print(f" {totalPages} ", end="")
        print(f"(n)>\n================================================================\n")   # Footer
        # Prompt next action
        cmd = input(prompt).lower()
        print()
        if cmd != "" and not canSelect: cmd = cmd[0]
        if cmd.isnumeric() and canSelect:
            cmd = int(cmd)
            if cmd >= 1 and cmd <= len(results):
                print(f"Selected option ({cmd}): {results[cmd - 1].primary_key if isinstance(results[cmd - 1], Node) else results[cmd - 1]}\n")
                return results[cmd - 1]
        if cmd != "p" and cmd != "n": cmd = ""
        if cmd == "p":
            if page > 1: page -= 1
            else: print(f"This is the first page; cannot go back\n")
        elif cmd == "n":
            if page + 1 <= totalPages: page += 1
            else: print(f"This is the last page; cannot go further\n")
    return None

def optionPicker(prompt: str, choices: Dict[str, str]) -> str:
    """Allow the user to select an option from a list of choices.
    
    Parameters
    ----------
    prompt: str
        A prompt of what the user is being asked to select.
    choices: Dict[str, str]
        A dictionary where the key is a single lowercase character, and its
        value is the option that will be selected.

    Returns
    -------
    str
        A lowercase string entered by the user.
    """
    print(f"{prompt}\n")
    for option in choices:
        print(f"({option}) {choices[option]}")
    print("(*) Cancel\n")
    return input().lower()

def validDate(date: str) -> bool:
    """Return whether a string follows the format of ####-##-##."""
    if len(date) == 10:
        return date[0:4].isnumeric() and date[5:7].isnumeric() and date[8:10].isnumeric() and date[4] == "-" and date[7] == "-"
    return False

def removeIllegalChars(s: str) -> str:
    """Returns a string without any illegal characters.
    
    The illegal characters that are removed are those defined in
    main.illegalCharacters.
    """
    if s:
        for c in illegalCharacters:
            s = s.replace(c, "")
    return s

# QUERY FUNCTIONS

def queryCharacter(exact: bool=False, limiter: int=-1) -> None:
    """Find a character in the database.
    
    Parameters
    ----------
    exact: bool
        Whether or not to query the given name exactly. If False, names will be
        queried that contain the name as a substring. (Default is False)
    limiter: int
        How many `appears_in` values to display. (Default is -1, which prints
        all)
    """
    charToQuery: str = removeIllegalChars(input("Please enter a character's name%s" % (" exactly: " if exact else ": ")))
    print()
    if charToQuery:
        if exact:       # Querying by exact name (myCharacters is a game_character object)
            myCharacters: Optional[game_character] = rdb.getCharacterByName(charToQuery)
            if myCharacters:
                print(myCharacters.printSelf(limiter, withRn = True))
            else:
                print("No characters by that name could be found")        
        else:           # Querying by generalized name (myCharacters is a list of game_character objects)
            myCharacters: Optional[List[game_character]] = rdb.getCharactersLikeName(charToQuery)  
            if myCharacters:
                myChar: Optional[game_character] = resultViewer(myCharacters, canSelect=True)
                if myChar:
                    print(myChar.printSelf(withRn=True))
            else:
                print("No characters by that name could be found")
    else:
        print("Nothing has been entered. Cancelling query...")

def queryGame(exact=False) -> None:
    """Find a game in the database
    
    The parameter exact (default value False) is whether or not to query the
    given title exactly. If False, titles will be queried that contain that
    title as a substring.

    After selecting a game, a prompt will also appear to view the characters
    in that game.
    """
    gameToQuery = removeIllegalChars(input("Please enter a game name%s" % (" exactly: " if exact else ": ")))
    print()
    if gameToQuery:
        if exact:           # Querying by exact title (myGames is a game object)
            g: Optional[game] = rdb.getGameByTitle(gameToQuery)
            if g:
                print(g.printSelf(withRn = True))
            else:
                print("No games by that name could be found")
                return
        else:               # Querying by generalized title (myGames is a list of game objects)
            myGames: Optional[List[game]] = rdb.getGamesLikeTitle(gameToQuery)
            if myGames:
                g: game = resultViewer(myGames, canSelect=True, resultsPerPage=20)
                if g:
                    print(g.printSelf(withRn=True))
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

def getPath(limiter: int=defaultLimiter) -> None:
    """Print a path from a character to Ryu.
    
    After selecting a character, a path from them to Ryu is provided either 
    randomly or by choice, based on whichever the user prefers.
    """

    def printPath(p: Optional[List[Node]]) -> None:
        """Print the path from a character towards Ryu."""
        if p:           # If the path actually exists
            print(f"{p[0].primary_key} has a Ryu Number of {p[0].ryu_number}\n")
            for elem in p:
                if isinstance(elem, game):
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
                p = rdb.getPathFromCharacter(myChar.name)
                printPath(p)
            elif choice == "c":
                x = myChar
                p = []
                p.append(x)
                # Choose my path
                while True:
                    x = rdb.getGameByTitle(resultViewer(rdb.stepTowardsRyu(x), True, resultsPerPage=20))
                    if x:
                        p.append(x)
                    else:
                        print("Cancelling...")
                        break
                    x = rdb.getCharacterByName(resultViewer(rdb.stepTowardsRyu(x), True, resultsPerPage=20))
                    if x:
                        p.append(x)
                        if type(x) is game_character and x.name == "Ryu":
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

def getStats() -> None:
    """Retrieve the stats of the database.
    
    These stats include either the number of games and/or the number of 
    characters. Each item is also counted per Ryu Number.
    """

    statsToSee = optionPicker("Which stats would you like to see?", {"g": "Games", "c": "Characters", "a": "All"})
    print()

    def getGames() -> None:
        """Print the number of games from Ryu Numbers 1 to max."""
        rn = 1
        val = rdb.getNumGamesWithRN(rn)
        while val:
            print(f"Games with Ryu Number {rn}: {val}")
            rn += 1
            val = rdb.getNumGamesWithRN(rn)
        print("\nTotal number of games in database: %d" % rdb.getNumGames())

    def getCharacters() -> None:
        """Print the number of characters from Ryu Numbers 0 to max."""
        rn = 0
        val = rdb.getNumCharactersWithRN(rn)
        while val:
            print(f"Characters with Ryu Number {rn}: {val}")
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

def addCharacters(charactersToAdd: List[str]=[]) -> List[str]:
    """Retrieve a list of character names.
    
    An already-started character list charactersToAdd is available as a
    parameter in the event that there are characters that already exist
    in the given game.
    """

    c2add: Optional[List[str]] = None
    while not c2add:
        # Receive input
        c2add = removeIllegalChars(input("Enter character name, or enter '.' to cancel the insert (enter nothing to finish):\n"))
        print()
        # Cancel the insert
        if c2add == ".":
            return []
        # Actually add a character
        if c2add:
            possibleCharacters: Optional[List[game_character]] = rdb.getCharactersLikeName(c2add)
            # If character exists, prompt to pick one of them or the entered value, or some other value entirely
            if possibleCharacters:
                whatDo = optionPicker(f"Found {len(possibleCharacters)} character(s) with similar name to '{c2add}'. What would you like to do?", {"e": "Pick an existing character", "n": "Use what I wrote"})
                chosenCharacter: Optional[game_character] = None
                while whatDo == "e" or chosenCharacter:
                    chosenCharacter = resultViewer(possibleCharacters, True)
                    if not chosenCharacter:
                        whatDo = optionPicker("Found {len(possibleCharacters)} character(s) with similar name to '{c2add}'. What would you like to do?", {"e": "Pick an existing character", "n": "Use what I wrote"})
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

def insertGame() -> None:
    """Insert a new game to the database.
    
    This method will retrieve the new game's title, release date, and a list
    of characters that appear in the game.
    """
    newGame: str = removeIllegalChars(input("Enter the game's name: "))
    print()
    if rdb.getGameByTitle(newGame):
        print("That game already exists in the database!")
        return
    # Get release date
    releaseDate: Optional[str] = None
    while not releaseDate:
        releaseDate = input("Enter the game's release date (YYYY-MM-DD) (or q to cancel): ")
        print()
        # Verify format
        if validDate(releaseDate):
            break
        if releaseDate.lower() == "q": 
            print("Cancelling insertion...")
            return
        releaseDate = None
        print("Format invalid. Please enter the release date in the proper format!")
    # Get characters
    charactersToAdd: List[str] = addCharacters([])
    if not charactersToAdd: return
    # Write the file
    print("Creating file for game...", end="")
    if fm.writeGameFile(newGame, releaseDate, charactersToAdd): print("Done")
    else:
        print(f"\nAn error occurred during file creation.\nPlease check the {PATH} folder or try again later.\n")
        return
    # Insert into the database
    print("Adding to database...", end="")
    if rdb.insertGame(newGame, releaseDate):
        priorityInserts = []    # Characters who already exist in the db should get priority (aides in the dynamic calculation of RN)
        if len(charactersToAdd) > 1: priorityInserts = [x.name for x in rdb.getCharactersByNames(tuple(charactersToAdd))]
        for x in priorityInserts:
            if x in charactersToAdd:
                charactersToAdd.remove(x)
        if priorityInserts: rdb.insertCharactersToGame(priorityInserts, newGame)
        if charactersToAdd: rdb.insertCharactersToGame(charactersToAdd, newGame)
        print("Done")
    else:
        print(f"\nAn error occurred during file insertion.\nPlease check the {PATH} folder or try again later.\n")
        return

def addToGame() -> None:
    """Append characters to a game that already exists in the database."""
    # Get game to add to
    gameTitle: str = removeIllegalChars(input("Enter game title: "))
    print()
    if gameTitle:
        # Verify game in DB and cross-check with user
        games: Optional[List[game]] = rdb.getGamesLikeTitle(gameTitle)
        if not games:
            print("That game does not exist in the database! Try inserting the game yourself.")
            return
        gameToAddTo: Optional[game] = resultViewer(games, True)
        if gameToAddTo:
            gameTitle = gameToAddTo.title
            # Start receiving character input
            charactersToAdd: List[str] = [x.name for x in rdb.getCharactersByGame(gameTitle)]
            charactersToAdd = addCharacters(charactersToAdd)
            if not charactersToAdd: return
            # Write the file
            print("Writing to file...", end="")
            currChars: Optional[List[str]] = [x.name for x in rdb.getCharactersByGame(gameTitle)]
            for c in currChars:
                if c in charactersToAdd:
                    charactersToAdd.remove(c)
            if fm.appendGameFile(gameTitle, charactersToAdd): print("Done")
            else:
                print(f"\nAn error occurred during file insertion.\nPlease check {gameTitle}.txt in {PATH} or try again later.")
                return
            # Insert into the database
            print("Adding to database...", end="")
            priorityInserts: List[str] = []
            if len(charactersToAdd) > 1: priorityInserts = [x.name for x in rdb.getCharactersByNames(tuple(charactersToAdd))]
            for x in priorityInserts:
                if x in charactersToAdd:
                    charactersToAdd.remove(x)
            if priorityInserts: rdb.insertCharactersToGame(priorityInserts, gameTitle)
            if charactersToAdd: rdb.insertCharactersToGame(charactersToAdd, gameTitle)
            print("Done")
        else:
            print("Invalid input. Cancelling action...")
    else:
        print("Nothing entered. Cancelling action...")

def removeFromDatabase() -> None:
    """Remove an item from the database.
    
    Things that can be removed from the database are characters (from just 
    one game or the whole database), or games.
    """

    def removeCharacter() -> None:
        """Remove a character from the database in some way."""

        def removeFromGame(cName: str, gTitle: str) -> None:
            """Remove a character from a game in both the database and local files."""
            if fm.removeCharacterFromGame(cName, gTitle):   # Remove from local files
                rdb.removeCharacterFromGame(cName, gTitle)  # Remove from db
                print("Removed '%s' from '%s'" % (cName, gTitle))
            else:
                print(f"An error occurred during file removal.\nPlease check {PATH}/{gTitle} and try again.")

        # Select character
        cname: str = removeIllegalChars(input("Enter character name: "))
        c: Optional[game_character] = resultViewer(rdb.getCharactersLikeName(cname), True)
        if c:
            # Select where to remove
            option: str = optionPicker("Where would you like to remove the character?", {"g": "From one game", "a": "From all games (the entire database)"})
            print()
            if option == "g":
                # Remove from a select game
                print("Select a game to remove '%s' from:\n" % c.name)
                g: str = resultViewer(c.appears_in, True)
                if g:
                    confirmDelete: str = input("You are about to remove '%s'\nfrom the game '%s'\n\nAre you sure you want to proceed? (y/n): " % (c.name, g)).lower()
                    print()
                    if confirmDelete == "y":
                        removeFromGame(c.name, g)
                    else:
                        print("Cancelling...")
                else:
                    print("No game selected. Cancelling...")
            elif option == "a":
                # Remove from all games
                confirmDelete: str = input("You are about to remove:\n'%s'\nFrom the database. Proceed? (y/n): " % (c.name)).lower()
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

    def removeGame() -> None:
        """Remove a game from the database and local files."""
        gtitle: str = removeIllegalChars(input("Enter game title: "))
        g: Optional[game] = resultViewer(rdb.getGamesLikeTitle(gtitle), True)
        if g:
            confirmDelete: str = input("You are about to remvove the game:\n'%s'\nAre you sure you want to proceed? (y/n): " % g.title).lower()
            if confirmDelete == "y":
                if fm.removeGame(g.title):  # Remove from local files
                    rdb.removeGame(g.title) # Remove from db
                    print(f"'{g.title}' successfully removed")
                else:
                    print(f"An error occurred during file removal.\nPlease check {PATH}/{g.title} and try again later.")
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

def updateData() -> None:
    """Select and update information within the database.
    
    Prompts will appear for whether or not to update a character or game, 
    and then further prompts will appear depending on which of those tables'
    attributes you would like to update.
    """

    def updateCharacter() -> None:
        """Select and update a character's information."""

        def updateName(oldName: str) -> None:
            """Select and update a character's name."""
            
            def updateFiles(oldName: str, newName: str) -> None:
                """Update a character's name in the database and local files."""
                c = rdb.getCharacterByName(oldName)
                if not fm.updateCharacterName(c, newName):
                    print(f"An error occurred during file updating.\nPlease check {PATH} and try again later.")
                    return

            newName: str = removeIllegalChars(input("Enter new name: "))
            print()
            existing: Optional[game_character] = rdb.getCharacterByName(newName)
            if existing:    # Overwriting character
                confirmUpdate: str = input("A character with that name already exists:\n\n%s\n\nThis will merge that character with '%s'.\nProceed? (y/n): " % (existing.printSelf(), oldName))
                print()
                if confirmUpdate.lower() == "y":
                    updateFiles(oldName, existing.name)
                    c: Optional[game_character] = rdb.getCharacterByName(oldName)
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
        cname: str = removeIllegalChars(input("Enter character name: "))
        print()
        results: Optional[List[game_character]] = rdb.getCharactersLikeName(cname)
        # Select character
        c: Optional[game_character] = resultViewer(results, True)
        if c:
            # Decide what to update and what to change it to
            # NOTE: Right now, the only attribute characters have is `name`, but more functionality could be possible in the future
            attribute: str = optionPicker("What would you like to update?", {"n": "Name"})
            print()
            if attribute == "n":    # Update name
                updateName(c.name)
            else:
                print("No valid option selected. Cancelling the operation...")
        else:
            print("No character selected. Cancelling the operation...")

    def updateGame() -> None:
        """Select and update a game's information."""

        def updateTitle(oldTitle: str) -> None:
            """Update a game's title."""
            newTitle: str = removeIllegalChars(input("Enter new title: "))
            print()
            if rdb.getGameByTitle(newTitle):
                print("A game with that name already exists! Cancelling the action...")
                return
            confirmUpdate: str = input("You are about to change the following game's title:\n\n%s\n\t↓\n%s\n\nConfirm update? (y/n): " % (oldTitle, newTitle))
            if confirmUpdate.lower() == "y":
                if fm.updateGameTitle(oldTitle, newTitle):  # Update in local files
                    rdb.updateGameTitle(oldTitle, newTitle) # Update in db
                    print("Changes made successfully.")         
                else:
                    print(f"An error occurred during file operations.\nPlease check {PATH} and try again later.")          
            else:
                print("Update cancelled.")

        def updateReleaseDate(gameTitle: str) -> None:
            """Update a game's release date."""
            newRDate: str = input("Enter new release date (YYYY-MM-DD): ")
            print()
            if validDate(newRDate):
                confirmUpdate: str = input("You are about to change the release date for:\n\n%s\n\nTo the following:\n\n%s\n\t↓\n%s\n\nConfirm update? (y/n): " % (gameTitle, g.release_date, newRDate))
                if confirmUpdate.lower() == "y":
                    if fm.updateGameReleaseDate(gameTitle, newRDate):   # Update in local files
                        rdb.updateGameReleaseDate(gameTitle, newRDate)  # Update in db
                        print("Changes made successfully.")
                    else:
                        print(f"An error occurred during file operations.\nPlease check {PATH} and try again later.")
                else:
                    print("Update cancelled.")
            else:
                print("Date entered is invalid. Cancelling the update...")

        # Query game
        gtitle: str = removeIllegalChars(input("Enter game title: "))
        print()
        results: Optional[List[game]] = rdb.getGamesLikeTitle(gtitle)
        # Select game
        g: Optional[game] = resultViewer(results, True)
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

def toggleView(currStyle: MenuStyle):
    """Toggle the menu's style between default and compact."""
    currStyle = MenuStyle.DEFAULT if currStyle is MenuStyle.COMPACT else MenuStyle.COMPACT
    return currStyle

def resetDatabase(detailed: bool=False) -> None:
    """Reset the entire database.
    
    A hard-reset of the database will drop the entire schema, reinserting 
    everything including the tables, triggers, AND do a soft-reset.
    A soft-reset of the database will only reinsert all raw data, and
    readjust all relations in the database.
    """
    response: str = optionPicker("How would you like to reset the database?", {"h": "Hard reset (Reinsert everything)", "s": "Soft reset (Only reinsert relations)"})
    if response == "h":
        response = input("This command may take some time to execute.\nAre you sure you want to reset the database? (y/n): ")
        print()
        if response.lower() in ["y", "yes", "yea", "ye"]:
            maintenance.reset_db(not detailed, detailed)
        else:
            print("Cancelling...")
    elif response == "s":
        response = input("This command may take some time to execute.\nAre you sure you want to reset the database? (y/n): ")
        print()
        if response.lower() in ["y", "yes", "yea", "ye"]:
            maintenance.updateRelations(not detailed, detailed)
        else:
            print("Cancelling...")
    else:
        print("Cancelling...")

### END FUNCTIONS ###

def main() -> None:
    """The main function for performing database operations."""
    command = ""
    menuStyle: MenuStyle = MenuStyle.DEFAULT
    while (command != "Q" and command != "q"):
        print(MENU_COMPACT if menuStyle == MenuStyle.COMPACT else MENU)
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