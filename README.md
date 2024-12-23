# SepGame_PGN
A little console utility to split a chess pgn file into separate games outputting a single pgn file for each game.


 ---------------------------
 Sep_Game_Pgn by Jim Ablett.
 ---------------------------


 Each single game pgn file is uniquely named with the players names and put in a unique folder named after the 
 event in which the match took place. This is the default when you run the program without any command line switches.
 
 
 How to use:
 
 Put the pgn/s you want to split in the same folder as the program as run it. All new game pgns will be placed in the
 'output' folder 
 
 
 [no switches]
 e.g 'sepgame-pgn.exe' to output all the separate games of each event to an individual folder with the event's name.
 
 
 [--players]
 Add the command line switch '--players' e.g 'sepgame-pgn.exe --players' to output all the separate games of each player 
 to an individual folder with the players name. 
 
 
 [--openings]
 Add the command line switch '--openings' e.g 'sepgame-pgn.exe --openings' to output all the separate games of each opening 
 to an individual folder with the opening's name.  Output is dependant on there being an 'Opening' tag in the game header 
 of the file.
 
 
 [--eco]
 Add the command line switch '--eco' e.g 'sepgame-pgn.exe --eco' to output all the separate games of each eco opening to an 
 individual folder with the eco opening's eco code plus full opening's name. Output is dependant on there being an 'ECO' tag 
 in the game header of the file.
 
 
 [--onefile]
 Add the command line switch '--onefile' to any of the other switches 
 
 
 e.g 'sepgame-pgn.exe --players --onefile' 
 to output a single pgn file combining all the games of each player to an individual folder with the players name.
 
 e.g 'sepgame-pgn.exe --openings --onefile' 
 to output a single pgn file combining all the games of each opening to an individual folder with the opening's name.  

 e.g 'sepgame-pgn.exe --eco --onefile' 
 to output a single pgn file combining all the games of each eco opening to an individual  folder with the eco opening's eco code 
 plus full opening's name.
 
 
 
 If the program cannot find an eco or openings header tag in any game (when using --eco or --openings) it will output using 
 the 'Event' tag instead for that particular game and continue.
 
 
 
 
 I recommend only using this tool on an ssd and make sure the ssd is trimmed before use.  It can potentially create
 thousands of files.
 