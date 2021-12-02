import file_manager as fm
import maintenance
from ryu_connector import RyuConnector
import queries

# NOTE: This code runs on the implication that init.py has already been run to set up the db
def main(debug = False, debug_detailed = False):
    with RyuConnector() as rdb:
        # Start reading files and adding data
        if debug or debug_detailed: print("Reading files...")
        for filename in fm.getGameFiles():
            # Every file is added s.t. it is saved as [Game Name].txt and the first line is the game's release date
            if debug_detailed: print(f"\tReading {filename}...")
            data = fm.parseFile(filename)
            rdb.execute(queries.insertGame(data["game"][0], data["game"][1]))
            rdb.execute(queries.getCharactersByNames(tuple(data["game_characters"])))
            priorityInserts = [c[0] for c in rdb.fetchall()]     # Names of characters who already exist in db (to insert FIRST)
            for x in priorityInserts:
                if x in data["game_characters"]:
                    data["game_characters"].remove(x)
            for c in priorityInserts:
                rdb.execute(queries.insertRelation(c, data["game"][0]))
            for c in data["game_characters"]:
                rdb.execute(queries.insertCharacter(c))
                rdb.execute(queries.insertRelation(c, data["game"][0]))
        if debug or debug_detailed: print("Raw data inserted successfully.")
    
    maintenance.updateRelations(debug, debug_detailed)

if __name__ == "__main__":
    main()