import mysql.connector
import queries

# THIS IS A VERY TIME-COSTLY METHOD SO ONLY USE IT IF ABSOLUTELY NECESSARY
def updateRelations():
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
    characterQueue = []
    gameQueue = []
    characterQueue.append("Ryu")
    for i in range(6):
        for c in characterQueue:
            characterQueue.pop(0)
            cursor.execute(queries.getRelationByCharacter(c))
            relations = cursor.fetchall()
            cursor.execute(queries.removeCharacterRelations(c))
            for row in relations:
                if row[1] not in gameQueue:
                    gameQueue.append(row[1])
                cursor.execute(queries.insertRelation(c, row[1]))
        for g in gameQueue:
            gameQueue.pop(0)
            cursor.execute(queries.getRelationByGame(g))
            relations = cursor.fetchall()
            cursor.execute(queries.removeGameRelations(g))
            for row in relations:
                if row[0] not in characterQueue:
                    characterQueue.append(row[0])
                cursor.execute(queries.insertRelation(row[0], g))
    
    mydb.commit()
    mydb.close()