import fill_db
import init
import mysql.connector
import queries

# THIS IS A VERY TIME-COSTLY METHOD SO ONLY USE IT IF ABSOLUTELY NECESSARY
def updateRelations(debug = False, debug_detailed = False):
    if debug or debug_detailed: print("Connecting to database...", end="")
    # Connect to the db
    dbCreds = open("db.txt", "r").read().splitlines()
    mydb = mysql.connector.connect(
        host        =dbCreds[0],
        user        =dbCreds[1],
        password    =dbCreds[2],
        database    =dbCreds[3]
    )
    cursor = mydb.cursor()
    if debug or debug_detailed: print("Done")

    # Start by getting Ryu, the boy, the absolute unit of a lad
    rn = 0
    cursor.execute(queries.getCharacterByRyu(rn))
    results = [str(c[0]) for c in cursor.fetchall()]
    # Continue iterating as long as there are results to iterate over
    while results:
        if debug or debug_detailed: print(f"Adjusting {len(results)} characters with Ryu number {rn}...")
        # Character operations
        for cname in results:
            if debug_detailed: print(f"\tAdjusting {cname}...")
            cursor.execute(queries.getRelationsAndRNByCharacter(cname, rn))
            relations = [str(g[1]) for g in cursor.fetchall()]   # Get games character `cname` appears in
            cursor.execute(queries.removeCharacterRelations(cname))
            for gtitle in relations:
                cursor.execute(queries.insertRelation(cname, gtitle))
        if debug or debug_detailed: print("\tDone")
        # Get next games
        rn += 1
        cursor.execute(queries.getGamesByRyu(rn))
        results = [g[0] for g in cursor.fetchall()]
        # Game operations
        if debug or debug_detailed: print(f"Adjusting {len(results)} games with Ryu number {rn}...")
        for gtitle in results:
            if debug_detailed: print(f"\tAdjusting {gtitle}...")
            cursor.execute(queries.getRelationsAndRNByGame(gtitle, rn))
            relations = [str(c[0]) for c in cursor.fetchall()]   # Get characters that appear in `gtitle`
            cursor.execute(queries.removeGameRelations(gtitle))
            for cname in relations:
                cursor.execute(queries.insertRelation(cname, gtitle))
        if debug or debug_detailed: print("\tDone")
        # Get next characters
        cursor.execute(queries.getCharacterByRyu(rn))
        results = [c[0] for c in cursor.fetchall()]
    if debug or debug_detailed: print("Done")
    
    mydb.commit()
    mydb.close()

def reset_db(debug = False, debug_detailed = False):
    # Connect to the db...
    dbCreds = open("db.txt", "r").read().splitlines()
    mydb = mysql.connector.connect(
        host        =dbCreds[0],
        user        =dbCreds[1],
        password    =dbCreds[2],
        database    =dbCreds[3]
    )
    cursor = mydb.cursor()
    # ... and now drop the db
    cursor.execute("DROP SCHEMA IF EXISTS ryu_number")
    mydb.commit()
    mydb.close()
    # Now refill the whole db
    init.main(debug, debug_detailed)
    fill_db.main(debug, debug_detailed)