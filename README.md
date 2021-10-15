# RyuNumber

"Six degrees of separation" is the idea that you can be linked to any other person in the world through 6 or fewer social links. During the summer of 2021, a [subreddit](https://www.reddit.com/r/ryunumber/) (and eventually an unofficial [twitter account](https://twitter.com/RyuNumber)) were created, relating this concept to the video game character of Ryu from the Street Fighter series. Without much better to do during quarantine, freshly equipped with the knowledge of MySQL, I decided to try turning this concept into a computerized database, allowing characters to be both added and found more easily.

# Contents

- [Functionality](#functionality)
  - [Query Commands](#query-commands)
  - [Alter Database Commands](#alter-database-commands)
  - [Maintenance](#maintenance)
- [How It Works](#how-it-works)
- [Using It For Yourself](#using-it-for-yourself)
- [Potential Improvements](#potential-improvements)

# Functionality
The application runs from a terminal window, which displays and stores all of the commands. I am running it through Ubuntu, which is where the following demo images are taken from. The menu window lists all available commands that the user can run:

![image](https://user-images.githubusercontent.com/51037424/137553928-148d8131-ae87-4d26-bf32-c47b95829076.png)

### Query Commands

`(c/C) Query a character (exactly)`

Allows you to query a character from the database, assuming they exist. Using an uppercase `C` will search for that character specifically, while a lowercase `c` will run through names that may also be similar. Within the result viewer window, pages can be flipped using `n` and `p`, or a character can be selected from the list by entering the number beside their name. If no characters exist, a message will be displayed that there are no characters in the database with the provided name. Below is an example of one such query for characters named "Mario". When printing the character's name, their Ryu number appears in square brackets, and all games they appear in (in the database) appear underneath them, indented once.

![image](https://user-images.githubusercontent.com/51037424/137555126-df9854d2-f096-4dd3-aa75-003cd0609cc9.png)

`(g/G) Query a game (exactly)`

Similarly to querying for characters, searches the database for games. Using an uppercase `G` will search for the exact title of a game, while lowercase `g` will find all similar games. Below is an example of one such query for games named "Tekken". When printing games, the name of the game is printed, followed by the release date in round brackets, and that game's Ryu number in square brackets.

![image](https://user-images.githubusercontent.com/51037424/137554895-8f7621c6-737a-4d30-90f6-6411ab11b107.png)

`(p/P) Get a path from a character to Ryu`

The meat and potatoes of this entire project: figuring out how characters are related to Ryu. After entering the name of a character and selecting them from the result viewer, a path is returned of how that character is linked to Ryu from Street Fighter. See the below example for the path between Son Goku of Dragon Ball (who has a Ryu Number of 3) to Ryu.

![image](https://user-images.githubusercontent.com/51037424/137555460-6463b4c5-f111-4e23-b7e8-15321ce8eed6.png)

`(n/N) See stats about the database`

View statistics about the characters and games in the database. Alternatively, you could see all stats as well, which includes both the number of characters and games per Ryu number, as well as the total number of games and characters. The only character with a Ryu Number of 0 is Ryu himself. (Note that the below screenshot is from the time of this commit, which is October 15, 2021, and there could have been more characters and games added)

![image](https://user-images.githubusercontent.com/51037424/137555810-9fac8cd5-87fc-4dfd-b833-ef242b7a0c75.png)

### Alter Database Commands

`(i/I) Insert a game and characters into the DB`

A prompt will appear to enter the name of the game and its release date. After that, characters' names can be entered one at a time to be included in that game.

In the event that a name is written that matches with one already in the database, you have the option of using that specific name instead, indicating that this specific character appears in this game as well. Otherwise, you can always leave what you wrote and include the new character to the database as well. If the character does not yet exist in the database yet, it will be indicated, and you'll have the option to confirm or deny inserting that character. This has proved useful for me, since it lets me quickly see if a character exists in the database or not, while not confining myself to enter every name right in that moment.

If at any point you change your mind about including the game, you can always type ".", which will cancel the insertion entirely.

When you are finished entering names for the game, simply press enter with nothing typed and it will complete the insertion, returning you to the menu.

`(a/A) Add characters to an existing game`

While the `A` also stands for "append", this command lets you include more characters to a game. After being prompted for the name of the game and making a selection, you run through a similar screen as adding characters to a new game, except that the names entered will go into the game you selected. This is useful for games that include DLC that has yet to be announced (like Super Smash Bros. Ultimate), or games that were added with missing characters.

`(x/X) Remove an item from the database`

After entering this command, you will be prompted as to whether you'd like to remove a character or game. You can then enter the character's name or game's title to search and select the one you'd like to remove.

If you're removing a character, you will be asked whether you'd like to remove it from one game specifically, or from the entire database. Removing from the entire database will also remove them from every game they've appeared in.

If you're removing a game, you'll be asked to confirm the deletion. However, any characters who relied on that game for their Ryu number may be lost after the deletion.

`(u/U) Update a character or game`

This command is useful for updating a character's name, or a game's title or release date. After searching for the desired element to change, you'll be asked what you'd like to change, and what you want to change it to. Upon confirmation, the changes will occur instantly in the database.

### Maintenance

`(v/V) Toggle view to be compact or descriptive`

This command simply alters the menu between one of two states. The descriptive menu is the one shown at the beginning, while the compact menu looks as follows:

![image](https://user-images.githubusercontent.com/51037424/137556760-760c577d-cbe2-40b0-afff-963ceba98225.png)

`(r/R) Reset the database (include all details)`

This command does just as it says and resets all the information in the database. It can be useful after many updates, deletions, or insertions that may scramble with some characters' Ryu numbers. It will ask for confirmation before running, however, since the full process takes some time to fully execute.

In technical terms, this command reinserts every relation sequentially starting with Ryu. It is easiest to consider by thinking about the database as a massive graph, where each node is either a game or character, and edges symbolize that a character appears in a game. All relations to Ryu are the first to be reset, where any game he appears in are removed and reinserted to allow the MySQL triggers to fire according to their condition. (The reason this is not done on insert is that MySQL triggers are not recursive) After this, all characters appearing in those game have their relations reinserted with those games as well, and the cycle repeats with characters of Ryu number 1, 2, up until the highest number in the database.

`(q/Q) Close the database and quit`

Ends the runtime of the application.

# How It Works

Many of the database functions simply run combinations of SQL queries to affect the database. But how does this database work?

The MySQL database operates with three tables: `game`, `game_character`, and `appears_in`. They each represent a game, a character from a video game, and the relational representation of a character appearing in a game (i.e. Chun-Li appears in Street Fighter II) respectively. The game table has attributes of `title` for the title of the game (which serves as the primary key), and `release_date`, which is the soonest day the game was released. The game character table only has the descriptive attribute of `name`, which is the character's full name (or at least as much of the name is known of the character). In cases where two characters have the same name, that character's series will be put in brackets after their name (i.e. Zero from Mega Man X, Zero from Kingdom Hearts II,and Zero from Sonic Adventure).

The game and game character tables also each have Ryu number attributes, which are initialized to 99 by default. Each number indicates the degree by which each character is related to Ryu. Characters with a Ryu number of 1 are characters that Ryu has formally seen, met, or fought. This goes for characters like Chun-Li, Iron Man, or Super Mario. Games with a Ryu number of 1 are those where the lowest possible Ryu number of a character is 0, and the highest possible Ryu number is 1. This goes for games like Street Fighter II or Marvel vs. Capcom. The line of reasoning is that any game with a Ryu number of 1 means every character that appears in that game alone will have a Ryu number of at most 1. It also aids in computing the path between characters and Ryu.

In the `Games List` folder, there are text files which each represent games. The file name is the title of the game, and the first line of each game is its release date. After this, every subsequent line is a character that appears in that game. Considering how many games feature crossovers, it is more optimal to store the games as text objects rather than having text objects for every character.

All relations are presumed to be defined with the precondition that Ryu, with a Ryu number of 0, exists in the database always. Given how the code is implemented, this should always be the case. When being inserted, it is akin to using breadth-first search, with Ryu being the central node, and edges representing `appears_in`.

# Using It For Yourself

There are a few things you'll need to set if you'd like to use this database for yourself:

1. Ensure you have downloaded `python3` and `MySQL` such that they can run on your OS. In addition, ensure you have python's `mysql-connector` downloaded as well, which can be done from terminal using the following command: `pip install mysql-connector-python`
2. Navigate to this directory your terminal.
3. Alter `db.txt` such that the lines are the following:
  - Line 1: The host name
  - Line 2: Your user name
  - Line 3: The password to your user name
  - Line 4: `ryu_number` (leave as is, as this is the database name)
4. Begin by running the command `python3 init.py` to set up the proper schema, table, and triggers.
5. Run the command `python3 fill_db.py` to insert all the data in "Games List" into the database.
6. Run the command `python3 main.py` and type "r" to reset the database, ensuring the existing characters' Ryu numbers update correctly.
7. Have fun running any other commands you wish!

# Potential Improvements

- Currently, characters' names will have their series in brackets to prevent duplicate entries, though there could be struggle in deciding whether or not to add this to a characters' name. An ID or indexing system could be put in place instead to alleviate this issue, allowing for names to be duplicated without confusion.
- There is limited data on characters and games, only recalling their name, title, and release date. More parameters could be added, though the terminal would also need the necessary commands to implement these.
- It is *theoretically* possible to recenter the database on any other character besides Ryu (for instance, giving Super Mario the Ryu number 0). This would allow you to calculate the "Mario number" of characters as well. This concept could have potential, but for now, leaving it to centralize on Ryu is simplest.
- Resetting the database does take some time, and as I become more familiar with Python's file I/O, I *may* be able to simplify this process.
