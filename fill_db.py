import os
import game
import game_character
import maintenance

# NOTE: This code runs on the implication that init.py has already been run to set up the db
def main(debug = False, debug_detailed = False):
    path = "Games List"
    if debug or debug_detailed: print("Reading files...")
    for filename in os.listdir(path):
        # Every file is added s.t. it is saved as [Game Name].txt and the first line is the game's release date
        data = open("%s/%s" % (path, filename), "r").read().splitlines()
        if debug_detailed: print("\tReading %s..." % filename)
        filename = filename[:-4]
        game.insertGame(filename, data.pop(0))
        priorityInserts = [x.name for x in game_character.getManyByNames(tuple(data))]
        for x in priorityInserts:
            if x in data:
                data.remove(x)
        if priorityInserts: game_character.insertCharactersToGame(priorityInserts, filename)
        if data: game_character.insertCharactersToGame(data, filename)

    if debug or debug_detailed: print("Raw data inserted successfully.")

    maintenance.updateRelations(debug, debug_detailed)

if __name__ == "__main__":
    main()