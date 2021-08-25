# NOTE: This script should only be run ONCE to initialize the database
import mysql.connector

# PHRASE CONSTANTS TO USE TO INSERT
insertCharacter = lambda game_character: "INSERT IGNORE INTO game_character (name) VALUES ('%s')" % game_character
insertGame = lambda game_title, release_date: "INSERT IGNORE INTO game (title, release_date) VALUES ('%s', '%s')" % (game_title, release_date)
insertRelation = lambda cname, gtitle: "INSERT IGNORE INTO appears_in (cname, gtitle) VALUES ('%s', '%s')" % (cname, gtitle)

# Create database if not exists
db1 = mysql.connector.connect(
    host        ="localhost",
    user        ="root",
    password    ="Password!"
)
cursor = db1.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS ryu_number;")
# Connect to the db we just created
mydb = mysql.connector.connect(
    host        ="localhost",
    user        ="root",
    password    ="Password!",
    database    ="ryu_number"
)
cursor = mydb.cursor()

# Create 'character' table
characterTable = "CREATE TABLE IF NOT EXISTS game_character (name VARCHAR(64) NOT NULL, ryu_number INTEGER DEFAULT 99, PRIMARY KEY (name));"
cursor.execute(characterTable)
# Create 'game' table
gameTable = "CREATE TABLE IF NOT EXISTS game (title VARCHAR(64) NOT NULL, ryu_number INTEGER DEFAULT 99, release_date DATE, PRIMARY KEY (title));"
cursor.execute(gameTable)
# Create 'appears_in' relation table
appearsInTable = "CREATE TABLE IF NOT EXISTS appears_in (cname VARCHAR(64) NOT NULL, gtitle VARCHAR(64) NOT NULL, PRIMARY KEY (cname, gtitle), FOREIGN KEY (cname) REFERENCES game_character(name), FOREIGN KEY (gtitle) REFERENCES game(title));"
cursor.execute(appearsInTable)

# Create the triggers to automatically set the Ryu Numbers
dropAI = "DROP TRIGGER IF EXISTS update_ai;"
updateAI = "CREATE TRIGGER update_ai AFTER INSERT ON appears_in FOR EACH ROW BEGIN \
    IF (SELECT ryu_number FROM game AS G WHERE G.title=NEW.gtitle) > (SELECT ryu_number FROM game_character AS C WHERE C.name=NEW.cname) THEN \
        UPDATE game AS G \
        SET ryu_number=(SELECT ryu_number FROM game_character AS C WHERE C.name=NEW.cname)+1 \
        WHERE G.title=NEW.gtitle; \
	ELSEIF (SELECT ryu_number FROM game_character AS C WHERE C.name=NEW.cname) > (SELECT ryu_number FROM game AS G WHERE G.title=NEW.gtitle) THEN \
        UPDATE game_character AS C \
        SET ryu_number=(SELECT ryu_number FROM game AS G WHERE G.title=NEW.gtitle) \
        WHERE C.name=NEW.cname; \
	END IF; END;"
cursor.execute(dropAI)
cursor.execute(updateAI)

# Add the legendary RYU himself
cursor.execute("INSERT IGNORE INTO game_character (name, ryu_number) VALUES ('Ryu', 0)")

### TEMP TEST ENTRIES TO VERIFY TRIGGERS ###
cursor.execute(insertCharacter("Kratos"))
cursor.execute(insertCharacter("Heihachi Mishima"))
cursor.execute(insertGame("Street Fighter X Tekken", "2012-03-06"))
cursor.execute(insertGame("PlayStation All-Stars Battle Royale", "2012-11-20"))
cursor.execute(insertRelation("Ryu", "Street Fighter X Tekken"))
cursor.execute(insertRelation("Heihachi Mishima", "Street Fighter X Tekken"))
cursor.execute(insertRelation("Heihachi Mishima", "PlayStation All-Stars Battle Royale"))
cursor.execute(insertRelation("Kratos", "PlayStation All-Stars Battle Royale"))
### END TEMP ENTRIES ###

mydb.commit()
mydb.close