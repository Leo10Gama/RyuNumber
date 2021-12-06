from classes import file_manager as fm
from init import initialize_db
from classes.ryu_connector import RyuConnector
from methods import queries

def updateRelations(debug = False, debug_detailed = False):
    with RyuConnector() as rdb:
        # Start by getting Ryu, the boy, the absolute unit of a lad
        rn = 0
        rdb.execute(queries.getCharacterByRyu(rn))
        results = [str(c[0]) for c in rdb.fetchall()]
        # Continue iterating as long as there are results to iterate over
        while results:
            if debug or debug_detailed: print(f"Adjusting {len(results)} characters with Ryu number {rn}...")
            # Character operations
            for cname in results:
                if debug_detailed: print(f"\tAdjusting {cname}...")
                rdb.execute(queries.getRelationsAndRNByCharacter(cname, rn))
                relations = [str(g[1]) for g in rdb.fetchall()]   # Get games character `cname` appears in
                rdb.execute(queries.removeCharacterRelations(cname))
                for gtitle in relations:
                    rdb.execute(queries.insertRelation(cname, gtitle))
            if debug or debug_detailed: print("\tDone")
            # Get next games
            rn += 1
            rdb.execute(queries.getGamesByRyu(rn))
            results = [g[0] for g in rdb.fetchall()]
            # Game operations
            if debug or debug_detailed: print(f"Adjusting {len(results)} games with Ryu number {rn}...")
            for gtitle in results:
                if debug_detailed: print(f"\tAdjusting {gtitle}...")
                rdb.execute(queries.getRelationsAndRNByGame(gtitle, rn))
                relations = [str(c[0]) for c in rdb.fetchall()]   # Get characters that appear in `gtitle`
                rdb.execute(queries.removeGameRelations(gtitle))
                for cname in relations:
                    rdb.execute(queries.insertRelation(cname, gtitle))
            if debug or debug_detailed: print("\tDone")
            # Get next characters
            rdb.execute(queries.getCharacterByRyu(rn))
            results = [c[0] for c in rdb.fetchall()]
        if debug or debug_detailed: print("Done")

def fill_db(debug = False, debug_detailed = False): # NOTE: Code runs under the implication that init.py has been run
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
    
    updateRelations(debug, debug_detailed)

def reset_db(debug = False, debug_detailed = False):
    with RyuConnector() as rdb:
        rdb.execute("DROP SCHEMA IF EXISTS ryu_number")
    # Now refill the whole db
    initialize_db(debug, debug_detailed)
    fill_db(debug, debug_detailed)