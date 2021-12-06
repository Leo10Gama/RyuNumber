import os
from typing import Dict, List

from classes.nodes import game_character
from main import PATH

ERROR_MESSAGES = {
    "default":      lambda e: f"ERROR: {e}",
    "os_open":      lambda f: f"Could not open file: {f}",
    "os_make":      lambda f: f"Could not create file: {f}",
    "os_nopath":    lambda f: f"Path to {f} does not exist"
}

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

def parseFile(filename) -> Dict[str, tuple]:
    # Every file is added s.t. it is saved as [Game Name].txt and the first line is the game's release date
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

def getGameFiles():
    return os.listdir(PATH)

def writeGameFile(gtitle: str, release_date: str, characters: List[str]):
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

def appendGameFile(gtitle: str, characters: List[str]):
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

def removeCharacterFromGame(cname: str, gtitle: str):
    try:
        replaceLine(cname, "", "%s/%s.txt" % (PATH, gtitle), end = "")
        return True
    except OSError:
        print(ERROR_MESSAGES["os_open"](gtitle))
        return False
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return False

def removeGame(gtitle: str):
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

def updateCharacterName(c: game_character, new_name: str):
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

def updateGameTitle(old_title: str, new_title: str):
    try:
        os.rename("%s/%s.txt" % (PATH, old_title), "%s/%s.txt" % (PATH, new_title))
        return True
    except OSError:
        print(ERROR_MESSAGES["os_nopath"](old_title))
        return False
    except Exception as e:
        print(ERROR_MESSAGES["default"](e))
        return False

def updateGameReleaseDate(gtitle: str, new_release_date: str):
    try:
        lines = []
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