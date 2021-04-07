
# Table of Contents

1.  [dl.py - Daemon Lord](#org532a630)
    1.  [Overview](#org27cb574)
        1.  [Wizardry clone](#org795c107)
        2.  [Rogue-like dungeon maps](#org4af854e)
        3.  [A little more friendly than the original](#org4e62e9e)
    2.  [Important notice: Under development](#org882529c)
2.  [Installation](#org97069f5)
3.  [Prerequisites](#org0094b6c)
4.  [How to Play](#orgc3cc554)
5.  [License](#orgfd9f63e)
6.  [Quick Tour of Daemon Lord](#org2bb327a)
    1.  [Game start](#orgd8c4ce8)
    2.  [Edge of Town](#org8e62709)
        1.  [Training Grounds](#org1e25c25)
    3.  [Castle](#org5ec3712)
        1.  [Hawthorne Tavern](#org168e246)
        2.  [Trader Jay's](#orgfc705c2)
        3.  [Equip](#orgf5d5d69)
    4.  [Save and Resume](#org7188287)
    5.  [Dungeon](#org84f234d)
        1.  [Walk around the Dungeon](#orgc6534b3)
        2.  [Battle](#orgd287008)
        3.  [Friendly monsters](#org1f71867)
        4.  [Get ouf of the Dungeon](#orgb7dc2b4)
        5.  [A new dungeon!](#org4dc5981)
        6.  [Camp](#org37a835d)
    6.  [Castle](#org7e74f1b)
        1.  [The Lakehouse Inn](#org55a40d4)



<a id="org532a630"></a>

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


<a id="org27cb574"></a>

## Overview


<a id="org795c107"></a>

### Wizardry clone

-   Based on Wizardry I; Proving Grounds of the Mad Overlord
-   Party of up to six members
-   Battles with monster parties in the dungeon
-   Gain experience points and level up
-   Get gold and powerful items from trap-protected chests
-   Roughly 50 magic spells, 100 items and 100 monsters (for now)
-   Need to type spells and chest traps accurately


<a id="org4af854e"></a>

### Rogue-like dungeon maps

-   Text-based, 2D dungeon maps
-   10 (or more) layers deep
-   Maps are auto-generated.  Every time you go down the dungeon, you will see different maps


<a id="org4e62e9e"></a>

### A little more friendly than the original

-   Re-calculate the bonus value with `.` key when creating a character
-   Age doesn't matter anymore
-   "tsubasa" spell (mage level 2) will take your party to known depth
-   Save and resume anywhere in the dungeon, preserving floor maps and effective spells such as identification of monsters or protection
-   HP decrease by poison stops at HP = 1
-   You don't have to pool gold anymore.  Someone in the party will pay for you
-   Group heal spells for the entire party


<a id="org882529c"></a>

## Important notice: Under development

Currently, DL (daemon lord) is under development and has tons of bugs and not-yet-implemented features.  It is below alpha quality and not playable yet as of April 6th, 2021.  Please note that your saved file might become obsolete and be invalidated.  Backward compatibility is not supported.  Anything might change anytime.

Please send bug reports to achiwa912+gmail.com (replace '+' with '@').


<a id="org97069f5"></a>

# Installation

1.  Setup python 3.8 or later
2.  Place dl.py, monsters.csv, spells.csv, items.csv in the same directory
3.  Run "python dl.py"


<a id="org0094b6c"></a>

# Prerequisites

-   macOS, Linux (or Windows)
    -   Developed on macOS BigSur and Fedora 32
    -   It might run on Windows but not tested
-   Python 3.8 or later (it uses the "walrus" assignment expression)
-   Terminal of 78x24 or larger
-   dl.py - the program
-   monsters.csv - monster data file
-   spells.csv - spell data file
-   items.csv - item data file


<a id="orgc3cc554"></a>

# How to Play

1.  Create and register characters at Training Grounds
2.  Form a party at Hawthorne Tavern
3.  Purchase weapons and armors at Trader Jay's
4.  Equip weaspns and armors at Hawthorne's Tavern
5.  Go in to the dungeon
6.  Battles with monsters
7.  Go back to the Edge of Town / Castle
8.  Get some rest at the Lakehouse Inn (you might level up)

You can save either at Edge of Town or from the Camp menu.
You can perform resume operation only from Edge of Town.


<a id="orgfd9f63e"></a>

# License

Daemon Lord is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
Daemon Lord - Copyright (C) 2021 Kyosuke Achiwa


<a id="org2bb327a"></a>

# Quick Tour of Daemon Lord


<a id="orgd8c4ce8"></a>

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

When you first start the game, you need to go to Edge of Town (press `e`) > Training Grounds (press `t`), and then create characters (press `c`).


<a id="org8e62709"></a>

## Edge of Town


<a id="org1e25c25"></a>

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

To create a character, input its name, choose race (human, elf, dwarf, gnome, hobbit) and alignment (good, neutral, evil).  Race determines base attribute values as in Wizardry.  For example, human's base strength is 8.

    |   Command? > c                                       |            
    | * Enter new name                                     |            
    | > Adrien                                             |            
    |   Choose race - h)uman e)lf d)warf g)nome o)hobbit > |            
    |   d                                                  |            
    | * dwarf                                              |            
    |   Choose alignment - g)ood n)eutral e)vil > g        |            
    | * Alignment: good                                    |            

Then you will distribute assigned bonus points to attributes.
Move the cursor `>` with `j, k` keys and decrease (`h`) or increase (`l`) the attribute value.  When bonus value reaches zero, you can choose a class by pressing `x`.  The maximum attribute values here is 18 (but subject to change).

Tip: If you don't like the bonus point assigned, you can recalculate one with `.` key.  You might want to recalculate bonus until you get 16 or higher.

Eligible classes are listed at the bottom of the window.  To choose a class, type the first letter of a class.  For example, `f` for fighter, `m` for mage, etc.

Classes have attribute requirements and in some cases alignment requirements as in Wizardry.  For example, fighter requires strength>=11.  Theif requires agility>=11 as well as alignment must be either neutral or evil.

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

A recommended party consists of three fighters, a thief, a priest and a mage.  You should create six characters before going into the dungeon.  Tip: You should have one thief in your party.  Without one, you might not be able to unlock doors in the dungeon.

To view created charactes, type `i` at the Training Grounds menu.

    | * *** training grounds ***                           |            
    |   c)reate a character                                |            
    |   i)nspect a character                               |            
    |   l)eave                                             |            
    |   Command? >                                         |

You can move cursor with `j, k` key and type `i` to view the character.

    | * Inspect characters                                   |          
    | *  - j)down k)up i)nspect d)elete l)eave               |          
    |    >1 ab               Lv  1 dwa-g-fig                 |          
    |     2 ben              Lv  1 hum-g-fig                 |

    daemon lord - dl - [training_grounds] floor:?? (???/???)                     
    
    	 |   ab               L  1 g-fig dwarf                    |          
    	 |                                                        |          
    	 |   strength 18  gold              102   lvl     1       |          
    	 |       i.q.  7  e.p.                0   rip     0       |          
    	 |      piety 10  next             1000   a.c.   10       |          
    	 |   vitality 13  marks               0                   |          
    	 |    agility 11  h.p.       13/     13                   |          
    	 |       luck  8  status OK                               |          
    	 |                                                        |          
    	 |   mage  0/0/0/0/0/0/0   priest  0/0/0/0/0/0/0/         |          
    	 |   1)                    2)                             |          
    	 |   3)                    4)                             |          
    	 |   5)                    6)                             |          
    	 |   7)                    8)                             |          
    	 |                                                        |          
    # name   |   i)tems s)pells jk)change member l)leave >            |

As you have already noticed, DL gives you a guide of which letter you can type when it prompts input from you.  For example, "i)tem s)pells .." means you can type `i` or `s`.

Have you created six characters?  Then, you should go to Castle > Hawthorne Tavern to form a party.  Type `l` to leave the Training Grounds and then type `c` to go to Castle.


<a id="org5ec3712"></a>

## Castle

    | * *** Castle ***                                     |            
    |   h)awthorne tavern                                  |            
    |   t)rader jay's                                      |            
    |   i)lakehouse inn                                    |            
    |   m)oss general hospital                             |            
    |   e)dge of town                                      |            
    |   Command? >                                         |

From the Castle menu, you can visit several places, but you want to go to Hawthorne Tavern now so type `h`.


<a id="org168e246"></a>

### Hawthorne Tavern

    | * *** The Hawthorne Tavern ***                             |        
    |   Command? - a)dd r)emove i)nspect d)ivvy gold l)eave >    |

At the Tavern, you can add, remove or inspect characters.  Also, you can equally devide gold among party members.  As you want to form a party, type `a` to add members to the party.

    | * | Add who to the party?                |                 |        
    |   |  - j)down k)up x)choose l)eave       |gold l)eave > a  |        
    |   | > 1 ab               Lv  1 DWA-G-FIG |                 |        
    |   |   2 ben              Lv  1 HUM-G-FIG |                 |        
    |   |   3 cam              Lv  1 DWA-G-FIG |                 |        
    |   |   4 dia              Lv  1 HOB-N-THI |                 |        
    |   |   5 emily            Lv  1 GNO-G-PRI |                 |        
    |   |   6 faun             Lv  1 ELF-G-MAG |                 |

You can just type `x` for six times to add these members to the party.
Now, they are shown in the party window at the bottom left of the screen.

    # name       class  ac   hp status                                           
    1 ab         G-FIG  10   13 OK                                               
    2 ben        G-FIG  10   12 OK                                               
    3 cam        G-FIG  10   10 OK                                               
    4 dia        N-THI  10    7 OK                                               
    5 emily      G-PRI  10   13 OK                                               
    6 faun       G-MAG  10    7 OK

Before heading straight to the dungeon, we need to purchase weapons and armors, and equip them.  So, let's go to Castle > Trader Jay's for some shopping.


<a id="orgfc705c2"></a>

### Trader Jay's

Each character is given between 100 and 200 gold upon creation.  You can expect a party with six members would have roughly 900 gold in total.

At Trader Jay's, you'll be asked who in the party to enter the store.  Specify the number of a member in the party.  You can buy, sell, uncurse, identify items.  You can also pool gold here.  Choose `b` for shopping.

    | * *** Trader Jay's ***                               |            
    |   Who? - # or l)eave > 1                             |            
    | * Welcome, ab.                                       |            
    | *   You have 102 gold.                               |            
    |   b)uy s)ell u)ncurse i)dentify p)ool gold l)eave >  |            

Another window opens for items they sell.  This is the weapon list page.  Use `j, k` keys to move the cursor (`>`).  Let's type `x` and buy long swords for fighters.

    daemon lord - dl - [trader_jays] floor:?? (???/???)                          
    	   | ab has 102 gold                          |                      
    	   |   jk)cursor x)choose hl)page ;)leave     |                      
    	   | > 1 long sword                   25 $    |                      
    	 | |   2 sling                       150      |         |            
    	 | |   3 mage's bow                 1200      |         |            
    	 | |   4 bow                        1500      |         |            
    	 | |   5 holy bow                   8000#     |         |            
    	 | |   6 short sword                  15 $    |         |            
    	 | |   7 short sword +1            15000      |         |            
    	 | |   8 mace                         30 $    |         |            
    	 | |   9 anointed flail              150      |         |            
    	 | |  10 wand                         10 $    |)eave >  |

To change item categories, use `h, l` keys.  Below is the armor list page.  Let's buy a chain mail.

    daemon lord - dl - [trader_jays] floor:?? (???/???)                          
    	   | Sorry, you can't afford it.              |                      
    	   | Will someone else pay? (y/n)>            |                      
    	   |   1 robe                         15 $    |                      
    	 | |   2 leather armor                50 $    |         |            
    	 | |   3 leather +1                 1500      |         |            
    	 | | > 4 chain mail                   90      |         |            
    	 | |   5 chain +1                   1500      |         |            
    	 | |   6 breast plate                200      |         |            
    	 | |   7 breast +1                  1500      |         |            
    	 | |   8 plate mail                  750      |         |            
    	 | |   9 plate +1                   1500      |         | 

Oops, he doesn't have the money.  But, no worries, you can pay as the party.  Type `y`.  This way, you don't have to pool gold to the current shopper anymore.

Tip: Recommended shopping list:

-   fighters - long sword, chain mail, large shield
-   thief - sling
-   priest - sling (if you can still afford it)
-   mage - (nothing)

sling is a long-range weapon that everyone can use.  You can't expect much from sling and its damage is at best 1 or 2, but better than nothing.


<a id="orgf5d5d69"></a>

### Equip

You can equip items at Hawthorne Tavern or while camping in the dungeon.  Let's go to Hawthorne Tavern.

At Hatthorne Tavern, choose `i)nspect` > `i)tems` > item number > `e)quip` .

    daemon lord - dl - [hawthorne_tavern] floor:?? (???/???)                     
    
           |   ab| * which item?  # or l)leave            |             |        
           |     |   2) chain mail                        |             |        
           |   st|   u)se e)quip t)rade d)rop l)eave >    | 1           |        
           |     |                                        | 0           |        
           |     |                                        |10           |        
           |   vi|                                        |             |        
           |    a|                                        |             |        
           |     |                                        |             |        
           |                                                            |        
           |   mage  0/0/0/0/0/0/0   priest  0/0/0/0/0/0/0/             |  
           |   1) *long sword        2)  chain mail                     |        
           |   3)  large shield      4)                                 |        
           |   5)                    6)                                 |        
           |   7)                    8)                                 |

Equipped items will have `*` mark next to the item name.  You need to equip one item at a time and for each member.  To change members, type `j, k` .


<a id="org7188287"></a>

## Save and Resume

To save and quit the game, go to Edge of Town and type `S` (capital-S).

    | * *** Edge of Town ***                               |            
    |   m)aze                                              |            
    |   t)raining grounds                                  |            
    |   c)astle                                            |            
    |   S)ave and quit game                                | 
    |   R)esume from saved data                            |            
    |   Command?  > S                                      |            
    | * Thank you for playing.                             |            
    | * See you soon.                                      | 

You need to run `python dl.py` again to restart and resume the game.  After restarting the game, go to Edge of Town and choose `R)esume from saved data` .  That is, capital-R.  Automatic resume is not supported.


<a id="org84f234d"></a>

## Dungeon

Now, you are ready for the Dungeon.  At Edge of Town, choose `m)aze` and voila!

     daemon lord - dl - [maze] floor:?? (???/???) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^...^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^.@.^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^...^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
     # name       class  ac   hp status       ^                                  ^
     1 ab         G-FIG   4   13 OK           ^                                  ^
     2 ben        G-FIG   4   12 OK           ^                                  ^
     3 cam        G-FIG   4   10 OK           ^                                  ^
     4 dia        N-THI  10    7 OK           ^                                  ^
     5 emily      G-PRI  10   13 OK           ^                                  ^
     6 faun       G-MAG  10    7 OK           ^                                  ^

Congratulations!
You (`@`) are now in the dungeon and on the upstairs to the outside world.
`^` indicates areas that you have not visited yet.  `.` is a floor tile that you can walk on.  


<a id="orgc6534b3"></a>

### Walk around the Dungeon

The dungeon is a little dark and only 3x3 tiles around you are visible.  Let's move around a little with `h, j, k, l` keys.

     daemon lord - dl - [maze] floor:?? (???/???) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^###+###^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#....@#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#..<..#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^###+###^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can now see inside a 5x4 room.  `<` is upstairs.  `#` is a stone wall or a rock.  `+` is a door.  Let's move next to a door and type `o` for open > and direction, in this case, `k` - north.

    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^###.###^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#..@..#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#..<..#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^###+###^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
     # name       class  ac   hp status       ^* north                           ^
     1 ab         G-FIG   4   13 OK           ^* north                           ^
     2 ben        G-FIG   4   12 OK           ^* north                           ^
     3 cam        G-FIG   4   10 OK           ^* west                            ^
     4 dia        N-THI  10    7 OK           ^* west                            ^
     5 emily      G-PRI  10   13 OK           ^  Which direction? - ;)leave > k  ^
     6 faun       G-MAG  10    7 OK           ^* Opened.                         ^

Oops, another door.  Let's open again.

    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#+#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^###@###^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#..<..#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^###+###^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


<a id="orgd287008"></a>

### Battle

Continue to walk around &#x2026; and, !?  See `*** encounter ***` in the message window at the bottom right?

    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#####+#####^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.........#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.........#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.........#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#....@....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.........#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.........#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^###.#######^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^###.###^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#..<..#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
     # name       class  ac   hp status       ^* east                            ^
     1 ab         G-FIG   4   13 OK           ^* east                            ^
     2 ben        G-FIG   4   12 OK           ^* north                           ^
     3 cam        G-FIG   4   10 OK           ^* west                            ^
     4 dia        N-THI  10    7 OK           ^* west                            ^
     5 emily      G-PRI  10   13 OK           ^* west                            ^
     6 faun       G-MAG  10    7 OK           ^* *** encounter ***               ^

You encountered a group of blue slimes!  Two new windows will open for a battle.  The upper one is the monster list window.  The lower one is the battle message window.

     daemon lord - dl - [battle] floor:?? (???/???) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^|   1) 3 blue slimes              (3)                  |^^^^^^^^^^^^^
    ^^^^^^^^^|                                                      |^^^^^^^^^^^^^
    ^^^^^^^^^|                                                      |^^^^^^^^^^^^^
    ^^^^^^^^^|                                                      |^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.........#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^| * You encountered slimes.                            |^^^^^^^^^^^^^
    ^^^^^^^^^| * Options - f)ight s)pell                            |^^^^^^^^^^^^^
    ^^^^^^^^^|   u)se p)arry r)un t)ake back                        |^^^^^^^^^^^^^
    ^^^^^^^^^|   ab's action? > k                                   |^^^^^^^^^^^^^
    ^^^^^^^^^|   ab's action? > f                                   |^^^^^^^^^^^^^
    ^^^^^^^^^|   ben's action? > f                                  |^^^^^^^^^^^^^
    ^^^^^^^^^|   cam's action? > f                                  |^^^^^^^^^^^^^
    ^^^^^^^^^|   dia's action? > f                                  |^^^^^^^^^^^^^
    ^^^^^^^^^|   emily's action? > f                                |^^^^^^^^^^^^^
    ^^^^^^^^^|   faun's action? > s                                 |^^^^^^^^^^^^^
    ^^^^^^^^^| * What spell to cast?                                |^^^^^^^^^^^^^
    ^^^^^^^^^| > shunmin                                            |^^^^^^^^^^^^^
    ^^^^^^^^^| * Press any key or t)ake back >                      |^^^^^^^^^^^^^

Five members will fight and Faun the mage will cast "shunmin" (spring sleep) spell, which forces a group of enemies into asleep.

     daemon lord - dl - [battle] floor:?? (???/???) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^|   1) 2 blue slimes              (1)                  |^^^^^^^^^^^^^
    ^^^^^^^^^|                                                      |^^^^^^^^^^^^^
    ^^^^^^^^^|                                                      |^^^^^^^^^^^^^
    ^^^^^^^^^|                                                      |^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.........#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^| * Press any key or t)ake back >                      |^^^^^^^^^^^^^
    ^^^^^^^^^| * dia swings violently at blue slime and hits 1      |^^^^^^^^^^^^^
    ^^^^^^^^^|   times for 2 damage.                                |^^^^^^^^^^^^^
    ^^^^^^^^^| * faun casted shunmin.                               |^^^^^^^^^^^^^
    ^^^^^^^^^|   blue slime is not slept.                           |^^^^^^^^^^^^^
    ^^^^^^^^^|   blue slime is not slept.                           |^^^^^^^^^^^^^
    ^^^^^^^^^|   blue slime is slept.                               |^^^^^^^^^^^^^
    ^^^^^^^^^| * cam thrusts violently at blue slime and hits 1     |^^^^^^^^^^^^^
    ^^^^^^^^^|   times for 1 damage.                                |^^^^^^^^^^^^^
    ^^^^^^^^^|   blue slime is killed.                              |^^^^^^^^^^^^^

Everybody is fighting.  Umm, "shunmin" put only one out of three slimes to sleep.  shunmin is more effective against animal or human type monsters.

Cam killed one of them.  Notice `1) 2 blue slimes    (1)` ?  Because 1 out of 2 is asleep.

    ^^^^^^^^^|   times for 1 damage.                                |^^^^^^^^^^^^^
    ^^^^^^^^^|   blue slime is killed.                              |^^^^^^^^^^^^^
    ^^^^^^^^^| * ben slashes violently at blue slime and hits 1     |^^^^^^^^^^^^^
    ^^^^^^^^^|   times for 6 damage.                                |^^^^^^^^^^^^^
    ^^^^^^^^^|   blue slime is killed.                              |^^^^^^^^^^^^^
    ^^^^^^^^^| * emily swings violently at blue slime and hits 1    |^^^^^^^^^^^^^
    ^^^^^^^^^|   times for 2 damage.                                |^^^^^^^^^^^^^
    ^^^^^^^^^| * ab slashes violently at blue slime and hits 1      |^^^^^^^^^^^^^
    ^^^^^^^^^|   times for 6 damage.                                |^^^^^^^^^^^^^
    ^^^^^^^^^|   blue slime is killed.                              |^^^^^^^^^^^^^

The party killed all three slimes.

     daemon lord - dl - [maze] floor:?? (???/???) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#####+#####^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.........#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.........#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.........#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.........#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#......@..#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.........#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^###.#######^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^###.###^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#..<..#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^###+###^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
     # name       class  ac   hp status       ^* south                           ^
     1 ab         G-FIG   4   13 OK           ^* east                            ^
     2 ben        G-FIG   4   12 OK           ^* east                            ^
     3 cam        G-FIG   4   10 OK           ^* east                            ^
     4 dia        N-THI  10    7 OK           ^* *** encounter ***               ^
     5 emily      G-PRI  10   13 OK           ^  Each survivor gets 27 e.p.      ^
     6 faun       G-MAG  10    7 OK           ^  Each survivor gets 9 gold.      ^

Yeah!  Each survivor received 27 experience points and 9 gold from this battle.


<a id="org1f71867"></a>

### Friendly monsters

Sometimes, you encounter a friendly monster party.  You can choose either leave (`y`) or fight anyway (`n`).  In DL, random alignment reversal is not implemented so you can freely walk away or fight without any penalties.

    ^^^^^^^^^|   1) 5 orcs                     (5)                  |^^^^^^^^^^^^^
    ^^^^^^^^^|                                                      |^^^^^^^^^^^^^
    ^^^^^^^^^|                                                      |^^^^^^^^^^^^^
    ^^^^^^^^^|                                                      |^^^^^^^^^^^^^
    ^^^^^^^^^^^^#.....#^^^^#....#^^^^^########^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^| * You encountered friendly orcs.                     |^^^^^^^^^^^^^
    ^^^^^^^^^|   Leave? (y/n) >                                     |^^^^^^^^^^^^^

Of course, you will get no e.p. or gold if you chose to walk away.

    4 dia        N-THI  10    7 OK           ^* *** encounter ***               ^
    5 emily      G-PRI  10   13 OK           ^  Each survivor gets 0 e.p.       ^
    6 faun       G-MAG  10    7 OK           ^  Each survivor gets 0 gold.      ^


<a id="orgb7dc2b4"></a>

### Get ouf of the Dungeon

     daemon lord - dl - [maze] floor:?? (???/???) #####.#^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.........#.......#^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.........#......+#######^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.........#......#,.....#^^^^^^^^^^#########
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^###.#########.####......#^^^^^^^^^^#........
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^###.###^^#.......#......#^^^^^^^^^^#........
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^#.......#......#^^^^^^^^^^#........
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^#.........++.###^^^^^^^^^^#........
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#..@..#^^#.......####.#^^^^^^^^###########.#
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^#.......#^^#.#^^^^^^^^#...###,....#
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^###.###^^#########^^#.#^^^^^^^^#............
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.#^^^^^^^^^^^^^^^#.#^^^^^^^^#...###.....#
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^###.###^^^^^^^^^^^^^#.#^^^^^^^^#...#^#######
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^######^^^#.#^^^^^^#####.#####^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^#....#^^^#.#^^^^^^#....,....#^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....#^^^^#....#####.########.........#^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#.....######....+.+.+.+......+.........#####
     # name       class  ac   hp status       .* north                           .
     1 ab         G-FIG   4   13 OK           #* north                           #
     2 ben        G-FIG   4    7 OK           ^* east                            ^
     3 cam        G-FIG   4    5 OK           ^* east                            ^
     4 dia        N-THI  10    7 OK           ^* north                           ^
     5 emily      G-PRI  10   13 OK           ^* north                           ^
     6 faun       G-MAG  10    7 OK           ^  Exit from dungeon? (y/n) >      ^

Walked around a lot on this floor, and now mage's MP is exhausted and some are injured.  Let's get back to the outside world.  `<` is the upstairs to outside.

    daemon lord - dl - [edge_of_town] floor:?? (???/???)                         
    
    
    
    	 | * *** Edge of Town ***                               |            
    	 |   m)aze                                              |            
    	 |   t)raining grounds                                  |            
    	 |   c)astle                                            |            
    	 |   S)ave and quit game                                |            
    	 |   R)esume from saved data                            |            
    	 |   Command?  >                                        |            
    	 |                                                      |            
    	 |                                                      |            
    	 |                                                      |            
    
    
    
    # name       class  ac   hp status        * east                             
    1 ab         G-FIG   4   13 OK            * north                            
    2 ben        G-FIG   4    7 OK            * north                            
    3 cam        G-FIG   4    5 OK            * south                            
    4 dia        N-THI  10    7 OK            * west                             
    5 emily      G-PRI  10   13 OK            * west                             
    6 faun       G-MAG  10    7 OK              Exit from dungeon? (y/n) > y     

The party is back at Edge of Town.  They are safe again!


<a id="org4dc5981"></a>

### A new dungeon!

&#x2026; but wait, you should have healed injuries before geting out!  No worries.  You can go back to the dungeon with `m)aze` again.

     daemon lord - dl - [maze] floor:?? (???/???) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^...^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^.@.^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^...^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
     # name       class  ac   hp status       ^* east                            ^
     1 ab         G-FIG   4   13 OK           ^* north                           ^
     2 ben        G-FIG   4    7 OK           ^* north                           ^
     3 cam        G-FIG   4    5 OK           ^* south                           ^
     4 dia        N-THI  10    7 OK           ^* west                            ^
     5 emily      G-PRI  10   13 OK           ^* west                            ^
     6 faun       G-MAG  10    7 OK           ^  Exit from dungeon? (y/n) > y    ^

What?  We can only see 3x3 tiles around the party.  Where has the map data gone?  Actually, they are in a different dungeon map.  Dungeon map was regenerated when the party came to the dungeon again.  Let's walk around a little.

     daemon lord - dl - [maze] floor:?? (???/???) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^##+###^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#....+^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^##+.##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^...@#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^..<.#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^....#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#####^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See the map is different this time?


<a id="org37a835d"></a>

### Camp

Anyway, type `c` key for camping.  The camp menu opens.

     daemon lord - dl - [camp] floor:?? (???/???) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^| * *** Camp ***                                             |^^^^^^
    ^^^^^^^^^^|   i)nspect                                                 |^^^^^^
    ^^^^^^^^^^|   r)eorder party                                           |^^^^^^
    ^^^^^^^^^^|   S)ave and quit game                                      |^^^^^^
    ^^^^^^^^^^|   l)eave                                                   |^^^^^^
    ^^^^^^^^^^|   Command? >                                               |^^^^^^
    ^^^^^^^^^^|                                                            |^^^^^^

At camp, you can `i)nspect` characters, `r)eorder party` or `S)ave and quit game` .  Let's try `i)nspect` .

     daemon lord - dl - [camp] floor:?? (???/???) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^|   ab               L  1 g-fig dwarf                        |^^^^^^
    ^^^^^^^^^^|                                                            |^^^^^^
    ^^^^^^^^^^|   strength 18  gold               21   lvl     1           |^^^^^^
    ^^^^^^^^^^|       i.q.  7  e.p.              183   rip     0           |^^^^^^
    ^^^^^^^^^^|      piety 10  next             1000   a.c.    4           |^^^^^^
    ^^^^^^^^^^|   vitality 13  marks               2                       |^^^^^^
    ^^^^^^^^^^|    agility 11  h.p.       13/     13                       |^^^^^^
    ^^^^^^^^^^|       luck  8  status OK                                   |^^^^^^
    ^^^^^^^^^^|                                                            |^^^^^^
    ^^^^^^^^^^|   mage  0/0/0/0/0/0/0   priest  0/0/0/0/0/0/0/             |^^^^^^
    ^^^^^^^^^^|   1) *long sword        2) *chain mail                     |^^^^^^
    ^^^^^^^^^^|   3) *large shield      4)                                 |^^^^^^
    ^^^^^^^^^^|   5)                    6)                                 |^^^^^^
    ^^^^^^^^^^|   7)                    8)                                 |^^^^^^
    ^^^^^^^^^^|                                                            |^^^^^^
    ^^^^^^^^^^|   i)tems s)pells jk)change member l)leave >                |^^^^^^
     # name   |                                                            |     ^
     1 ab         G-FIG   4   13 OK           ^* south                           ^
     2 ben        G-FIG   4    7 OK           ^* *** encounter ***               ^
     3 cam        G-FIG   4    5 OK           ^  Each survivor gets 0 e.p.       ^
     4 dia        N-THI  10    7 OK           ^  Each survivor gets 0 gold.      ^
     5 emily      G-PRI  10   13 OK           ^* south                           ^
     6 faun       G-MAG  10    7 OK           ^* south                           ^

It shows the info of the front member Ab.  You can change member shown with `j, k` keys.

    ^^^^^^^^^^|   emily            L  1 g-pri gnome                        |^^^^^^
    ^^^^^^^^^^|                                                            |^^^^^^
    ^^^^^^^^^^|   strength  7  gold               21   lvl     1           |^^^^^^
    ^^^^^^^^^^|       i.q.  7  e.p.              183   rip     0           |^^^^^^
    ^^^^^^^^^^|      piety 18  next             1050   a.c.   10           |^^^^^^
    ^^^^^^^^^^|   vitality 13  marks               0                       |^^^^^^
    ^^^^^^^^^^|    agility 14  h.p.       13/     13                       |^^^^^^
    ^^^^^^^^^^|       luck  7  status OK                                   |^^^^^^
    ^^^^^^^^^^|                                                            |^^^^^^
    ^^^^^^^^^^|   mage  0/0/0/0/0/0/0   priest  2/0/0/0/0/0/0/             |^^^^^^
    ^^^^^^^^^^|   1) *sling             2)                                 |^^^^^^
    ^^^^^^^^^^|   3)                    4)                                 |^^^^^^
    ^^^^^^^^^^|   5)                    6)                                 |^^^^^^
    ^^^^^^^^^^|   7)                    8)                                 |^^^^^^
    ^^^^^^^^^^|                                                            |^^^^^^
    ^^^^^^^^^^|   i)tems s)pells jk)change member l)leave >                |^^^^^^

Emily is a priest and can cast healing spells.  Type `s)pell` > `c)ast spell` and type "jiai" which heals HP of a member.

    ^^^^^^^^^^|   emily            L  1 g-pri gnome                        |^^^^^^
    ^^^^^^^^^^|                                                            |^^^^^^
    ^^^^^^^^^^|   strength  7  gold               21   lvl     1           |^^^^^^
    ^^^^^^^^^^|   | * Spell memu:                          |   0           |^^^^^^
    ^^^^^^^^^^|   |   c)ast spell v)iew list l)eave > c    |  10           |^^^^^^
    ^^^^^^^^^^|   | * What spell to cast?                  |               |^^^^^^
    ^^^^^^^^^^|   | > jiai                                 |               |^^^^^^
    ^^^^^^^^^^|   |   Who? - # or l)eave > 2               |               |^^^^^^
    ^^^^^^^^^^|   |   emily started casting jiai           |               |^^^^^^
    ^^^^^^^^^^|   |   ben's HP was fully restored.         |0/             |^^^^^^
    ^^^^^^^^^^|   | * Spell memu:                          |               |^^^^^^
    ^^^^^^^^^^|   |   c)ast spell v)iew list l)eave >      |               |^^^^^^

Looks like, Ben's HP is fully restored.  Do that again for Cam.

    ^^^^^^^^^^|   |   ben's HP was fully restored.         |               |^^^^^^
    ^^^^^^^^^^|   | * Spell memu:                          |               |^^^^^^
    ^^^^^^^^^^|   |   c)ast spell v)iew list l)eave > c    |               |^^^^^^
    ^^^^^^^^^^|   | * What spell to cast?                  |               |^^^^^^
    ^^^^^^^^^^|   | > jiai                                 |0/             |^^^^^^
    ^^^^^^^^^^|   |   Who? - # or l)eave > 3               |               |^^^^^^
    ^^^^^^^^^^|   |   emily started casting jiai           |               |^^^^^^
    ^^^^^^^^^^|   |   cam's HP was fully restored.         |               |^^^^^^

Great!

Let's exit from dungeon and head to Edge of Town > Castle > the Lakehouse Inn.


<a id="org7e74f1b"></a>

## Castle


<a id="org55a40d4"></a>

### The Lakehouse Inn

    | * *** Castle ***                                     |            
    |   h)awthorne tavern                                  |            
    |   t)rader jay's                                      |            
    |   i)lakehouse inn                                    |            
    |   m)oss general hospital                             |            
    |   e)dge of town                                      |            
    |   Command? >                                         |            

Back at Castle, type `i` for Lakehouse Inn.

    | * *** The Lakehouse Inn ***                          |            
    |   Welcome.  You must be very tired.                  |            
    |   You have 232 gold in total.                        |            
    |   c)ots                  12 gold                     |            
    |   s)tandard rooms       120 gold                     |            
    |   d)elux rooms          300 gold                     |            
    |   v)lake view suites   1200 gold                     |            
    |   p)residential suites 3000 gold                     |            
    |   or l)eave                                          |            
    |   Which rooms to stay today? >                       |            

Delux room sounds good, but as we have only 232 gold, let's choose `c)ots` tonight.

    |   Which rooms to stay today? > c                     |            
    | * Today's dinner is cabbage soup.                    |            
    | * ab went to bed...                                  |            
    | * ben went to bed...                                 |            
    | * cam went to bed...                                 |            
    | * dia went to bed...                                 |            
    | * emily went to bed...                               |            
    | * faun went to bed...                                |            

If their e.p. reach the next level, their level will go up while they are asleep at the inn.

In DL, age doesn't matter.  They can stay at the inn as long as they wish without getting old.  All the party members stay at the same room type.

Magic points are fully restored rgardless of the room they choose.  HPs being restored depend on the room they stay.  More comfortable (and thus expensive) rooms will heal them better.  Dinner is better in those rooms as well.

