# NOTE: This script should only be run ONCE to initialize the database
import mysql.connector
from ryu_connector import RyuConnector

def main(debug = False, debug_detailed = False):
    if debug or debug_detailed: print("Establishing connection...")
    # Create database if not exists
    dbCreds = open("db.txt", "r").read().splitlines()

    db1 = mysql.connector.connect(
        host        =dbCreds[0],
        user        =dbCreds[1],
        password    =dbCreds[2]
    )
    cursor = db1.cursor()
    if debug or debug_detailed: print("Creating database...")
    cursor.execute("CREATE DATABASE IF NOT EXISTS ryu_number;")
    db1.commit()
    db1.close()
    # Connect to the db we just created
    with RyuConnector() as rdb:
        # Create 'character' table
        characterTable = "CREATE TABLE IF NOT EXISTS game_character (\
            name VARCHAR(64) NOT NULL, \
            ryu_number INTEGER DEFAULT 99, \
            PRIMARY KEY (name));"
        rdb.execute(characterTable)
        # Create 'game' table
        gameTable = "CREATE TABLE IF NOT EXISTS game (\
            title VARCHAR(64) NOT NULL, \
            ryu_number INTEGER DEFAULT 99, \
            release_date DATE, \
            PRIMARY KEY (title));"
        rdb.execute(gameTable)
        # Create 'appears_in' relation table
        appearsInTable = "CREATE TABLE IF NOT EXISTS appears_in (\
            cname VARCHAR(64) NOT NULL, \
            gtitle VARCHAR(64) NOT NULL, \
            PRIMARY KEY (cname, gtitle), \
            FOREIGN KEY (cname) REFERENCES game_character(name) \
                ON UPDATE CASCADE \
                ON DELETE CASCADE, \
            FOREIGN KEY (gtitle) REFERENCES game(title) \
                ON UPDATE CASCADE \
                ON DELETE CASCADE);"
        rdb.execute(appearsInTable)

        if debug or debug_detailed: print("Creating triggers...")
        # Create the triggers to automatically set the Ryu Numbers
        dropAI = "DROP TRIGGER IF EXISTS update_ai;"
        dropAI2 = "DROP TRIGGER IF EXISTS insert_ai;"
        insertAI = "CREATE TRIGGER insert_ai AFTER INSERT ON appears_in FOR EACH ROW BEGIN \
            IF (SELECT ryu_number FROM game AS G WHERE G.title=NEW.gtitle) > (SELECT ryu_number FROM game_character AS C WHERE C.name=NEW.cname) THEN \
                UPDATE game AS G \
                SET ryu_number=(SELECT ryu_number FROM game_character AS C WHERE C.name=NEW.cname)+1 \
                WHERE G.title=NEW.gtitle; \
            ELSEIF (SELECT ryu_number FROM game_character AS C WHERE C.name=NEW.cname) > (SELECT ryu_number FROM game AS G WHERE G.title=NEW.gtitle) THEN \
                UPDATE game_character AS C \
                SET ryu_number=(SELECT ryu_number FROM game AS G WHERE G.title=NEW.gtitle) \
                WHERE C.name=NEW.cname; \
            END IF; END;"
        updateAI = "CREATE TRIGGER update_ai AFTER UPDATE ON appears_in FOR EACH ROW BEGIN \
            IF (SELECT ryu_number FROM game AS G WHERE G.title=NEW.gtitle) > (SELECT ryu_number FROM game_character AS C WHERE C.name=NEW.cname) THEN \
                UPDATE game AS G \
                SET ryu_number=(SELECT ryu_number FROM game_character AS C WHERE C.name=NEW.cname)+1 \
                WHERE G.title=NEW.gtitle; \
            ELSEIF (SELECT ryu_number FROM game_character AS C WHERE C.name=NEW.cname) > (SELECT ryu_number FROM game AS G WHERE G.title=NEW.gtitle) THEN \
                UPDATE game_character AS C \
                SET ryu_number=(SELECT ryu_number FROM game AS G WHERE G.title=NEW.gtitle) \
                WHERE C.name=NEW.cname; \
            END IF; END;"
        rdb.execute(dropAI)
        rdb.execute(dropAI2)
        rdb.execute(insertAI)
        rdb.execute(updateAI)

        # Add the legendary RYU himself
        rdb.execute("INSERT IGNORE INTO game_character (name, ryu_number) VALUES ('Ryu', 0)")    
        if debug or debug_detailed: print("Database initialized.")

if __name__ == "__main__":
    main()