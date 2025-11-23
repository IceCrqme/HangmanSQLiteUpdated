# HangmanSQLite
Hangman new 
Hangman Game (Tkinter + SQLite)

A graphical Hangman Game built with Python and Tkinter, featuring:

Random words stored in an SQLite database

Multiple categories (Programming, Animals, Countries)

On-screen QWERTY keyboard

Hints, reset, and category selection

Features

✅ Graphical interface using Tkinter
✅ Words fetched randomly from SQLite database
✅ Selectable categories (“Programming”, “Animals”, “Countries”, or “All”)
✅ Interactive QWERTY keyboard
✅ Hint system (reveals one hidden letter)
✅ Reset game and auto new round
✅ Simple, offline — no external dependencies beyond Python standard libraries
✅ Sound effects and background music using pygame, with music on/off toggle


How It Works

When the program starts, it checks if the words.db file exists.

If not, it automatically creates the database and inserts default words.

Choose a category from the dropdown menu and press Start Game.

Guess letters using either:

The text entry box, or

The on-screen keyboard (QWERTY layout).

You have 6 attempts to guess the word before the hangman is complete.

Press Hint (enabled mid-game) to reveal a random letter.

Press Reset to start a new round.



Technologies Used
Python 3
Tkinter (for GUI)
SQLite3 (for local database)
Random (for word selection)

Installation:
1.Clone the repository:
git clone https://github.com/YOUR_USERNAME/hangman-sqlite.git
cd hangman-sqlite

2.Run the game:
python hangman.py

