# RyuNumber

"Six degrees of separation" is the idea that you can be linked to any other person in the world through 6 or fewer social links. During the summer of 2021, a [subreddit](https://www.reddit.com/r/ryunumber/) (and eventually an unofficial [Twitter account](https://twitter.com/RyuNumber)) were created, relating this concept to the video game character of Ryu from the Street Fighter series. Without much better to do during quarantine, freshly equipped with the knowledge of MySQL, I decided to try turning this concept into a computerized database, allowing characters to be both added and found more easily. The "rules" of a given character's Ryu Number can be found on both the Twitter and Reddit pages. Of note are the primary 4 rules:
1. Video games only
2. Commercial works only
3. No time-limited character access (e.g. "gacha" or Fortnite events)
4. Identifiably unique individuals (no common species e.g. Goombas or Koopas)

This is similar in concept to [Bacon numbers](https://en.wikipedia.org/wiki/Six_Degrees_of_Kevin_Bacon) (which link actors to Kevin Bacon by way of appearances in film) or [Erdős numbers](https://en.wikipedia.org/wiki/Erd%C5%91s_number) (which link mathematicians and researchers to Paul Erdős by way of collaborating on scientific papers).

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

The meat and potatoes of this entire project: figuring out how characters are related to Ryu. After entering the name of a character and selecting them from the result viewer, one can see a path of how that character is linked to Ryu from Street Fighter. These paths can be either chosen randomly, or selected from a list of potential options. If chosen from potential options, results will be provided of games and characters with Ryu numbers one less than the current option, until eventually reaching Ryu. See the below example for the random path between Son Goku of Dragon Ball (who has a Ryu Number of 3) to Ryu.

![image](https://user-images.githubusercontent.com/51037424/143779769-3fe9439c-856d-4263-b62c-694931c1a09d.png)

`(n/N) See stats about the database`

View statistics about the characters and games in the database. Alternatively, you could see all stats as well, which includes both the number of characters and games per Ryu number, as well as the total number of games and characters. The only character with a Ryu Number of 0 is Ryu himself. (Note that the below screenshot is from the time of this commit, which is November 28, 2021. The true number of characters and games may fluctuate over time)

![image](https://user-images.githubusercontent.com/51037424/143779826-2ee7a859-a60e-4029-86a6-c116274ba7a8.png)

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

This database is very graph-like in structure. That is, Ryu operates as a root node, linking games and characters together through `appears_in` relations, which act as edges. Each `game` and `game_character` acts as a node on this graph, and many of the operations take advantage of this. 

This Ryu number value is the degree by which a character or game is separated from Ryu. For instance, a character with a Ryu number of 1 is a character that has fought Ryu directly (e.g. Chun-Li in Street Fighter II, or Super Mario in Super Smash Bros.), while a character with a Ryu number of 2 is a character who has fought a character that has fought Ryu (e.g. Kratos fights Heihachi Mishima in PlayStation All-Stars, and Heihachi fights Ryu in Street Fighter X Tekken). The Ryu number for games, however, indicates that every character in that game has a Ryu number of that number **at most** (e.g. Street Fighter II has a Ryu number of 1, since every character in that game can fight Ryu, but Ryu himself has a Ryu number of 0). This helps simplify the path-finding algorithm employed to link characters to Ryu.

Let's use the example of Zagreus (from the game Hades) to explain the path-finding algorithm. To find a link from him to Ryu, the first query that runs is to find games that this character appears in, that also have the same Ryu number as them. In Zagreus' case (as of right now), the only option is through his debut game "Hades". Once selected, the next query that runs will return all characters who appear in Hades, whose Ryu numbers are **one fewer** than that of the game. If the command were retrieving a random path, a character from this list would be selected at random. However, assuming we can choose, let's arbitrarily select Hades himself, whose Ryu number is 2. The last two steps will then repeat, querying game followed by character, until we reach a character with a Ryu number of 0. This is Ryu himself, and at this point, we return the list of all the characters and games we've come across.

When a new game or character is added, their Ryu number defaults to 99. When it is linked with a character or game whose Ryu number is less than this, SQL triggers update its value accordingly. However, since SQL triggers are not recursive, it is not always guaranteed that an updated Ryu number will be accurate to what it truly is. The "reset database" command is my response to this, which uses a BFS-style algorithm to sequentially update each Ryu number from 0 to whatever the current linked maximum is.

All input data is currently stored in .txt files under the "Games List" folder, following this convention:
- The file's name is the title of the game;
- The first line of the file is the game's release date; and
- Every subsequent line in the file indicates a character that appears in the game.

Games are inserted by reading these files and parsing the data in this fashion, which ensures it is entered properly. However, for best results, it is recommended to use the terminal's "insert game" functionality, which lets the user ensure that the character they are refering to exists or does not exist in the database.

# Using It For Yourself

There are a few things you'll need to set if you'd like to use this database for yourself:

1. Ensure you have downloaded `python3` and `MySQL` such that they can run on your OS. In addition, ensure you have python's `mysql-connector` downloaded as well, which can be done from terminal using the following command: `pip install mysql-connector-python`
2. Navigate to this directory your terminal.
3. Alter `db.txt` such that the lines are the following:
  - Line 1: The host name
  - Line 2: Your user name
  - Line 3: The password to your user name
  - Line 4: `ryu_number` (leave as is, as this is the database name)
4. Run the command `python3 main.py` and type "r", then "h" to initialize and reset the database, ensuring the existing characters' Ryu numbers update correctly.
5. Have fun running any other commands you wish!

# Potential Improvements

- Currently, characters' names will have their series in brackets to prevent duplicate entries, though there could be struggle in deciding whether or not to add this to a characters' name. An ID or indexing system could be put in place instead to alleviate this issue, allowing for names to be duplicated without confusion.
- There is limited data on characters and games, only recalling their name, title, and release date. More parameters could be added, though the terminal would also need the necessary commands to implement these.
- It is *theoretically* possible to recenter the database on any other character besides Ryu (for instance, giving Super Mario the Ryu number 0). This would allow you to calculate the "Mario number" of characters as well. This concept could have potential, but for now, leaving it to centralize on Ryu is simplest.
