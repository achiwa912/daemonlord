
# Table of Contents

1.  [dl.py - Daemon Lord](#org06b04c6)
    1.  [Overview](#org542916a)
        1.  [Wizardry clone](#org4345ce2)
        2.  [Rogue-like dungeon maps](#orgd17d1a5)
        3.  [A little more friendly than the original](#org6d19ecf)
    2.  [Important notice: Under development](#org3034fcd)
2.  [Installation](#orgdd9aacf)
3.  [Prerequisites](#org7cf2bca)
4.  [How to Play](#org6bca894)
5.  [License](#orgc7d4159)
6.  [Quick Tour of Daemon Lord](#org48b3b7c)
    1.  [Game start](#orgcd5c9eb)
    2.  [Edge of Town](#orgefce5b1)
        1.  [Training Grounds](#orge6954c6)
    3.  [Castle](#org66d134b)
        1.  [Hawthorne Tavern](#org1af445f)
        2.  [Trader Jay's](#orgb33dd7b)
        3.  [Equip](#orge1efb02)
    4.  [Save and Resume](#org264924e)
    5.  [Dungeon](#org0095314)
        1.  [Walk around the Dungeon](#orgde09f9e)
        2.  [Battle](#org85513f6)
        3.  [Chest](#orgcda3629)
        4.  [Friendly monsters](#orgc151371)
        5.  [Get ouf of the Dungeon](#orgebfbac6)
        6.  [A new dungeon!](#orgd02917f)
        7.  [Camp](#org89105df)
        8.  [Save and Resume from camp](#orgba51673)
    6.  [Castle](#orgd663207)
        1.  [The Lakehouse Inn](#org4fd4c68)
7.  [Spells](#org5e5f821)
    1.  [Overview](#org395b65d)
    2.  [Usage](#org3370c8c)
    3.  [Mage Spells](#orgc8690d7)
    4.  [Priest Spells](#org3141394)



<a id="org06b04c6"></a>

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


<a id="org542916a"></a>

## Overview


<a id="org4345ce2"></a>

### Wizardry clone

-   Based on Wizardry I; Proving Grounds of the Mad Overlord
-   Party of up to six members
-   Battles with monster parties in the dungeon
-   Gain experience points and level up
-   Get gold and powerful items from trap-protected chests
-   Roughly 50 magic spells, 100 items and 100 monsters (for now)
-   Need to type spells and chest traps accurately


<a id="orgd17d1a5"></a>

### Rogue-like dungeon maps

-   Text-based, 2D dungeon maps
-   10 (or more) layers deep
-   Maps are auto-generated.  Every time you go down the dungeon, you will see different maps


<a id="org6d19ecf"></a>

### A little more friendly than the original

-   Re-calculate the bonus value with `.` key when creating a character
-   Age doesn't matter anymore
-   "tsubasa" spell (mage level 2) will take your party to known depth
-   Save and resume anywhere in the dungeon, preserving floor maps and spells in effect such as identification of monsters or protection
-   HP decrease by poison stops at HP = 1
-   You don't have to pool gold anymore.  Someone in the party will pay for you
-   Group heal spells for the entire party


<a id="org3034fcd"></a>

## Important notice: Under development

Currently, DL (daemon lord) is under development and has tons of bugs and not-yet-implemented features.  It is below alpha quality and not playable yet as of April 6th, 2021.  Please note that your saved file might become obsolete and be invalidated.  Backward compatibility is not supported.  Anything might change anytime.

Please send bug reports to achiwa912+gmail.com (replace '+' with '@').

To-be-implemented features:

-   Change classes
-   Game clear
-   Rescue defeated party members in the dungeon
-   Monsters and items on floor 11 or deeper
-   Background story


<a id="orgdd9aacf"></a>

# Installation

1.  Setup python 3.8 or later
2.  Place dl.py, monsters.csv, spells.csv, items.csv in the same directory
3.  Run "python dl.py"


<a id="org7cf2bca"></a>

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


<a id="org6bca894"></a>

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


<a id="orgc7d4159"></a>

# License

Daemon Lord is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
Daemon Lord - Copyright (C) 2021 Kyosuke Achiwa


<a id="org48b3b7c"></a>

# Quick Tour of Daemon Lord


<a id="orgcd5c9eb"></a>

## Game start

DL (Daemon Lord) starts with the screen below at the Castle.

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


<a id="orgefce5b1"></a>

## Edge of Town


<a id="orge6954c6"></a>

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

Here's base attribute table:

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-right" />

<col  class="org-right" />

<col  class="org-right" />

<col  class="org-right" />

<col  class="org-right" />

<col  class="org-right" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">race</th>
<th scope="col" class="org-right">str</th>
<th scope="col" class="org-right">i.q.</th>
<th scope="col" class="org-right">pie</th>
<th scope="col" class="org-right">vit</th>
<th scope="col" class="org-right">agi</th>
<th scope="col" class="org-right">luk</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">human</td>
<td class="org-right">8</td>
<td class="org-right">8</td>
<td class="org-right">5</td>
<td class="org-right">8</td>
<td class="org-right">8</td>
<td class="org-right">9</td>
</tr>


<tr>
<td class="org-left">elf</td>
<td class="org-right">7</td>
<td class="org-right">10</td>
<td class="org-right">10</td>
<td class="org-right">6</td>
<td class="org-right">9</td>
<td class="org-right">6</td>
</tr>


<tr>
<td class="org-left">dwarf</td>
<td class="org-right">10</td>
<td class="org-right">7</td>
<td class="org-right">10</td>
<td class="org-right">10</td>
<td class="org-right">5</td>
<td class="org-right">6</td>
</tr>


<tr>
<td class="org-left">gnome</td>
<td class="org-right">7</td>
<td class="org-right">7</td>
<td class="org-right">10</td>
<td class="org-right">8</td>
<td class="org-right">10</td>
<td class="org-right">7</td>
</tr>


<tr>
<td class="org-left">hobbit</td>
<td class="org-right">5</td>
<td class="org-right">7</td>
<td class="org-right">7</td>
<td class="org-right">6</td>
<td class="org-right">10</td>
<td class="org-right">15</td>
</tr>
</tbody>
</table>

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

Class requirement table:

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-right" />

<col  class="org-right" />

<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">class</th>
<th scope="col" class="org-left">str</th>
<th scope="col" class="org-right">i.q.</th>
<th scope="col" class="org-right">pie</th>
<th scope="col" class="org-left">vit</th>
<th scope="col" class="org-left">agi</th>
<th scope="col" class="org-left">luk</th>
<th scope="col" class="org-left">good</th>
<th scope="col" class="org-left">neutral</th>
<th scope="col" class="org-left">evil</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">fighter</td>
<td class="org-left">11</td>
<td class="org-right">-</td>
<td class="org-right">-</td>
<td class="org-left">-</td>
<td class="org-left">-</td>
<td class="org-left">-</td>
<td class="org-left">ok</td>
<td class="org-left">ok</td>
<td class="org-left">ok</td>
</tr>


<tr>
<td class="org-left">mage</td>
<td class="org-left">-</td>
<td class="org-right">11</td>
<td class="org-right">-</td>
<td class="org-left">-</td>
<td class="org-left">-</td>
<td class="org-left">-</td>
<td class="org-left">ok</td>
<td class="org-left">ok</td>
<td class="org-left">ok</td>
</tr>


<tr>
<td class="org-left">priest</td>
<td class="org-left">-</td>
<td class="org-right">-</td>
<td class="org-right">11</td>
<td class="org-left">-</td>
<td class="org-left">-</td>
<td class="org-left">-</td>
<td class="org-left">ok</td>
<td class="org-left">-</td>
<td class="org-left">ok</td>
</tr>


<tr>
<td class="org-left">thief</td>
<td class="org-left">-</td>
<td class="org-right">-</td>
<td class="org-right">-</td>
<td class="org-left">-</td>
<td class="org-left">11</td>
<td class="org-left">-</td>
<td class="org-left">-</td>
<td class="org-left">ok</td>
<td class="org-left">ok</td>
</tr>


<tr>
<td class="org-left">bishop</td>
<td class="org-left">-</td>
<td class="org-right">12</td>
<td class="org-right">12</td>
<td class="org-left">-</td>
<td class="org-left">-</td>
<td class="org-left">-</td>
<td class="org-left">ok</td>
<td class="org-left">-</td>
<td class="org-left">ok</td>
</tr>


<tr>
<td class="org-left">samurai</td>
<td class="org-left">15</td>
<td class="org-right">11</td>
<td class="org-right">10</td>
<td class="org-left">14</td>
<td class="org-left">10</td>
<td class="org-left">-</td>
<td class="org-left">ok</td>
<td class="org-left">ok</td>
<td class="org-left">-</td>
</tr>


<tr>
<td class="org-left">ninja</td>
<td class="org-left">17</td>
<td class="org-right">17</td>
<td class="org-right">17</td>
<td class="org-left">17</td>
<td class="org-left">17</td>
<td class="org-left">17</td>
<td class="org-left">-</td>
<td class="org-left">-</td>
<td class="org-left">ok</td>
</tr>


<tr>
<td class="org-left">lord</td>
<td class="org-left">15</td>
<td class="org-right">12</td>
<td class="org-right">12</td>
<td class="org-left">15</td>
<td class="org-left">14</td>
<td class="org-left">15</td>
<td class="org-left">ok</td>
<td class="org-left">-</td>
<td class="org-left">-</td>
</tr>
</tbody>
</table>

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

Also, you can `d)elete` the character from here.  Deleted characters are lost forever and you can't undo a delete operation.

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


<a id="org66d134b"></a>

## Castle

    | * *** Castle ***                                     |            
    |   h)awthorne tavern                                  |            
    |   t)rader jay's                                      |            
    |   i)lakehouse inn                                    |            
    |   m)oss general hospital                             |            
    |   e)dge of town                                      |            
    |   Command? >                                         |

From the Castle menu, you can visit several places, but you want to go to Hawthorne Tavern now so type `h`.


<a id="org1af445f"></a>

### Hawthorne Tavern

    | * *** The Hawthorne Tavern ***                             |        
    |   Command? - a)dd r)emove i)nspect d)ivvy gold l)eave >    |

At the Tavern, you can add, remove or inspect characters.  Also, you can equally divide gold among party members.  As you want to form a party, type `a` to add members to the party.

Use `j, k` keys to choose members and `x` to add.

    | * | Add who to the party?                |                 |        
    |   |  - j)down k)up x)choose l)eave       |gold l)eave > a  |        
    |   | > 1 ab               Lv  1 DWA-G-FIG |                 |        
    |   |   2 ben              Lv  1 HUM-G-FIG |                 |        
    |   |   3 cam              Lv  1 DWA-G-FIG |                 |        
    |   |   4 dia              Lv  1 HOB-N-THI |                 |        
    |   |   5 emily            Lv  1 GNO-G-PRI |                 |        
    |   |   6 faun             Lv  1 ELF-G-MAG |                 |

Here, you can just type `x` for six times to add the six members to the party.
Now, they are shown in the party window at the bottom left of the screen.

    # name       class  ac   hp status                                           
    1 ab         G-FIG  10   13 OK                                               
    2 ben        G-FIG  10   12 OK                                               
    3 cam        G-FIG  10   10 OK                                               
    4 dia        N-THI  10    7 OK                                               
    5 emily      G-PRI  10   13 OK                                               
    6 faun       G-MAG  10    7 OK


<a id="orgb33dd7b"></a>

### Trader Jay's

Before heading straight to the dungeon, we need to purchase weapons and armors, and equip them.  So, let's go to Castle > Trader Jay's for some shopping.

Each character is given between 100 and 200 gold upon creation.  You can expect a party with six members would have roughly 900 gold in total.

At Trader Jay's, you'll be asked who in the party to enter the store.  Specify the number of a member in the party.  You can buy, sell, uncurse, identify items.  You can also pool gold here.  Choose `b)uy` for shopping.

    | * *** Trader Jay's ***                               |            
    |   Who? - # or l)eave > 1                             |            
    | * Welcome, ab.                                       |            
    | *   You have 102 gold.                               |            
    |   b)uy s)ell u)ncurse i)dentify p)ool gold l)eave >  |            

Another window opens for items they sell.  This is the weapon list page.  Use `j, k` keys to move the cursor (`>`).  Let's type `x` and buy a long sword for Ab.

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

To change item categories, use `h, l` keys.  Below is the armor list page.  Let's buy a chain mail for him.

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

Oops, he doesn't have the money.  But, no worries, you can pay as the party.  Type `y` to the question "Will someone else pay? (y/n)".  This way, you don't have to pool gold first to the current shopper anymore.

Tip: Recommended shopping list:

-   fighter - long sword, chain mail, large shield
-   thief - sling
-   priest - sling (if you can still afford it)
-   mage - (nothing)

Basically, the front (ie, the first three) members should equip heavily because monsters mostly aim at front members when physically attack.  Short-range wepons can't be used by the 4th to 6th members.

sling is a long-range weapon that everyone can use.  You can't expect much from sling and its damage is at best 1 or 2, but better than nothing.  Long-ranged weapons tend to be less powerful and more expensive than short-range ones.


<a id="orge1efb02"></a>

### Equip

You can equip items at Hawthorne Tavern or while camping in the dungeon.  Let's go to Hawthorne Tavern.

At Hatthorne Tavern, first `i)nspect` a character and then choose `i)tems` > item number > `e)quip` .

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


<a id="org264924e"></a>

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


<a id="org0095314"></a>

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


<a id="orgde09f9e"></a>

### Walk around the Dungeon

The dungeon is a little dark and only 3x3 tiles around you are visible.  Let's move around a little with `h, j, k, l` keys.  The key bindings should be familiar to those who use vi/vim and have played rogue-like games.

The party (`@`) is always shown in the center of the map scroll window.

Here's the key operations on dungeon maps

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">key</th>
<th scope="col" class="org-left">action</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">h</td>
<td class="org-left">move left (west)</td>
</tr>


<tr>
<td class="org-left">j</td>
<td class="org-left">move up (north)</td>
</tr>


<tr>
<td class="org-left">k</td>
<td class="org-left">move down (south)</td>
</tr>


<tr>
<td class="org-left">l</td>
<td class="org-left">move right (east)</td>
</tr>


<tr>
<td class="org-left">c</td>
<td class="org-left">camp menu</td>
</tr>


<tr>
<td class="org-left">o + direction</td>
<td class="org-left">(unlock and) open door</td>
</tr>


<tr>
<td class="org-left">.</td>
<td class="org-left">stay/stomp?</td>
</tr>
</tbody>
</table>

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

Here's map tile table for your convenience.

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">tile</th>
<th scope="col" class="org-left">description</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">`.`</td>
<td class="org-left">floor tile you can walk on</td>
</tr>


<tr>
<td class="org-left">`^`</td>
<td class="org-left">unknown area (not visited yet)</td>
</tr>


<tr>
<td class="org-left">`#`</td>
<td class="org-left">stone wall/rock</td>
</tr>


<tr>
<td class="org-left">`<`</td>
<td class="org-left">upstairs</td>
</tr>


<tr>
<td class="org-left">`>`</td>
<td class="org-left">downstaris</td>
</tr>


<tr>
<td class="org-left">`+`</td>
<td class="org-left">door (need to open)</td>
</tr>


<tr>
<td class="org-left">`*`</td>
<td class="org-left">locked door</td>
</tr>


<tr>
<td class="org-left">`%`</td>
<td class="org-left">locked door (need special key)</td>
</tr>


<tr>
<td class="org-left">`,`</td>
<td class="org-left">message or event</td>
</tr>
</tbody>
</table>

For locked doors (`*`), you can try to unlock until succeed.  Your party needs a thief or a ninja for that.  A low level theif might find difficult to unlock a locked door.

For special locked doors (`%`), you first need to find the key.  Hint: The key should be somewhere on the same floor.  Look for an event tile (`,`).

Note that there's no elevator/lift in the dungeon.  Use "tsubasa" spell instead.

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


<a id="org85513f6"></a>

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


<a id="orgcda3629"></a>

### Chest

Sometimes, you encounter a monster party on entering a room.  They are room guardians.

    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^####.^^^^...^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^....#^^^^.@.^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^....######.#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^..<........#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^....########^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^##+##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
     # name       class  ac   hp status       ^* north                           ^
     1 ab         G-FIG   4   13 OK           ^* *** encounter ***               ^
     2 ben        G-FIG   4   12 OK           ^                                  ^

And after you defeated room guardians, you may find a chest.

     daemon lord - dl - [maze] floor:?? (???/???) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^| * A chest!                             |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^| * o)pen k)antei i)nspect d)isarm       |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^|   l)eave alone                         |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^|   Option? >                            |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^|                                        |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^|                                        |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^|                                        |^^^^^^^^^^^^^^^^^^^^^^

Chests are usually protected with traps.  You need first to identify the trap and then disarm it before opening a chest.  And this is when a thief is quite usuful.

You have a few options.

-   `o)pen` without disarming the trap.
-   `k)antei` use "kantei" spell to identify the trap
-   `i)nspect` the trap.  It might activate the trap
-   `d)isarm` the trap.  You need to type the trap name
-   `l)eave alone` Give up the chest and walk away

    ^^^^^^^^^^^^^^| * A chest!                             |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^| * o)pen k)antei i)nspect d)isarm       |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^|   l)eave alone                         |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^|   Option? > i                          |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^|   Who? - # or l)eave > 4               |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^|   It is poison needle.                 |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^| * o)pen k)antei i)nspect d)isarm       |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^|   l)eave alone                         |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^|   Option? >                            |^^^^^^^^^^^^^^^^^^^^^^

Dia the theif identified the trap as "poison needle".  To disarm it, you need to type the trap name accurately.

    ^^^^^^^^^^^^^^| * o)pen k)antei i)nspect d)isarm       |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^|   l)eave alone                         |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^|   Option? > d                          |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^|   Who? - # or l)eave > 4               |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^| * Trap name?                           |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^| > poison needle                        |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^|   Disarmed the trap.                   |^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^| * There was no interesting item.       |^^^^^^^^^^^^^^^^^^^^^^

He disarmed the poison needle trap and opened the chest.  Unfortunately, there was nothing interesting in it this time.

Here's the trap list.

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">trap</th>
<th scope="col" class="org-left">effect</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">poison needle</td>
<td class="org-left">poision the member who tried to identify/disarm</td>
</tr>


<tr>
<td class="org-left">crossbow bolt</td>
<td class="org-left">inflict damages to a random member</td>
</tr>


<tr>
<td class="org-left">stunner</td>
<td class="org-left">paralyze the member who tried to identify/disarm</td>
</tr>


<tr>
<td class="org-left">exploding box</td>
<td class="org-left">inflict damages to entire party members</td>
</tr>


<tr>
<td class="org-left">gas bomb</td>
<td class="org-left">poison entire party members</td>
</tr>


<tr>
<td class="org-left">mage blaster</td>
<td class="org-left">paralyze members who use mage spells</td>
</tr>


<tr>
<td class="org-left">priest blaster</td>
<td class="org-left">paralyze members who use priest spells</td>
</tr>


<tr>
<td class="org-left">teleporter</td>
<td class="org-left">teleport party to random location (could be in rock)</td>
</tr>


<tr>
<td class="org-left">alarm</td>
<td class="org-left">summon nearby monsters</td>
</tr>
</tbody>
</table>


<a id="orgc151371"></a>

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


<a id="orgebfbac6"></a>

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

Having walked around a lot on this floor, and now the mage's MP is exhausted and some are injured.  Let's get back to the outside world.  `<` is the upstairs to outside.  Answer `y` to the question: "Exit from dungeon? (y/n)"

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

The party is back at Edge of Town.  It should take a while to get used to the brightness but they are safe again!


<a id="orgd02917f"></a>

### A new dungeon!

&#x2026; but wait, you should have healed injuries before geting out!  No worries.  You can go back to the dungeon with `m)aze` again.  Let's go back.

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

What?  We can only see 3x3 tiles around the party.  Where has the map data gone?  Actually, they are in a different dungeon map.  Due to some magical power, dungeon maps are regenerated every time the party comes to the dungeon.  Let's walk around a little to confirm the theory.

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


<a id="org89105df"></a>

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

At camp, you can `i)nspect` characters, `r)eorder party` or `S)ave and quit game` .  Choose `i)nspect` for spells.

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

It shows the info of the front member Ab.  You can change the member shown with `j, k` keys.

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

Emily is a priest and can cast healing spells.  Type `s)pells` > `c)ast spell` and type "jiai" which heals HP of a member.

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

Looks like, Ben's HP is fully restored.  Do the same for Cam.

    ^^^^^^^^^^|   |   ben's HP was fully restored.         |               |^^^^^^
    ^^^^^^^^^^|   | * Spell memu:                          |               |^^^^^^
    ^^^^^^^^^^|   |   c)ast spell v)iew list l)eave > c    |               |^^^^^^
    ^^^^^^^^^^|   | * What spell to cast?                  |               |^^^^^^
    ^^^^^^^^^^|   | > jiai                                 |0/             |^^^^^^
    ^^^^^^^^^^|   |   Who? - # or l)eave > 3               |               |^^^^^^
    ^^^^^^^^^^|   |   emily started casting jiai           |               |^^^^^^
    ^^^^^^^^^^|   |   cam's HP was fully restored.         |               |^^^^^^

Great!


<a id="orgba51673"></a>

### Save and Resume from camp

Now, try to save and resume in the dungeon.  From the camp menu, choose `S)ave and quit game` .

    ^^^^^^^^^^| * *** Camp ***                                             |^^^^^^
    ^^^^^^^^^^|   i)nspect                                                 |^^^^^^
    ^^^^^^^^^^|   r)eorder party                                           |^^^^^^
    ^^^^^^^^^^|   S)ave and quit game                                      |^^^^^^
    ^^^^^^^^^^|   l)eave                                                   |^^^^^^
    ^^^^^^^^^^|   Command? > S                                             |^^^^^^
    ^^^^^^^^^^| * Thank you for playing.                                   |^^^^^^
    ^^^^^^^^^^| * See you again soon.                                      |^^^^^^
    ^^^^^^^^^^|                                                            |^^^^^^

And run the python script.

    $ python dl.py

Choose `e)dge of town` > `R)esume from saved data`

    | * *** Edge of Town ***                               |            
    |   m)aze                                              |            
    |   t)raining grounds                                  |            
    |   c)astle                                            |            
    |   S)ave and quit game                                |            
    |   R)esume from saved data                            |            
    |   Command?  >                                        |        

And, you are in the dungeon again.

     daemon lord - dl - [maze] floor:?? (???/???) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
     # name       class  ac   hp status       ^                                  ^
     1 ab         G-FIG   4   13 OK           ^                                  ^
     2 ben        G-FIG   4   12 OK           ^                                  ^
     3 cam        G-FIG   4   10 OK           ^                                  ^
     4 dia        N-THI  10    7 OK           ^                                  ^
     5 emily      G-PRI  10   13 OK           ^                                  ^
     6 faun       G-MAG  10    7 OK           ^                                  ^

Let's exit from the dungeon and head to Edge of Town > Castle > Lakehouse Inn for some rest.


<a id="orgd663207"></a>

## Castle


<a id="org4fd4c68"></a>

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

Delux room sounds good, but as we have only 232 gold, let's choose `c)ots` tonight.  Maybe we can stay in standard rooms tomorrow.

    |   Which rooms to stay today? > c                     |            
    | * Today's dinner is cabbage soup.                    |            
    | * ab went to bed...                                  |            
    | * ben went to bed...                                 |            
    | * cam went to bed...                                 |            
    | * dia went to bed...                                 |            
    | * emily went to bed...                               |            
    | * faun went to bed...                                |            

Magic points are fully restored regardless of the room they choose.  HPs being restored depend on the room they stay.  More comfortable (and thus expensive) rooms will heal them better.  Dinner is better in those rooms as well.

If their e.p. reach the next level, their level will go up while they are asleep at the inn.

In DL, age doesn't matter.  They can stay at the inn as long as they wish without getting old.  All the party members stay at the same room type.


<a id="org5e5f821"></a>

# Spells


<a id="org395b65d"></a>

## Overview

As in Wizardry, spells in DL are divided into two categories: mage spells and priest spells.  Very roughly speaking, mage spells are for battles with monsters and priest spells are to heal and cure.

There are magic points (MPs) for each category and spell level.  You can check their remaining MPs in the character inspection window.

    ^^^^^^^^^^|       luck 11  status OK                                   |^^^^^^
    ^^^^^^^^^^|                                                            |^^^^^^
    ^^^^^^^^^^|   mage  2/0/0/0/0/0/0   priest  0/0/0/0/0/0/0/             |^^^^^^
    ^^^^^^^^^^|   1)                    2)                                 |^^^^^^
    ^^^^^^^^^^|   3)                    4)                                 |^^^^^^

In this example, she has 2 MPs remaining for level 1 mage spells.  She will acquire more MPs as her level goes up.

The maximum MPs for each spell level is 9.  A high level mage/priest will have `9/9/9/9/9/9/9` MPs.


<a id="org3370c8c"></a>

## Usage

Spells can be used only in the dungeon.  More specifically, during a battle or while they are camping.  The only exception is "kantei" which can be used for identifying a chest trap.

Some spells such as mage's "shunmin" or "taika" can be used only in battles.  Some other spells such as mage's "gps" or "tsubasa" are only available while they are camping.

To use spells from the camp menu, first `i)nspect` a character who would like to cast a spell.  To change characters in the inspect menu, use `j, k` keys until it shows the member to cast the spell.  Then, type `s)pells` > `c)ast spell` > enter the spell name (> choose target member).

     daemon lord - dl - [camp] floor:?? (???/???) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ^^^^^^^^^^|   faun             L  1 g-mag elf                          |^^^^^^
    ^^^^^^^^^^|                                                            |^^^^^^
    ^^^^^^^^^^|   strength  7  gold              100   lvl     1           |^^^^^^
    ^^^^^^^^^^|   | * Spell memu:                          |   0           |^^^^^^
    ^^^^^^^^^^|   |   c)ast spell v)iew list l)eave > c    |  10           |^^^^^^
    ^^^^^^^^^^|   | * What spell to cast?                  |               |^^^^^^
    ^^^^^^^^^^|   | > gps                                  |               |^^^^^^
    ^^^^^^^^^^|   |                                        |               |^^^^^^
    ^^^^^^^^^^|   |                                        |               |^^^^^^
    ^^^^^^^^^^|   |                                        |0/             |^^^^^^
    ^^^^^^^^^^|   |                                        |               |^^^^^^
    ^^^^^^^^^^|   |                                        |               |^^^^^^
    ^^^^^^^^^^|   |                                        |               |^^^^^^
    ^^^^^^^^^^|   |                                        |               |^^^^^^
    ^^^^^^^^^^|   |                                        |               |^^^^^^
    ^^^^^^^^^^|   i)tems s)pells jk)change member l)leave > s              |^^^^^^


<a id="orgc8690d7"></a>

## Mage Spells

One of the most useful spells will be newly introduced "tsubasa".  This spell can take the party to the upstairs of a known depth floor for the caster.  It can be used to get out of the dungeon (ie, choose depth=1) or to start an adventure from the deepest floor they experienced.

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-right" />

<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-right">lv</th>
<th scope="col" class="org-left">name</th>
<th scope="col" class="org-left">wiz (FYI)</th>
<th scope="col" class="org-left">description</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-right">1</td>
<td class="org-left">onibi</td>
<td class="org-left">halito</td>
<td class="org-left">Fireball to hit a monster for 1-8 damage</td>
</tr>


<tr>
<td class="org-right">1</td>
<td class="org-left">tate</td>
<td class="org-left">mogref</td>
<td class="org-left">Reduce the caster's AC by 2</td>
</tr>


<tr>
<td class="org-right">1</td>
<td class="org-left">shunmin</td>
<td class="org-left">katino</td>
<td class="org-left">Put one enemy group to asleep</td>
</tr>
</tbody>

<tbody>
<tr>
<td class="org-right">2</td>
<td class="org-left">gps</td>
<td class="org-left">(dumapic)</td>
<td class="org-left">Locate the precise position in the dungeon</td>
</tr>


<tr>
<td class="org-right">2</td>
<td class="org-left">kurayami</td>
<td class="org-left">dilto</td>
<td class="org-left">Increase AC by 2 for an enemy group</td>
</tr>


<tr>
<td class="org-right">2</td>
<td class="org-left">tomei</td>
<td class="org-left">sopic</td>
<td class="org-left">Reduce the caster's AC by 4</td>
</tr>


<tr>
<td class="org-right">2</td>
<td class="org-left">tsubasa</td>
<td class="org-left">(malor)</td>
<td class="org-left">Teleport to a known floor</td>
</tr>
</tbody>

<tbody>
<tr>
<td class="org-right">3</td>
<td class="org-left">taika</td>
<td class="org-left">mahalito</td>
<td class="org-left">Wall of fire to hit a group of enemies for 4-24 damage</td>
</tr>


<tr>
<td class="org-right">3</td>
<td class="org-left">kamaitachi</td>
<td class="org-left">molito</td>
<td class="org-left">Sharp wind to inflict 3-18 damage to an enemy group</td>
</tr>
</tbody>

<tbody>
<tr>
<td class="org-right">4</td>
<td class="org-left">kanashibari</td>
<td class="org-left">morlis</td>
<td class="org-left">Increase AC by 4 for an enemy group</td>
</tr>


<tr>
<td class="org-right">4</td>
<td class="org-left">toketsu</td>
<td class="org-left">dalto</td>
<td class="org-left">Blizzard to inflict 6-36 damage to an enemy group</td>
</tr>


<tr>
<td class="org-right">4</td>
<td class="org-left">gouka</td>
<td class="org-left">lahalito</td>
<td class="org-left">Big fire to inflict 6-36 damage to an enemy group</td>
</tr>
</tbody>

<tbody>
<tr>
<td class="org-right">5</td>
<td class="org-left">kyofu</td>
<td class="org-left">mamorlis</td>
<td class="org-left">Increase AC by 4 for all enemy groups</td>
</tr>


<tr>
<td class="org-right">5</td>
<td class="org-left">senmetsu</td>
<td class="org-left">makanito</td>
<td class="org-left">Eliminate all enemies below Lvl 8</td>
</tr>


<tr>
<td class="org-right">5</td>
<td class="org-left">zettaireido</td>
<td class="org-left">madalto</td>
<td class="org-left">Abs. zero to cause 8-64 damage to an enemy group</td>
</tr>
</tbody>

<tbody>
<tr>
<td class="org-right">6</td>
<td class="org-left">shinoroi</td>
<td class="org-left">lakanito</td>
<td class="org-left">Kill all air-breathing enemies in a group</td>
</tr>


<tr>
<td class="org-right">6</td>
<td class="org-left">butsumetsu</td>
<td class="org-left">zilwan</td>
<td class="org-left">Buddha power to inflict 10-2000 damage to an undead</td>
</tr>


<tr>
<td class="org-right">6</td>
<td class="org-left">zentomei</td>
<td class="org-left">masopic</td>
<td class="org-left">Reduce party's AC by 4</td>
</tr>
</tbody>

<tbody>
<tr>
<td class="org-right">7</td>
<td class="org-left">jigokunohonou</td>
<td class="org-left">-</td>
<td class="org-left">Inferno to inflict 20-400 damage to a single enemy</td>
</tr>


<tr>
<td class="org-right">7</td>
<td class="org-left">kakubaku</td>
<td class="org-left">tiltowait</td>
<td class="org-left">Nuclear fusion to inflict 10-150 damage to all enemies</td>
</tr>
</tbody>
</table>


<a id="org3141394"></a>

## Priest Spells

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-right" />

<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-right">lv</th>
<th scope="col" class="org-left">name</th>
<th scope="col" class="org-left">wiz (FYI)</th>
<th scope="col" class="org-left">description</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-right">1</td>
<td class="org-left">shukufuku</td>
<td class="org-left">kalki</td>
<td class="org-left">Reduce party's AC by 1</td>
</tr>


<tr>
<td class="org-right">1</td>
<td class="org-left">jiai</td>
<td class="org-left">dios</td>
<td class="org-left">Restore 1-8 HP to a single target</td>
</tr>


<tr>
<td class="org-right">1</td>
<td class="org-left">ikari</td>
<td class="org-left">badios</td>
<td class="org-left">Angry power to inflict 1-8 damage to an enemy</td>
</tr>


<tr>
<td class="org-right">1</td>
<td class="org-left">akari</td>
<td class="org-left">milwa</td>
<td class="org-left">A bright light lets you see further for a while</td>
</tr>


<tr>
<td class="org-right">1</td>
<td class="org-left">mamori</td>
<td class="org-left">porfic</td>
<td class="org-left">Reduce the caster's AC by 4</td>
</tr>
</tbody>

<tbody>
<tr>
<td class="org-right">2</td>
<td class="org-left">kabe</td>
<td class="org-left">matu</td>
<td class="org-left">Reduce party's AC by 2</td>
</tr>


<tr>
<td class="org-right">2</td>
<td class="org-left">kantei</td>
<td class="org-left">calfo</td>
<td class="org-left">Identify a trap with 95% accuracy</td>
</tr>


<tr>
<td class="org-right">2</td>
<td class="org-left">nero</td>
<td class="org-left">manifo</td>
<td class="org-left">Paralyze a group of enemies</td>
</tr>


<tr>
<td class="org-right">2</td>
<td class="org-left">damare</td>
<td class="org-left">montino</td>
<td class="org-left">Silence an enemy group</td>
</tr>
</tbody>

<tbody>
<tr>
<td class="org-right">3</td>
<td class="org-left">hikarinotama</td>
<td class="org-left">lomilwa</td>
<td class="org-left">A bright light lets you see further for a long time</td>
</tr>


<tr>
<td class="org-right">3</td>
<td class="org-left">okiro</td>
<td class="org-left">dialko</td>
<td class="org-left">Cures a paralyzed or asleep for a single target</td>
</tr>


<tr>
<td class="org-right">3</td>
<td class="org-left">shikibetsu</td>
<td class="org-left">latumapic</td>
<td class="org-left">Identify enemies</td>
</tr>


<tr>
<td class="org-right">3</td>
<td class="org-left">kaminohogo</td>
<td class="org-left">bamatu</td>
<td class="org-left">Reduce party's AC by 4</td>
</tr>


<tr>
<td class="org-right">3</td>
<td class="org-left">iyashi</td>
<td class="org-left">dial</td>
<td class="org-left">Restore 4-16 HP to a single target</td>
</tr>
</tbody>

<tbody>
<tr>
<td class="org-right">4</td>
<td class="org-left">gekido</td>
<td class="org-left">badial</td>
<td class="org-left">Infuriate power to inflict 2-16 damage to an enemy</td>
</tr>


<tr>
<td class="org-right">4</td>
<td class="org-left">gedoku</td>
<td class="org-left">latumofis</td>
<td class="org-left">Cure poison to a single target</td>
</tr>


<tr>
<td class="org-right">4</td>
<td class="org-left">hogo</td>
<td class="org-left">maporfic</td>
<td class="org-left">Reduce party's AC by 2 while you are in the dungeon</td>
</tr>


<tr>
<td class="org-right">4</td>
<td class="org-left">zenjiai</td>
<td class="org-left">-</td>
<td class="org-left">Heal entire party by 1-8 HP</td>
</tr>
</tbody>

<tbody>
<tr>
<td class="org-right">5</td>
<td class="org-left">daikaifuku</td>
<td class="org-left">dialma</td>
<td class="org-left">Restore 8-24 HP to a single target</td>
</tr>


<tr>
<td class="org-right">5</td>
<td class="org-left">kaminoikari</td>
<td class="org-left">litokan</td>
<td class="org-left">God's fire inflicts 3-24 damage to an enemy group</td>
</tr>


<tr>
<td class="org-right">5</td>
<td class="org-left">sosei</td>
<td class="org-left">di</td>
<td class="org-left">Attempt to ressurect a dead character</td>
</tr>


<tr>
<td class="org-right">5</td>
<td class="org-left">shisubeshi</td>
<td class="org-left">badi</td>
<td class="org-left">Attempt to kill an enemy</td>
</tr>
</tbody>

<tbody>
<tr>
<td class="org-right">6</td>
<td class="org-left">tenchu</td>
<td class="org-left">lorto</td>
<td class="org-left">Gods power to inflict 6-36 damage to an enemy group</td>
</tr>


<tr>
<td class="org-right">6</td>
<td class="org-left">kanzen</td>
<td class="org-left">madi</td>
<td class="org-left">Complete heal & cure</td>
</tr>


<tr>
<td class="org-right">6</td>
<td class="org-left">hinshi</td>
<td class="org-left">mabadi</td>
<td class="org-left">Gods power to almost kill a single enemy</td>
</tr>
</tbody>

<tbody>
<tr>
<td class="org-right">7</td>
<td class="org-left">tenchihokai</td>
<td class="org-left">malikto</td>
<td class="org-left">A meteor strike inflicts 12-72 damage to all enemies</td>
</tr>


<tr>
<td class="org-right">7</td>
<td class="org-left">fukkatsu</td>
<td class="org-left">kadorto</td>
<td class="org-left">Attempt to resurrent an even ashed person</td>
</tr>


<tr>
<td class="org-right">7</td>
<td class="org-left">zenkai</td>
<td class="org-left">-</td>
<td class="org-left">8-24 HP group heal to party</td>
</tr>
</tbody>
</table>

