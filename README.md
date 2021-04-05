
# Table of Contents

1.  [dl.py - Daemon Lord](#org26f34a8)
    1.  [Overview](#orge77395a)
    2.  [Important: Under development](#org1b85d34)
2.  [Installation](#org933065c)
3.  [Prerequisites](#org2754caf)
4.  [How to Play](#org0002b98)
5.  [License](#orgb60e389)



<a id="org26f34a8"></a>

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


<a id="orge77395a"></a>

## Overview

-   Wizardry clone
    -   Party of up to 6 adventuers
    -   Battles with monster parties
    -   Gain experience points and level up
    -   Get gold and powerful items from trap-protected chests
    -   Roughly 50 magic spells, 100 items and 100 monsters (for now)
    -   Need to type spells and chest traps accurately
-   Rogue-like dungeon maps
    -   Text-based, 2D dungeon maps
    -   10 (or more) layers deep
    -   Maps are uuto-generated.  Every time you go down the dungeon, you will see different maps
-   A little more friendly than the original
    -   Re-calculate the bonus value with '.' key when creating a character
    -   Age doesn't matter anymore
    -   "tsubasa" spell (mage level 2) will take your party to known floors
    -   Save and resume anywhere in the dungeon, preserving floor maps and effective spells such as identification of monsters or protection
    -   HP decrease by poison stops at HP = 1
    -   You don't have to pool gold anymore.  Someone in the party will pay for you
    -   Group heal spells for an entire party


<a id="org1b85d34"></a>

## Important: Under development

Currently, dl (daemon lord) is under development and has tons of bugs and not-yet-implemented features.  Please note that your saved file might become obsolete and be invalidated.  Backward compatibility is not supported.  Anything might change anytime.

Please send bug reports to achiwa912+gmail.com (replace '+' with '@').


<a id="org933065c"></a>

# Installation

1.  Setup python 3.8 or later
2.  Place dl.py, monsters.csv, spells.csv, items.csv in the same directory
3.  Run "python dl.py"


<a id="org2754caf"></a>

# Prerequisites

-   macOS, Linux or Windows
    -   Developed on macOS BigSur and Fedora 32
-   Python 3.8 or later (it uses assignment expression)
-   Terminal of 78x24 or larger
-   dl.py - the program
-   monsters.csv - monster definition file
-   spells.csv - spell definition file
-   items.csv - item definition file


<a id="org0002b98"></a>

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


<a id="orgb60e389"></a>

# License

Daemon Lord is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
Daemon Lord - Copyright (C) 2021 Kyosuke Achiwa

