"""Encapsulation of operations to occur on local files.

All methods within this module serve the purpose of interacting with
local files, allowing changes made to the database to be accurately
reflected in local text files.
"""

import os
from typing import Dict, Optional, List

from classes.nodes import GameCharacter
from main import PATH


ERROR_MESSAGES = {
    "default":      lambda e: f"ERROR: {e}",
    "os_open":      lambda f: f"Could not open file: {f}",
    "os_make":      lambda f: f"Could not create file: {f}",
    "os_nopath":    lambda f: f"Path to {f} does not exist"
}


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

def parseFile(filename: str) -> Optional[Dict[str, tuple]]:
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
        data = open("%s/%s" % (PATH, filename), "r").read().splitlines()
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
    return os.listdir(PATH)

def writeGameFile(gtitle: str, release_date: str, characters: List[str]) -> bool:
    """Create a file for a game according to the database format.
    
    The file is created such that the filename is `gtitle`.txt, the first
    line is the game's release date, and each subsequent line is a character
    name, which can be found in the `characters` list. 

    Returns whether or not the file was created successfully.
    """
    try:
        with open("%s/%s.txt" % (PATH, gtitle), "w") as f:
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
        with open("%s/%s.txt" % (PATH, gtitle), "a") as f:
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
        replaceLine(cname, "", "%s/%s.txt" % (PATH, gtitle), end = "")
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
        if os.path.exists("%s/%s.txt" % (PATH, gtitle)):
            os.remove("%s/%s.txt" % (PATH, gtitle))
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
            replaceLine(c.name, new_name, "%s/%s.txt" % (PATH, gtitle))
        return True
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
        os.rename("%s/%s.txt" % (PATH, old_title), "%s/%s.txt" % (PATH, new_title))
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
        with open("%s/%s.txt" % (PATH, gtitle), "r") as f:
            lines = f.readlines()
            lines[0] = "%s\n" % new_release_date    # The release date is the first line of the text file
        with open("%s/%s.txt" % (PATH, gtitle), "w") as f:
            f.writelines(lines)
        return True
    except OSError:
        print(ERROR_MESSAGES["os_open"](gtitle))
        return False
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return False