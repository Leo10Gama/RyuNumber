import fill_db
import init
from ryu_connector import RyuConnector
import queries

# THIS IS A VERY TIME-COSTLY METHOD SO ONLY USE IT IF ABSOLUTELY NECESSARY
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

def reset_db(debug = False, debug_detailed = False):
    with RyuConnector() as rdb:
        rdb.execute("DROP SCHEMA IF EXISTS ryu_number")
    # Now refill the whole db
    init.main(debug, debug_detailed)
    fill_db.main(debug, debug_detailed)