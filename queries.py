# THIS FILE SHOULD BE USED EXCLUSIVELY FOR STORING QUERIES

# Character queries
insertCharacter = lambda gc: "INSERT IGNORE INTO game_character (name) VALUES ('%s')" % gc
getCharacterByName = lambda gc: "SELECT * FROM game_character WHERE name LIKE '%%%s%%' ORDER BY ryu_number ASC" % gc
getCharacterByNameExact = lambda gc: "SELECT * FROM game_character WHERE name='%s'" % gc
getCharactersByNames = lambda gc: "SELECT * FROM game_character WHERE name IN %s ORDER BY ryu_number ASC" % gc  # NOTE: param must be a tuple
getCharactersByGame = lambda gt: "SELECT name, ryu_number FROM game_character, appears_in WHERE appears_in.cname=game_character.name AND appears_in.gtitle='%s'" % gt
getCharacterByRyu = lambda rn: "SELECT * FROM game_character WHERE ryu_number=%d" % rn

# Game queries
insertGame = lambda game_title, release_date: "INSERT IGNORE INTO game (title, release_date) VALUES ('%s', '%s')" % (game_title, release_date)
getGameByTitle = lambda gt: "SELECT * FROM game WHERE title LIKE '%%%s%%' ORDER BY ryu_number ASC" % gt
getGameByTitleExact = lambda gt: "SELECT * FROM game WHERE title='%s'" % gt
getGamesByTitles = lambda gt: "SELECT * FROM game WHERE title IN %s ORDER BY ryu_number ASC" % gt   # NOTE: param must be a tuple
getGamesByCharacter = lambda gc: "SELECT title, ryu_number, release_date FROM appears_in, game WHERE appears_in.cname='%s' AND appears_in.gtitle=game.title" % gc
getGamesByRyu = lambda rn: "SELECT * FROM game WHERE ryu_number=%d" % rn

# Relation queries
insertRelation = lambda cname, gtitle: "INSERT IGNORE INTO appears_in (cname, gtitle) VALUES ('%s', '%s')" % (cname, gtitle)
getRelationByCharacter = lambda gc: "SELECT cname, gtitle, ryu_number FROM appears_in INNER JOIN game_character ON cname=name WHERE cname='%s'" % gc
getRelationByGame = lambda gt: "SELECT cname, gtitle, ryu_number FROM appears_in INNER JOIN game ON gtitle=title WHERE gtitle='%s'" % gt
removeCharacterRelations = lambda gc: "DELETE FROM appears_in WHERE cname='%s'" % gc
removeGameRelations = lambda gt: "DELETE FROM appears_in WHERE gtitle='%s'" % gt

# Ryu Number queries
getGameFromCharacter = lambda cname: "SELECT DISTINCT G.title, G.ryu_number FROM appears_in INNER JOIN game_character AS C ON cname=C.name INNER JOIN game AS G ON gtitle=G.title WHERE cname LIKE '%s' AND G.ryu_number=C.ryu_number;" % cname
getCharacterFromGame = lambda gtitle: "SELECT DISTINCT C.name, C.ryu_number FROM appears_in INNER JOIN game_character AS C ON cname=C.name INNER JOIN game AS G ON gtitle=G.title WHERE gtitle LIKE '%s' AND C.ryu_number=G.ryu_number-1;" % gtitle