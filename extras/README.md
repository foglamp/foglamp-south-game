Extra scripts used in the game scoring
======================================

`scores.py` collects the scores from each car in the game and outputs the
rolling totals on standard output. Run one copy of this script for each
car and redirect the output to a file named carX. It is important this
script is run with the -u flag.

python -u scores.py <hostname>


`scoreboard.sh` reads the latest scores from each file being written by
the scores.py script and creates a combined scoreboard for the game. Edit
this files to maintain the list of car files to be read for the scoreboard.

`scoreboard.awk` formats and displays the scoreboard.
