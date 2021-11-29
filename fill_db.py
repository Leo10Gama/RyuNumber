import os
import maintenance
import mysql.connector
import queries

# NOTE: This code runs on the implication that init.py has already been run to set up the db
def main(debug = False, debug_detailed = False):
    path = "Games List"
    # Connect to the db
    dbCreds = open("db.txt", "r").read().splitlines()
    mydb = mysql.connector.connect(
        host        =dbCreds[0],
        user        =dbCreds[1],
        password    =dbCreds[2],
        database    =dbCreds[3]
    )
    cursor = mydb.cursor()
    # Start reading files and adding data
    if debug or debug_detailed: print("Reading files...")
    for filename in os.listdir(path):
        # Every file is added s.t. it is saved as [Game Name].txt and the first line is the game's release date
        data = open("%s/%s" % (path, filename), "r").read().splitlines()
        if debug_detailed: print("\tReading %s..." % filename)
        filename = filename[:-4]
        cursor.execute(queries.insertGame(filename, data.pop(0)))
        cursor.execute(queries.getCharactersByNames(tuple(data)))
        priorityInserts = [x[0] for x in cursor.fetchall()]     # Give priority to characters who already exist in the db
        for x in priorityInserts:
            if x in data:
                data.remove(x)
        for c in priorityInserts:
            cursor.execute(queries.insertRelation(c, filename))
        for c in data:
            cursor.execute(queries.insertCharacter(c))
            cursor.execute(queries.insertRelation(c, filename))


    if debug or debug_detailed: print("Raw data inserted successfully.")
    
    mydb.commit()
    mydb.close()

    maintenance.updateRelations(debug, debug_detailed)

if __name__ == "__main__":
    main()