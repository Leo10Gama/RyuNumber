"""Encapsulation of operations to occur on local files.

All methods within this module serve the purpose of interacting with
local files, allowing changes made to the database to be accurately
reflected in local text files.

The files that can be changed include the following:
    The `.txt` files holding all information about games and characters.
    The `.csv` file holding all information about character aliases.
"""

import os
from typing import Dict, Optional, List

import csv

from classes.nodes import GameCharacter
from main import GAMES_PATH, TABLES_PATH


ALIAS_FILE = f"{TABLES_PATH}/alias.csv"
TEMP_FILE = f"{TABLES_PATH}/temp.csv"
ALIAS_HEADER = ["cname", "aname"]
CSV_PROPERTIES = {
    "delimiter": ",",
    "quotechar": ":",
    "quoting": csv.QUOTE_MINIMAL
}

ERROR_MESSAGES = {
    "default":      lambda e: f"ERROR: {e}",
    "os_open":      lambda f: f"Could not open file: {f}",
    "os_make":      lambda f: f"Could not create file: {f}",
    "os_nopath":    lambda f: f"Path to {f} does not exist"
}


#======================#
# GAME FILE OPERATIONS #
#======================#

def replaceLine(oldLine: str, newLine: str, filePath: str, end: str='\n') -> bool:
    """Replace a given line in a file with another line.
    
    Parameters
    ----------
    oldLine: str
        The line that can be found in the file, that will be replaced. This
        does not include the newline character found at the end of each line.
    newLine: str
        The new line to insert to the file in place of the oldLine.
    filePath: str
        The path by which to find the file, including the extension and leading
        folders.
    end: str
        What to insert at the end of the line. Default is a newline character.
        Altering this to not produce a new line may cause unintended side-
        effects.
    
    Return
    ------
    bool
        Whether or not the file was successfully altered.
    """
    try:
        with open(filePath, "r+") as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if lines[i].strip('\n') == oldLine:
                    if i < len(lines) - 1:
                        lines[i] = f"{newLine}{end}"
                    else:
                        lines[i] = f"{newLine}"
                        if end == '':
                            lines[i-1] = lines[i-1].strip('\n')
            f.seek(0)
            f.truncate()
            f.seek(0)
            f.writelines(lines)
        return True
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return False

def parseGameFile(filename: str) -> Optional[Dict[str, tuple]]:
    """Parse a game's text file and return its dictionary representation.
    
    Since every file is saved in an identical format, parsing each file is
    repetitive and can be done in a similar fashion for each text file.

    Return
    ------
    Dict[str, tuple] | None
        A dictionary representation of the game. Specifically, with keys "game"
        and "GameCharacters", which relate to a tuple (title, release_date)
        and list of names respectively. If any errors occur, None is returned.
    """
    try:
        data = open("%s/%s" % (GAMES_PATH, filename), "r").read().splitlines()
        returnVal = {}
        filename = filename[:-4]
        returnVal["game"] = (filename, data.pop(0))
        returnVal["game_characters"] = []
        for c in data:
            returnVal["game_characters"].append(c)
        return returnVal
    except OSError:
        print(ERROR_MESSAGES["os_open"](filename))
        return None
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return None

def getGameFiles() -> List[str]:
    """Return an array containing the names of all files in `main.PATH`."""
    return os.listdir(GAMES_PATH)

def writeGameFile(gtitle: str, release_date: str, characters: List[str]) -> bool:
    """Create a file for a game according to the database format.
    
    The file is created such that the filename is `gtitle`.txt, the first
    line is the game's release date, and each subsequent line is a character
    name, which can be found in the `characters` list. 

    Returns whether or not the file was created successfully.
    """
    try:
        with open("%s/%s.txt" % (GAMES_PATH, gtitle), "w") as f:
            f.write("%s" % release_date)
            for c in characters:
                f.write("\n%s" % c)
        return True
    except OSError:
        print(ERROR_MESSAGES["os_make"](gtitle))
        return False
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return False

def appendGameFile(gtitle: str, characters: List[str]) -> bool:
    """Add characters to the end of a game's text file.
    
    The title of the game is passed, and any additional characters are
    passed in the `characters` list. This method does not check for
    duplicate entries, so it is up to the caller to ensure this method does
    not allow for duplicate entries, which may lead to unintended side-
    effects.

    Returns whether or not the characters were appended to the file
    successfully.
    """
    try:
        with open("%s/%s.txt" % (GAMES_PATH, gtitle), "a") as f:
            for c in characters:
                f.write("\n%s" % c)
        return True
    except OSError:
        print(ERROR_MESSAGES["os_open"](gtitle))
        return False
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return False

def removeCharacterFromGame(cname: str, gtitle: str) -> bool:
    """Remove a character's name from a game's text file.
    
    Returns whether or not the character's name was removed successfully.
    """
    try:
        replaceLine(cname, "", "%s/%s.txt" % (GAMES_PATH, gtitle), end = "")
        return True
    except OSError:
        print(ERROR_MESSAGES["os_open"](gtitle))
        return False
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return False

def removeGame(gtitle: str) -> bool:
    """Remove a game's text file from the local files.
    
    Returns whether or not the file was removed successfully.
    """
    try:
        if os.path.exists("%s/%s.txt" % (GAMES_PATH, gtitle)):
            os.remove("%s/%s.txt" % (GAMES_PATH, gtitle))
            return True
        else:
            raise OSError()
    except OSError:
        print(ERROR_MESSAGES["os_nopath"](gtitle))
        return False
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return False

def updateCharacterName(c: GameCharacter, new_name: str) -> bool:
    """Update a character's name in all games for which they appear.
    
    Returns whether or not the character's name was updated in all games.
    """
    try:
        for gtitle in c.appears_in:
            replaceLine(c.name, new_name, "%s/%s.txt" % (GAMES_PATH, gtitle))
        if updateAliasCname(c.name, new_name):
            return True
        return False
    except OSError:
        print(ERROR_MESSAGES["os_open"](gtitle))
        return False
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return False

def updateGameTitle(old_title: str, new_title: str) -> bool:
    """Update the title of a game's text file locally.
    
    Returns whether or not the game's title was updated successfully.
    """
    try:
        os.rename("%s/%s.txt" % (GAMES_PATH, old_title), "%s/%s.txt" % (GAMES_PATH, new_title))
        return True
    except OSError:
        print(ERROR_MESSAGES["os_nopath"](old_title))
        return False
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return False

def updateGameReleaseDate(gtitle: str, new_release_date: str) -> bool:
    """Update the release date of a game's local text file.
    
    Returns whether or not the game's release date was updated
    successfully.
    """
    try:
        lines: List[str] = []
        with open("%s/%s.txt" % (GAMES_PATH, gtitle), "r") as f:
            lines = f.readlines()
            lines[0] = "%s\n" % new_release_date    # The release date is the first line of the text file
        with open("%s/%s.txt" % (GAMES_PATH, gtitle), "w") as f:
            f.writelines(lines)
        return True
    except OSError:
        print(ERROR_MESSAGES["os_open"](gtitle))
        return False
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return False

#=======================#
# ALIAS FILE OPERATIONS #
#=======================#

def appendAlias(cname: str, aname: str) -> bool:
    """Add a character's alias to local files.
    
    Returns whether or not the file was written successfully.
    """
    try:
        write_mode = "a" if os.path.exists(ALIAS_FILE) else "w"
        with open(ALIAS_FILE, write_mode) as f:
            csv_writer = csv.DictWriter(f, 
                fieldnames=ALIAS_HEADER,
                delimiter=CSV_PROPERTIES["delimiter"],
                quotechar=CSV_PROPERTIES["quotechar"],
                quoting=CSV_PROPERTIES["quoting"]
            )
            if write_mode == "w": csv_writer.writeheader()
            csv_writer.writerow(dict(zip(ALIAS_HEADER, (cname, aname))))
        return True
    except OSError as e:
        print(ERROR_MESSAGES["os_open"](ALIAS_FILE))
        return False
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return False

def removeAlias(aname: str) -> bool:
    """Remove a character's alias from local files.
    
    Returns whether or not the item was removed from files successfully.
    """
    try:
        if not os.path.exists(ALIAS_FILE): 
            return True     # If the file doesn't exist, there's nothing to remove! True by default
        with open(ALIAS_FILE, "r") as f_in, open(TEMP_FILE, "w+") as f_out:
            # Set up reader and writer
            csv_reader = csv.DictReader(f_in, 
                fieldnames=ALIAS_HEADER,
                delimiter=CSV_PROPERTIES["delimiter"],
                quotechar=CSV_PROPERTIES["quotechar"],
                quoting=CSV_PROPERTIES["quoting"]
            )
            csv_writer = csv.DictWriter(f_out,
                fieldnames=ALIAS_HEADER,
                delimiter=CSV_PROPERTIES["delimiter"],
                quotechar=CSV_PROPERTIES["quotechar"],
                quoting=CSV_PROPERTIES["quoting"]
            )
            # Iterate, only writing the line if it isn't the one we want to remove
            for row in csv_reader:
                if row[ALIAS_HEADER[1]] != aname:
                    csv_writer.writerow(row)
        os.rename(TEMP_FILE, ALIAS_FILE)    # temp file is now our new alias.csv
        return True
    except OSError as e:
        print(ERROR_MESSAGES["os_open"](ALIAS_FILE))
        return False
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return False

def updateAliasCname(old_cname: str, new_cname: str) -> bool:
    """Update a character's name in local csv files.
    
    Returns whether or not the item was updated from files successfully.
    """
    try:
        if not os.path.exists(ALIAS_FILE): 
            return True     # If the file doesn't exist, there's nothing to remove! True by default
        with open(ALIAS_FILE, "r") as f_in, open(TEMP_FILE, "w+") as f_out:
            # Set up reader and writer
            csv_reader = csv.DictReader(f_in, 
                fieldnames=ALIAS_HEADER,
                delimiter=CSV_PROPERTIES["delimiter"],
                quotechar=CSV_PROPERTIES["quotechar"],
                quoting=CSV_PROPERTIES["quoting"]
            )
            csv_writer = csv.DictWriter(f_out,
                fieldnames=ALIAS_HEADER,
                delimiter=CSV_PROPERTIES["delimiter"],
                quotechar=CSV_PROPERTIES["quotechar"],
                quoting=CSV_PROPERTIES["quoting"]
            )
            # Iterate, only rewriting the line we want to change
            for row in csv_reader:
                if row[ALIAS_HEADER[0]] != old_cname:
                    csv_writer.writerow(row)
                else:
                    row[ALIAS_HEADER[0]] = new_cname
                    csv_writer.writerow(row)
        os.rename(TEMP_FILE, ALIAS_FILE)    # temp file is now our new alias.csv
        return True
    except OSError as e:
        print(ERROR_MESSAGES["os_open"](ALIAS_FILE))
        return False
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return False

def updateAlias(old_aname: str, new_aname: str) -> bool:
    """Update a character's alias from local files.
    
    Returns whether or not the item was updated from files successfully.
    """
    try:
        if not os.path.exists(ALIAS_FILE): 
            return True     # If the file doesn't exist, there's nothing to remove! True by default
        with open(ALIAS_FILE, "r") as f_in, open(TEMP_FILE, "w+") as f_out:
            # Set up reader and writer
            csv_reader = csv.DictReader(f_in, 
                fieldnames=ALIAS_HEADER,
                delimiter=CSV_PROPERTIES["delimiter"],
                quotechar=CSV_PROPERTIES["quotechar"],
                quoting=CSV_PROPERTIES["quoting"]
            )
            csv_writer = csv.DictWriter(f_out,
                fieldnames=ALIAS_HEADER,
                delimiter=CSV_PROPERTIES["delimiter"],
                quotechar=CSV_PROPERTIES["quotechar"],
                quoting=CSV_PROPERTIES["quoting"]
            )
            # Iterate, only rewriting the line we want to change
            for row in csv_reader:
                if row[ALIAS_HEADER[1]] != old_aname:
                    csv_writer.writerow(row)
                else:
                    row[ALIAS_HEADER[1]] = new_aname
                    csv_writer.writerow(row)
        os.rename(TEMP_FILE, ALIAS_FILE)    # temp file is now our new alias.csv
        return True
    except OSError as e:
        print(ERROR_MESSAGES["os_open"](ALIAS_FILE))
        return False
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return False

def parseAliases() -> Optional[List[Dict[str, str]]]:
    """Return a dictionary mapping all alias tables.
    
    The resulting dictionary has multiple dictionaries mapping cname and
    aname. If any errors occur, None is returned.
    """
    try:
        with open(ALIAS_FILE, "r") as f:
            csv_reader = csv.DictReader(f,
                fieldnames=ALIAS_HEADER,
                delimiter=CSV_PROPERTIES["delimiter"],
                quotechar=CSV_PROPERTIES["quotechar"],
                quoting=CSV_PROPERTIES["quoting"]
            )
            result: List[Dict[str, str]] = []
            for row in csv_reader:
                result.append(row)
        return result
    except Exception as e:
        print(ERROR_MESSAGES["os_open"](ALIAS_FILE))
        return None
