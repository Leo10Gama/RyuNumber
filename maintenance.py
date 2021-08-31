import fill_db
import init
import mysql.connector
import os
import queries

# THIS IS A VERY TIME-COSTLY METHOD SO ONLY USE IT IF ABSOLUTELY NECESSARY
def updateRelations(debug = False, debug_detailed = False):
    if debug or debug_detailed: print("Connecting to database...")
    # Connect to the db
    dbCreds = open("db.txt", "r").read().splitlines()
    mydb = mysql.connector.connect(
        host        =dbCreds[0],
        user        =dbCreds[1],
        password    =dbCreds[2],
        database    =dbCreds[3]
    )
    cursor = mydb.cursor()

    # Pull out and reinsert every relation starting with Ryu
    if debug or debug_detailed: print("Beginning character insertion:")
    characterQueue = open("charqueue.txt", "w+")
    open("gamequeue.txt", "w+")
    gameQueue = open("gamequeue.txt", "r+")
    characterQueue.write("Ryu\n")
    characterQueue.close()
    rn = 0
    # Keep in mind: the reason we're using file-I/O instead of traditional lists
    # is because, especially dealing with this much data, lists can exceed max
    # capacity very quickly :(
    while os.path.getsize("charqueue.txt") or os.path.getsize("gamequeue.txt"):
        # For each character, reinsert their relation to the games immediately across from them
        if debug: print("Reading characters with Ryu Number >= %d..." % rn)
        with open("charqueue.txt", "r") as f:
            c = f.readline().strip('\n')
            if debug_detailed: print("Reading character %s..." % c)
            games = []
            while c:
                cursor.execute(queries.getRelationByCharacter(c))
                relations = cursor.fetchall()
                cursor.execute(queries.removeCharacterRelations(c))
                for row in relations:
                    # Avoid duplicate entries AND only insert if it's newer
                    if row[1] not in games and row[2] >= rn:
                        gameQueue.write("%s\n" % row[1])
                        games.append(row[1])
                        if debug_detailed: print("\tAppending game %s to read next..." % row[1])
                    cursor.execute(queries.insertRelation(c, row[1]))
                c = f.readline().strip('\n')
        characterQueue = open("charqueue.txt", "w+")
        characterQueue.truncate(0)  # Clear the file since it will be written to in the next loop
        gameQueue.close()   # Close gameQueue so it will update in memory
        # For each game, reinsert their relation to every character starring in it
        if debug: print("Reading games with Ryu Number > %d..." % rn)
        with open("gamequeue.txt", "r") as f:
            g = f.readline().strip('\n')
            if debug_detailed: print("Reading game %s..." % g)
            while g:
                cursor.execute(queries.getRelationByGame(g))
                relations = cursor.fetchall()
                cursor.execute(queries.removeGameRelations(g))
                for row in relations:
                    # Insert so long as the character's Ryu Number is high enough (duplicates will sometimes be allowed, but for characters it is negligable)
                    if row[2] > rn:
                        characterQueue.write("%s\n" % row[0])
                        if debug_detailed: print("\tAppending character %s to read next..." % row[0])
                    cursor.execute(queries.insertRelation(row[0], g))
                g = f.readline().strip('\n')
        gameQueue = open("gamequeue.txt", "r+")
        gameQueue.truncate(0)   # Clear the file since it will be written to in the next loop (if there is a next loop)
        characterQueue.close()  # Close the queue so it updates in memory
        rn += 1
    if debug or debug_detailed: print("Done.")
    os.remove("charqueue.txt")
    os.remove("gamequeue.txt")
    
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
    # Now refill the whole db
    init.main(debug, debug_detailed)
    fill_db.main(debug, debug_detailed)