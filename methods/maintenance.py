"""Module for maintaining and updating the database.

The methods held within this module are used to update the relations of
the database, fill the database with data, and reset the entire 
database. Each method's documentation describes it in greater detail.

All methods take two parameters (namely, debug and debug_detailed)
which determine whether or not to print debug statements, and if so,
how detailed to be with them.

Methods
-------
updateRelations(bool, bool) -> None
    Update the Ryu Numbers of each character in the database recursively.
fill_db(bool, bool) -> None
    Fill the database with data based on local text files found in `main.PATH`.
reset_db(bool, bool) -> None
    Re-initialize the entire database in memory.
"""

from classes import file_manager as fm
from init import initialize_db
from classes.ryu_connector import RyuConnector
from methods import queries

def updateRelations(debug: bool=False, debug_detailed: bool=False) -> None:
    """Update the Ryu Numbers of each character in the database recursively.
    
    The method increases a local counter (starting from 0), removing and 
    reinserting each character and game with a Ryu Number equal to that 
    value. This causes the database's triggers to fire, which automatically 
    update each character's and game's Ryu Numbers to be their minimum
    possible value.

    Parameters
    ----------
    debug: bool
        Whether or not to print debug statements. These include printing out how
        many characters and games to adjust per Ryu Number.
    debug_detailed: bool
        Whether or not to print detailed debug statements. This includes every
        normal debug statements, as well as indicating every character name and
        game title that is updated
    """
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

def fill_db(debug: bool=False, debug_detailed: bool=False) -> None:
    """Fill the database with data based on local text files found in `main.PATH`.
    
    After connecting to the database, each text file in `main.PATH` is 
    parsed for information. This information is parsed under the assumption
    that each file follows the convention that the file's `title`.txt is the
    game's `title`, the first line of the text file is the game's 
    `release_date`, and each subsequent line is the `name` of a character
    that appears in that game.

    After all the "raw data" is inserted, the relations are updated using 
    the `updateRelations()` method.

    NOTE: This code is set to run under the implication that the database
          has already been initialized.

    Parameters
    ----------
    debug: bool
        Whether or not to print debug statements for if files are being read.
    debug_detailed: bool
        Whether or not to print detailed debug statements for every game being
        parsed.
    """
    with RyuConnector() as rdb:
        # Start reading files and adding data
        if debug or debug_detailed: print("Reading files...")
        for filename in fm.getGameFiles():
            if debug_detailed: print(f"\tReading {filename}...")
            data = fm.parseGameFile(filename)
            rdb.execute(queries.insertGame(data["game"][0], data["game"][1]))
            # Get priority inserts
            rdb.execute(queries.getCharactersByNames(tuple(data["game_characters"])))
            priorityInserts = [c[0] for c in rdb.fetchall()]     # Names of characters who already exist in db (to insert FIRST)
            for x in priorityInserts:
                if x in data["game_characters"]:
                    data["game_characters"].remove(x)
            for c in priorityInserts:
                rdb.execute(queries.insertRelation(c, data["game"][0]))
            # Insert the remainder of characters
            for c in data["game_characters"]:
                rdb.execute(queries.insertCharacter(c))
                rdb.execute(queries.insertRelation(c, data["game"][0]))
        if debug or debug_detailed: print("Raw data inserted successfully.")
    
    updateRelations(debug, debug_detailed)

def reset_db(debug: bool=False, debug_detailed: bool=False) -> None:
    """Re-initialize the entire database in memory.
    
    The command will drop the entire schema, then reinitialize the database
    and reinsert all files.
    """
    with RyuConnector() as rdb:
        rdb.execute("DROP SCHEMA IF EXISTS ryu_number")
    # Now refill the whole db
    initialize_db(debug, debug_detailed)
    fill_db(debug, debug_detailed)