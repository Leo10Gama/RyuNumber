"""Initialize the entirety of the database.

This module encompasses the creation process of the Ryu Database by
creating all necessary tables and triggers. It should only need to be
run once upon creation, and will only ever be run again during a hard-
reset, where the entire database is dropped and reinserted.
"""

import mysql.connector

from classes.ryu_connector import RyuConnector

def initialize_db(debug = False, debug_detailed = False):
    # Connect and create db
    if debug or debug_detailed: print(f"Establishing connection...", end="")
    dbCreds = open("db.txt", "r").read().splitlines()

    db1 = mysql.connector.connect(
        host        =dbCreds[0],
        user        =dbCreds[1],
        password    =dbCreds[2]
    )
    cursor = db1.cursor()
    if debug or debug_detailed: print(f"Done")
    if debug or debug_detailed: print(f"Creating database...", end="")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS ryu_number;")
    db1.commit()
    db1.close()
    if debug or debug_detailed: print(f"Done")
    # Connect to the db we just created
    with RyuConnector() as rdb:
        # Create tables
        if debug or debug_detailed: print(f"Creating tables...", end="")
        # Create 'game_character' table
        characterTable = (f"CREATE TABLE IF NOT EXISTS game_character ("
                            f"name        VARCHAR(64) NOT NULL, "
                            f"ryu_number  INTEGER     DEFAULT 99, "
                            f"PRIMARY KEY (name));"
        )
        rdb.execute(characterTable)
        # Create 'game' table
        gameTable = (f"CREATE TABLE IF NOT EXISTS game ("
                        f"title         VARCHAR(64) NOT NULL, "
                        f"ryu_number    INTEGER     DEFAULT 99, "
                        f"release_date  DATE, "
                        f"PRIMARY KEY (title));"
        )
        rdb.execute(gameTable)
        # Create 'appears_in' relation table
        appearsInTable = (f"CREATE TABLE IF NOT EXISTS appears_in ("
                            f"cname     VARCHAR(64) NOT NULL, "
                            f"gtitle    VARCHAR(64) NOT NULL, "
                            f"PRIMARY KEY (cname, gtitle), "
                            f"FOREIGN KEY (cname) REFERENCES game_character(name) "
                                f"ON UPDATE CASCADE "
                                f"ON DELETE CASCADE, "
                            f"FOREIGN KEY (gtitle) REFERENCES game(title) "
                                f"ON UPDATE CASCADE "
                                f"ON DELETE CASCADE);"
        )
        rdb.execute(appearsInTable)
        if debug or debug_detailed: print(f"Done")

        # Create the triggers to automatically set the Ryu Numbers
        if debug or debug_detailed: print(f"Creating triggers...", end="")
        dropAI = f"DROP TRIGGER IF EXISTS update_ai;"
        dropAI2 = f"DROP TRIGGER IF EXISTS insert_ai;"
        insertAI = (f"CREATE TRIGGER insert_ai AFTER INSERT ON appears_in "
                    f"FOR EACH ROW "
                    f"BEGIN "
                        f"IF (SELECT ryu_number FROM game AS G WHERE G.title=NEW.gtitle) > (SELECT ryu_number FROM game_character AS C WHERE C.name=NEW.cname) THEN "
                            f"UPDATE game AS G "
                            f"SET ryu_number=("
                                f"SELECT ryu_number "
                                f"FROM game_character AS C "
                                f"WHERE C.name=NEW.cname)+1 "
                            f"WHERE G.title=NEW.gtitle; "
                        f"ELSEIF (SELECT ryu_number FROM game_character AS C WHERE C.name=NEW.cname) > (SELECT ryu_number FROM game AS G WHERE G.title=NEW.gtitle) THEN "
                            f"UPDATE game_character AS C "
                            f"SET ryu_number=("
                                f"SELECT ryu_number "
                                f"FROM game AS G "
                                f"WHERE G.title=NEW.gtitle) "
                            f"WHERE C.name=NEW.cname; "
                        f"END IF; "
                    f"END;"
        )
        updateAI = (f"CREATE TRIGGER update_ai AFTER UPDATE ON appears_in "
                    f"FOR EACH ROW "
                    f"BEGIN "
                        f"IF (SELECT ryu_number FROM game AS G WHERE G.title=NEW.gtitle) > (SELECT ryu_number FROM game_character AS C WHERE C.name=NEW.cname) THEN "
                            f"UPDATE game AS G "
                            f"SET ryu_number=("
                                f"SELECT ryu_number "
                                f"FROM game_character AS C "
                                f"WHERE C.name=NEW.cname)+1 "
                            f"WHERE G.title=NEW.gtitle; "
                        f"ELSEIF (SELECT ryu_number FROM game_character AS C WHERE C.name=NEW.cname) > (SELECT ryu_number FROM game AS G WHERE G.title=NEW.gtitle) THEN "
                            f"UPDATE game_character AS C "
                            f"SET ryu_number=("
                                f"SELECT ryu_number "
                                f"FROM game AS G "
                                f"WHERE G.title=NEW.gtitle) "
                            f"WHERE C.name=NEW.cname; "
                        f"END IF; "
                    f"END;"
        )
        rdb.execute(dropAI)
        rdb.execute(dropAI2)
        rdb.execute(insertAI)
        rdb.execute(updateAI)
        if debug or debug_detailed: print(f"Done")

        # Add the legendary RYU himself
        rdb.execute(f"INSERT IGNORE INTO game_character (name, ryu_number) VALUES ('Ryu', 0)") 

    if debug or debug_detailed: print(f"Database successfully initialized.")

if __name__ == "__main__":
    initialize_db()