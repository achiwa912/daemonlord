
# Table of Contents

1.  [dl.py - Daemon Lord](#orge31d192)
    1.  [Overview](#orgc6d9f64)
    2.  [Important: Under development](#orgeacf0b6)
2.  [Installation](#orgba0326b)
3.  [Prerequisites](#orga4a9702)
4.  [How to Play](#orgc03b5e2)
5.  [License](#orgbd9ff6a)
6.  [Appendix](#org867763c)
    1.  [Game start](#org54805b0)
    2.  [Edge of Town](#orgaf198db)
        1.  [Training Grounds](#org7362629)



<a id="orge31d192"></a>

# dl.py - Daemon Lord

Daemon Lord is a Wizardry-clone RPG with rogue-like (ie, text-based), randomly-created 2D maps.

     daemon lord - dl - [battle] floor: 3 ( 82/ 18) <identify> <light> ######...#^
    ^^^^##.########.#######^^#...######.######^^^^##.##########.....##########%##^
    ^^^^##.########.##^^^^^^^#...######.######^#####.......####.....###.........#^
    ^^^^##.##|   1) 6 lvl3 samurai             (6)                  |##.........#^
    ^^^^##.##|                                                      |##.........#^
    ^^^^#...#|                                                      |####.#######^
    #####...#|                                                      |####.###^^^^^
    #####...#^##.........#....#.##.........##.......++++.########.#######.######^^
    ........+| * What spell to cast?                                |.........##^^
    .*...++##| > taika                                              |.........##^^
    .########| * Press any key or t)ake back >                      |.........##^^
    ###......| * eddie thrusts violently at lvl3 samurai and hits 1 |########.##^^
    ###......|   times for 1 damage.                                |^^######.###^
    ^##......| * faun casted taika.                                 |^^^^####.###^
    ^##......|   lvl3 samurai incurred 15 damage.                   |######.....#^
    ^##......|   lvl3 samurai incurred 16 damage.                   |######.....#^
    ###......|   lvl3 samurai incurred 16 damage.                   |.....#.....#^
     # name  |   lvl3 samurai incurred 13 damage.                   |            ^
     1 ab    |   lvl3 samurai incurred 6 damage.                    |            ^
     2 ben   |   lvl3 samurai incurred 13 damage.                   |            ^
     3 chase      G-FIG   1  409 fight        .* west                            ^
     4 debbie     N-THI   8  306 fight        .* west                            ^
     5 eddie      G-PRI   8  391 fight        .* west                            ^
     6 faun       G-MAG   8  200 taika        .* *** encounter ***               ^


<a id="orgc6d9f64"></a>

## Overview

-   Wizardry clone
    -   Party of up to six members
    -   Battles with monster parties in the dungeon
    -   Gain experience points and level up
    -   Get gold and powerful items from trap-protected chests
    -   Roughly 50 magic spells, 100 items and 100 monsters (for now)
    -   Need to type spells and chest traps accurately
-   Rogue-like dungeon maps
    -   Text-based, 2D dungeon maps
    -   10 (or more) layers deep
    -   Maps are auto-generated.  Every time you go down the dungeon, you will see different maps
-   A little more friendly than the original
    -   Re-calculate the bonus value with '.' key when creating a character
    -   Age doesn't matter anymore
    -   "tsubasa" spell (mage level 2) will take your party to known depth
    -   Save and resume anywhere in the dungeon, preserving floor maps and effective spells such as identification of monsters or protection
    -   HP decrease by poison stops at HP = 1
    -   You don't have to pool gold anymore.  Someone in the party will pay for you
    -   Group heal spells for the entire party


<a id="orgeacf0b6"></a>

## Important: Under development

Currently, dl (daemon lord) is under development and has tons of bugs and not-yet-implemented features.  Please note that your saved file might become obsolete and be invalidated.  Backward compatibility is not supported.  Anything might change anytime.

Please send bug reports to achiwa912+gmail.com (replace '+' with '@').


<a id="orgba0326b"></a>

# Installation

1.  Setup python 3.8 or later
2.  Place dl.py, monsters.csv, spells.csv, items.csv in the same directory
3.  Run "python dl.py"


<a id="orga4a9702"></a>

# Prerequisites

-   macOS, Linux or Windows
    -   Developed on macOS BigSur and Fedora 32 but not tested on Windows
-   Python 3.8 or later (it uses assignment expression)
-   Terminal of 78x24 or larger
-   dl.py - the program
-   monsters.csv - monster definition file
-   spells.csv - spell definition file
-   items.csv - item definition file


<a id="orgc03b5e2"></a>

# How to Play

1.  Create and register characters at Proving Grounds
2.  Form a party at Hawthorne's Tavern
3.  Purchase weapons and armors at Trader Jay's
4.  Equip weaspns and armors at Hawthorne's Tavern
5.  Go in to the dungeon
6.  Battles with monsters
7.  Go back to the Edge of Town / Castle
8.  Have dinner and get rest at the Lakehouse Inn (you might level up)

You can save either at Edge of Town or from the Camp menu.
You can do resume operation only from Edge of Town.


<a id="orgbd9ff6a"></a>

# License

Daemon Lord is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
Daemon Lord - Copyright (C) 2021 Kyosuke Achiwa


<a id="org867763c"></a>

# Appendix


<a id="org54805b0"></a>

## Game start

DL starts with the screen below at the Castle.

    daemon lord - dl - [castle] floor:?? (???/???)                               
    
    
    
    	 | * *** Castle ***                                     |            
    	 |   h)awthorne tavern                                  |            
    	 |   t)rader jay's                                      |            
    	 |   i)lakehouse inn                                    |            
    	 |   m)oss general hospital                             |            
    	 |   e)dge of town                                      |            
    	 |   Command? >                                         |            
    	 |                                                      |            
    	 |                                                      |            
    	 |                                                      |            
    
    
    
    # name       class  ac   hp status                                           
    1                                                                            
    2                                                                            
    3                                                                            
    4                                                                            
    5                                                                            
    6

When you first start the game, you need to go to Edge of Town (press 'e') > Training Grounds (press 't'), and then create characters (press 'c').


<a id="orgaf198db"></a>

## Edge of Town


<a id="org7362629"></a>

### Training Grounds

At Training Grounds, you can create or inspect characters.  You create one character at a time.

    daemon lord - dl - [training_grounds] floor:?? (???/???)                     
    
    
    
    	 |   S)ave and quit game                                |            
    	 |   R)esume from saved data                            |            
    	 |   Command?  > t                                      |            
    	 | * *** training grounds ***                           |            
    	 |   c)reate a character                                |            
    	 |   i)nspect a character                               |            
    	 |   l)eave                                             |            
    	 |   Command? > c                                       |            
    	 | * Enter new name                                     |            
    	 | >                                                    |            
    
    
    
    # name       class  ac   hp status                                           
    1                                                                            
    2                                                                            
    3                                                                            
    4                                                                            
    5                                                                            
    6 

To create a character, input its name, choose race (human, elf, dwarf, gnome, hobbit) and alignment (good, neutral, evil), and input his/her age.  Race determines base attribute values.  In DL, age doesn't matter and its just for your imagination.

    |   Command? > c                                       |            
    | * Enter new name                                     |            
    | > Adrien                                             |            
    |   Choose race - h)uman e)lf d)warf g)nome o)hobbit > |            
    |   d                                                  |            
    | * dwarf                                              |            
    |   Choose alignment - g)ood n)eutral e)vil > g        |            
    | * Alignment: good                                    |            
    | * How old is he/she? (13-199)                        |            
    | > 22

Then you will distribute assigned bonus points to attributes.
Move the cursor `>` with `j, k` keys and decrease (`h`) or increase (`l`) the attribute value.  When bonus value is zero, you can choose a class by pressing `x`.

Eligible classes are displayed at the bottom of the window.  To choose a class, type the first character of a class.  For example, `f` for fighter, `m` for mage, etc.

Classes have attributes and in some cases alignment requirements.  For example, fighter requires strength>=11.  Theif requires agility>=11 as well as alignment must be either neutral or evil.

    daemon lord - dl - [training_grounds] floor:?? (???/???)                     
    
    	     | * Distribute bonus points -                       |            
    	     |     h)minus j)down k)up l)plus                    |            
    	  | *|     .)change bonus x)done                         |            
    	  | >|                                                   |            
    	  |  |     strength  18                                  |            
    	  |  |     iq        13                                  |            
    	  | *|     piety     14                                  |            
    	  |  |     vitality  10                                  |            
    	  | *|     agility  > 6                                  |            
    	  | *|     luck       6                                  |            
    	  | >|                                                   |            
    	  | *|     bonus      0                                  |            
    	     |                                                   |            
    	     |   fighter mage priest bishop                      |  
    	     |   Choose class (f/m/p/b) >                        | 

