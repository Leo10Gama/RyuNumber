# NOTE: This script should only be run ONCE to initialize the database
import mysql.connector

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
appearsInTable = "CREATE TABLE IF NOT EXISTS appears_in (cname VARCHAR(64) NOT NULL, gtitle VARCHAR(64) NOT NULL, FOREIGN KEY (cname) REFERENCES game_character(name), FOREIGN KEY (gtitle) REFERENCES game(title));"
cursor.execute(appearsInTable)

# Create the triggers to automatically set the Ryu Numbers
dropAI = "DROP TRIGGER IF EXISTS update_ai;"
updateAI = "CREATE TRIGGER update_ai AFTER INSERT ON appears_in FOR EACH ROW BEGIN \
    IF (SELECT ryu_number FROM game WHERE title=NEW.gtitle) > (SELECT ryu_number FROM game_character WHERE name=NEW.cname) THEN UPDATE game SET ryu_number=(SELECT ryu_number FROM game_character WHERE name=NEW.cname)+1 WHERE title=NEW.gtitle;\
	ELSEIF (SELECT ryu_number FROM game_character WHERE name=NEW.cname) > (SELECT ryu_number FROM game WHERE title=NEW.gtitle) THEN UPDATE game_character SET ryu_number=(SELECT ryu_number FROM game WHERE title=NEW.gtitle) WHERE name=NEW.cname;\
	END IF; END;"
dropChar = "DROP TRIGGER IF EXISTS update_char;"
updateChar = "CREATE TRIGGER update_char \
AFTER UPDATE ON game_character \
FOR EACH ROW \
	UPDATE game \
    SET ryu_number=NEW.ryu_number+1 \
    WHERE appears_in.cname=NEW.name AND appears_in.gtitle=title AND ryu_number>(NEW.ryu_number+1);"
dropGame = "DROP TRIGGER IF EXISTS update_game;"
updateGame = "CREATE TRIGGER update_game \
AFTER UPDATE ON game \
FOR EACH ROW \
	UPDATE game_character \
    SET ryu_number=NEW.ryu_number \
    WHERE appears_in.cname=name AND appears_in.gtitle=NEW.title AND ryu_number>NEW.ryu_number;"
cursor.execute(dropAI)
cursor.execute(updateAI)
cursor.execute(dropChar)
cursor.execute(updateChar)
cursor.execute(dropGame)
cursor.execute(updateGame)

# Add the legendary RYU himself
cursor.execute("INSERT INTO game_character (name, ryu_number) VALUES ('Ryu', 0)")

mydb.commit()
mydb.close