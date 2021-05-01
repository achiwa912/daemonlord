import pickle
import re
import textwrap
import time
import random
import os
import sys
import struct
import tty
from enum import Enum
import fcntl
import json
import csv
from operator import itemgetter, attrgetter
import itertools
import collections
if os.name == 'nt':
    import msvcrt  # Windows
    os_windows = True
else:
    import termios  # Mac & Linux
    os_windows = False

config = {
    'debug': False,
}


class Job(Enum):
    FIGHTER, MAGE, PRIEST, THIEF, BISHOP, SAMURAI, LORD, NINJA, UNEMPLOYED = range(
        9)


class Race(Enum):
    HUMAN, ELF, DWARF, GNOME, HOBBIT = range(5)


class State(Enum):
    OK, ASLEEP, PARALYZED, STONED, DEAD, ASHED, LOST = range(7)


class Align(Enum):
    GOOD, NEUTRAL, EVIL = range(3)


class Place(Enum):
    MAZE, EDGE_OF_TOWN, TRAINING_GROUNDS, CASTLE, HAWTHORNE_TAVERN, TRADER_JAYS, LAKEHOUSE_INN, MGH, CAMP, BATTLE, LEAVE_GAME = range(
        11)


class Trap(Enum):
    TRAPLESS_CHEST, POISON_NEEDLE, CROSSBOW_BOLT, GAS_BOMB, STUNNER, EXPLODING_BOX, TELEPORTER, MAGE_BLASTER, PRIEST_BLASTER, ALARM = range(
        10)


class Eventid(Enum):
    RNDMSG, KEY, BOSS = range(
        3)


class Evloctype(Enum):
    RANDOM, DOWNSTAIRS = range(2)


race_status = {
    Race.HUMAN: (8, 8, 5, 8, 8, 9),
    Race.ELF: (7, 10, 10, 6, 9, 6),
    Race.DWARF: (10, 7, 10, 10, 5, 6),
    Race.GNOME: (7, 7, 10, 8, 10, 7),
    Race.HOBBIT: (5, 7, 7, 6, 10, 15),
}

job_requirements = {
    Job.FIGHTER: (11, 0, 0, 0, 0, 0, (True, True, True)),
    Job.MAGE: (0, 11, 0, 0, 0, 0, (True, True, True)),
    Job.PRIEST: (0, 0, 11, 0, 0, 0, (True, False, True)),
    Job.THIEF: (0, 0, 0, 0, 11, 0, (False, True, True)),
    Job.BISHOP: (0, 12, 12, 0, 0, 0, (True, False, True)),
    Job.SAMURAI: (15, 11, 10, 14, 10, 0, (True, True, False)),
    Job.NINJA: (15, 17, 15, 16, 15, 16, (False, False, True)),
    Job.LORD: (15, 12, 12, 15, 14, 15, (True, False, False)),
}

level_table = {
    Job.FIGHTER: (1000, 1724, 2972, 5124, 8834, 15231, 26260, 45275, 78060, 134586, 232044, 400075, 289709),
    Job.MAGE: (1100, 1896, 3268, 5634, 9713, 16746, 28872, 49779, 85825, 147974, 255127, 439874, 318529),
    Job.PRIEST: (1050, 1810, 3120, 5379, 9274, 15989, 27567, 47529, 81946, 141289, 243596, 419993, 304132),
    Job.THIEF: (900, 1551, 2674, 4610, 7948, 13703, 23625, 40732, 70227, 121081, 208760, 359931, 260326),
    Job.BISHOP: (1200, 2105, 3692, 6477, 11363, 19935, 34973, 61356, 107642, 188845, 331307, 581240, 438479),
    Job.SAMURAI: (1250, 2192, 3845, 6745, 11833, 20759, 36419, 63892, 112091, 196650, 345000, 605263, 456601),
    Job.LORD: (1300, 2280, 4000, 7017, 12310, 21596, 37887, 66468, 116610, 204578, 358908, 629663, 475008),
    Job.NINJA: (1450, 2543, 4461, 7829, 13729, 24085, 42254, 74179, 130050, 228157, 400275, 702236, 529756),
}

random_messages = [
    ["You hear a loud noise from south.",
     "You wondered if monsters are fighting down there."],
    ["You see a herd of mice.",
     "These mice are devoring a human-like figure.",
     "You noticed a pugent smell of blood."],
    ["You've lost a sense of time since you came down to this dungeon.",
     "Is it still early afternoon?  Or is it already late at night?"],
    ["It is hot and moist around this area.",
     "You've become very thirsty.  Do we have sufficient water with us?"],
    ["You found a piece of paper.",
     "You read: 'Her name is Anna.  She is dangerous.  You must run away from her while you still can.'"],
    ["You saw a word 'Help!' carved on the wall.",
     "Probably you are way too late for the rescue."],
    ["You saw scratches on the stone wall.",
     "Were these made with sharp claws of a monster?"],
    ["Look out!",
     "You almost caught in a deep pitfall.",
     "You saw some dead bodies and bones at the bottom."],
    ["You found some words on the surface of a wooden board.",
     "'Please, more light, &%*&#'"],
    ["Watch out!",
     "An arrow flew from your left and hit the stone wall."],
    ["You found a strange nutcracker.",
     "It started talking in a high piched voice.",
     "'You are doomed.  Go back while you can.'"],
    ["You found someone's journal.  On the last page, you read:",
     "'I would pay a millon gold if I could see sun light again.'"],
    ["You heard a voice in your head.",
     "'Do you know that this dungeon is a playground of the Lord?'",
     "'Do you think that you know what you are doing?'"],
    ["It's frigid in this area.",
     "Is there an icy monster around here?"],
    ["There should be other adventurers in this dungeon.",
     "You wondered why you don't see anyone else."],
    ["You just wish you could stay in a better room tonight.",
     "You are fed up with cabbage soup for dinner."],
    ["You find a message board saying:",
     "'From north west to south east.  Just keep walking to south east, fool!'"],
    ["You heard a voice in your head:",
     "'You are penetrating the Lords territory.'",
     "'It will cost you your lives.'"],
]


class Vscr:
    """
    Manage and control scroll window and virtual scroll windows
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.vscr0 = bytearray(b'P'*width*height)
        self.vscr1 = bytearray(b'Q'*width*height)
        self.prev_vscr_view = memoryview(self.vscr0)
        self.cur_vscr_view = memoryview(self.vscr1)
        self.meswins = []

    def draw_map(self, party, floor_obj):
        """
        Copy map data to a virtual scroll window
        """
        floor_view = memoryview(floor_obj.floor_data)
        cv = self.cur_vscr_view
        w = self.width
        for cy in range(self.height):
            cv[cy*w:(cy+1)*w] = b'^'*w  # fill with rocks
            my = party.y - (self.height-7)//2 + cy  # convert cy to floor_y
            if 0 <= my < floor_obj.y_size:
                l_left = min(0, party.x-w//2) * -1
                l_right = min(w, floor_obj.x_size - party.x + w//2)
                map_left = my*floor_obj.x_size + party.x - w//2 + l_left
                map_right = map_left + l_right - l_left
                cv[cy*w+l_left:cy*w+l_right] = floor_view[map_left:map_right]
            if cy == (self.height-7)//2:
                cv[cy*w+w//2:cy*w+w//2+1] = b'@'

    def cls(self):
        """
        clear both vscr0 and vscr1, and force clear screen
        """
        self.cur_vscr_view[:] = b' ' * self.width * self.height
        self.prev_vscr_view[:] = b' ' * self.width * self.height
        self.display(force=True)

    def display(self, force=False):
        """
        Actually print current virtual screen on the terminal and
        flip virtual screens for the next display.
        Caution: Do not call this method directly.  Use disp_scrwin() instead.
        """
        cv = self.cur_vscr_view
        w = self.width
        for y in range(self.height):
            slc = slice(y*w, (y+1)*w)
            if force == True or cv[slc] != self.prev_vscr_view[slc]:
                print(f"\033[{y+1};0H{cv[slc].tobytes().decode()}", end='')
        self.cur_vscr_view, self.prev_vscr_view = \
            self.prev_vscr_view, self.cur_vscr_view

    def draw_meswins(self):
        """
        Display the message window
        """
        for mw in self.meswins:
            meswidth = mw.width - 2
            if mw.frame:
                meswidth -= 4
            for y in range(mw.height):
                if len(mw.mes_lines) <= y:
                    line = ' '*(meswidth)
                else:
                    line = mw.mes_lines[y].ljust(meswidth)
                if mw.frame:
                    line = ''.join(['| ', line, ' |'])
                line = line.encode()
                vscr_left = (mw.y+y)*self.width + mw.x
                self.cur_vscr_view[vscr_left:vscr_left+len(line)] = line

    def draw_partywin(self, party):
        """
        Show the party window
        """
        for y in range(7):
            line = " # name       class  ac   hp status       "
            width = len(line)
            if y != 0:
                if len(party.members) >= y:
                    m = party.members[y-1]
                    hpchar = ' '
                    if m.hpplus > 0:
                        hpchar = '+'
                    elif m.hpplus < 0:
                        hpchar = '-'
                    alcls = ''.join([m.align.name[0], '-', m.job.name[:3]])
                    ac = m.ac + party.ac
                    if party.place == Place.BATTLE:
                        ac += m.acplus
                    if party.place == Place.BATTLE and \
                       m.state in [State.OK]:
                        line = f" {y} {m.name[:10].ljust(10)} {alcls} {ac:3d} {m.hp:4d}{hpchar}{m.action.ljust(13)}"
                    else:
                        if m.poisoned and m.state == State.OK:
                            line = f" {y} {m.name[:10].ljust(10)} {alcls} {ac:3d} {m.hp:4d}{hpchar}{'POISONED'.ljust(13)}"
                        else:
                            line = f" {y} {m.name[:10].ljust(10)} {alcls} {ac:3d} {m.hp:4d}{hpchar}{m.state.name[:13].ljust(13)}"
                else:
                    line = f" {y}" + ' '*(width-2)
            line = line.encode()
            vscr_left = (self.height-7+y)*self.width
            self.cur_vscr_view[vscr_left:vscr_left+len(line)] = line

    def draw_header(self, party):
        """
        Display the header info
        """
        if party.gps:
            line = f" daemon lord - dl - [{party.place.name.lower()}] floor:{party.floor:2d} ({party.x:3d}/{party.y:3d}) "
        else:
            line = f" daemon lord - dl - [{party.place.name.lower()}] floor:?? (???/???) "
        if party.identify:
            line = line + "<identify> "
        if party.light_cnt:
            line = line + "<light> "
        self.cur_vscr_view[:len(line)] = line.encode()

    def disp_scrwin(self, floor_obj=None):
        """
        Display scroll window main
        """
        game = self.game
        start = time.time()
        party = game.party
        if not floor_obj:
            floor_obj = party.floor_obj
        view_range = 1
        if party.light_cnt > 0:
            view_range = 3
        if party.place == Place.MAZE or party.place == Place.CAMP:
            for y in range(party.y-view_range, party.y+view_range+1):
                for x in range(party.x-view_range, party.x+view_range+1):
                    floor_obj.put_tile(
                        x, y, floor_obj.get_tile(x, y), orig=False)
            self.draw_map(party, floor_obj)
        self.draw_partywin(party)
        self.draw_header(party)
        self.draw_meswins()
        self.display()
        delta = time.time() - start
        try:
            print(
                f"\033[{self.height};0H", end='', flush=True)
        except:
            pass


class Meswin:
    """
    Message window.  A message line starts with "* ".
    """

    def __init__(self, vscr, x, y, width, height, frame=False):
        self.vscr = vscr
        self.width = min(width, vscr.width)
        self.height = min(height, vscr.height)
        self.x = x
        self.y = y
        self.cur_x = 0  # cursor position in message area
        self.cur_y = 0
        self.frame = frame
        self.show = False
        self.mes_lines = []
        self.cls()

    def change(self, x, y, width, height):
        """
        Change size and position of message window
        """
        self.x = x
        self.y = y
        self.width = min(width, self.vscr.width)
        self.height = min(height, self.vscr.height)

    def cls(self):
        # clear message area
        self.mes_lines = []

    def print(self, msg, start='*'):
        """
        Print a message in the message window.  Long text wraps
        to the next line.  Process '\n' in texts.
        """
        meswidth = self.width - 2
        if self.frame:
            meswidth -= 5

        sublines = re.split('\n', msg)
        for idx, sl in enumerate(sublines):  # subline
            header = '  '
            if idx == 0:
                header = start + ' '
            ssls = textwrap.wrap(sl, width=meswidth-1)
            if len(ssls) == 0:
                self.mes_lines.append(header)
            else:
                for ssl in ssls:
                    self.mes_lines.append(''.join([header, ssl]))
                    header = '  '
        if len(self.mes_lines) > self.height:
            self.mes_lines = self.mes_lines[len(
                self.mes_lines)-self.height:]
        self.cur_y = len(self.mes_lines)-1
        self.show = True

    def input(self, msg):
        """
        Input a string in the message window.
        """
        self.print(msg)
        self.print('', start='>')
        # self.vscr.draw_meswins()
        # self.vscr.display()
        self.vscr.disp_scrwin()
        print(f"\033[{self.y+self.cur_y+1};{self.x+5}H", end='', flush=True)
        try:
            value = input()
            self.mes_lines[self.cur_y] = "> " + value
        except:
            pass
        return value

    def input_char(self, msg, values=[]):
        """
        Input a character in the message window.
        """
        ch = ''
        while ch not in values:
            self.print(msg+' >', start=' ')
            self.vscr.disp_scrwin()
            print(f"\033[{self.y+self.cur_y+1};{self.x+len(msg)+8}H",
                  end='', flush=True)
            ch = getch()
            l = self.mes_lines.pop()
            self.print(''.join([l, ' ', ch])[2:], start=' ')
            self.vscr.disp_scrwin()
            if not values:
                break
        return ch


class Game:
    def __init__(self):
        self.characters = []  # registerd characters
        self.hospitalized = []  # members in the hospital
        self.party = None
        self.vscr = None
        self.dungeon = None
        self.spell = None
        self.battle = None

    def save(self):
        """
        Save game status for later resume.  If saved in dungeon,
        it saves floor objects as well.  As pickling party object
        resulted in an error (memoryview can't be pickled), convert
        it to a tuple first.  floor_obj has memoryview variable, too.
        """
        self.savedata = []
        self.savedata.append(self.characters)

        p = self.party
        ptpl = (p.x, p.y, p.px, p.py, p.floor, p.pfloor,
                p.light_cnt, p.ac, p.gps, p.place, p.silenced, p.identify)
        self.savedata.append(ptpl)
        mems = []  # list of names
        for mem in self.party.members:
            mems.append(mem.name)
        self.savedata.append(mems)

        self.savedata.append(self.shopitems)

        if p.place in [Place.MAZE, Place.CAMP, Place.BATTLE]:
            self.savedata.append(self.dungeon.events)
            for f in self.dungeon.floors:
                ftpl = (f.x_size, f.y_size, f.floor, f.up_x, f.up_y,
                        f.down_x, f.down_y, f.floor_data, f.floor_orig,
                        f.rooms, f.battled, f.events)
                self.savedata.append(ftpl)
            self.savedata.append(None)
        with open('savedata.pickle', 'wb') as f:
            pickle.dump(self.savedata, f)

    def load(self):
        """
        Load savedata.pickle to resume game.
        """
        try:
            with open('savedata.pickle', 'rb') as f:
                self.savedata = pickle.load(f)
        except:
            return False
        self.characters = self.savedata.pop(0)

        ptup = self.savedata.pop(0)
        self.load_party(ptup)
        mems = self.savedata.pop(0)
        self.party.members = []
        for mem in mems:
            for ch in self.characters:
                if mem == ch.name:
                    self.party.members.append(ch)

        self.shopitems = self.savedata.pop(0)

        if self.party.place not in [Place.MAZE, Place.CAMP, Place.BATTLE]:
            return

        self.dungeon.events = self.savedata.pop(0)
        self.dungeon.floors = []
        while True:
            ftpl = self.savedata.pop(0)
            if not ftpl:
                break
            x_size, y_size, floor, up_x, up_y, down_x, down_y, floor_data, floor_orig, rooms, battled, events = ftpl
            f = Floor(x_size, y_size, floor, floor_data)
            f.up_x, f.up_y = up_x, up_y
            f.down_x, f.down_y = down_x, down_y
            f.floor_orig = floor_orig
            f.floor_data = floor_data
            f.rooms = rooms
            f.battled = battled
            f.events = events
            self.dungeon.floors.append(f)
        self.party.floor_obj = self.dungeon.floors[self.party.floor-1]
        return True

    def load_party(self, ptup):
        p = self.party
        p.x, p.y, p.px, p.py, p.floor, p.pfloor, p.light_cnt, p.ac, p.gps, \
            p.place, p.silenced, p.identify = ptup
        if p.place in [Place.MAZE, Place.CAMP, Place.BATTLE]:
            p.resumed = True  # resume flag

    def load_monsterdef(self):
        """
        load monster definition file
        As fellow monster in csv is wizname, convert to dl name
        """
        Monster = collections.namedtuple(
            'Monster', ['names', 'unident', 'unidents', 'type',
                        'level', 'hp', 'ac', 'attack', 'count', 'act',
                        'poison', 'paraly',
                        'stone', 'critical', 'drain', 'breathsp', 'heal',
                        'regdeathp', 'regfire', 'regcold', 'regpoison',
                        'regspellp', 'weakmaka', 'weaksleep', 'friendly',
                        'exp', 'number', 'floors', 'fellow', 'fellowp',
                        'agi', 'treasure'])
        Tmpmonster = collections.namedtuple(
            'Tmpmonster', ['name', 'names', 'unident', 'unidents', 'type',
                           'level', 'hp', 'ac', 'attack', 'count', 'act1',
                           'act2', 'act3', 'act4', 'act5', 'poison', 'paraly',
                           'stone', 'critical', 'drain', 'breathsp', 'heal',
                           'regdeathp', 'regfire', 'regcold', 'regpoison',
                           'regspellp', 'weakmaka', 'weaksleep', 'friendly',
                           'exp', 'number', 'floors', 'fellowwiz', 'fellowp',
                           'agi', 'treasure'])
        with open('monsters.csv') as csvfile:
            rdr = csv.reader(csvfile)
            tmp_dic = {}
            for i, row in enumerate(rdr):
                if i == 0:
                    continue
                try:
                    level = int(row[7])
                except:
                    level = 1
                try:
                    ac = int(row[9])
                except:
                    ac = 10
                try:
                    count = int(row[11])
                except:
                    count = 1
                poison = False
                if row[17].lower() == 'true':
                    poison = True
                paraly = False
                if row[18].lower() == 'true':
                    paraly = True
                stone = False
                if row[19].lower() == 'true':
                    stone = True
                critical = False
                if row[20].lower() == 'true':
                    critical = True
                try:
                    drain = int(row[21])
                except:
                    drain = 0
                try:
                    heal = int(row[23])
                except:
                    heal = 0
                try:
                    regdeathp = int(row[24])
                except:
                    regdeathp = 0
                regfire = False
                if row[25].lower() == 'true':
                    regfire = True
                regcold = False
                if row[26].lower() == 'true':
                    regcold = True
                regpoison = False
                if row[27].lower() == 'true':
                    regpoison = True
                try:
                    regspellp = int(row[28])
                except:
                    regspellp = 0
                weakmaka = False
                if row[29].lower() == 'true':
                    weakmaka = True
                weaksleep = False
                if row[30].lower() == 'true':
                    weaksleep = True
                friendly = False
                if row[31].lower() == 'true':
                    friendly = True
                try:
                    exp = int(row[32])
                except:
                    exp = 0
                floors = row[34]  # floors
                if floors == '':
                    floors = {999}
                else:
                    floors_tmp = re.split(r',\s*', floors)
                    floors = set()
                    for floor in floors_tmp:
                        try:
                            floor = int(floor)
                        except:
                            floor = 999
                        floors.add(floor)
                try:
                    fellowp = int(row[36])
                except:
                    fellowp = 0
                try:
                    agi = int(row[37])
                except:
                    agi = 10
                treasure = row[38]
                if treasure == '':
                    treasure = []
                else:
                    treasure_tmp = re.split(r',\s*', treasure)
                    treasure = []
                    for level in treasure_tmp:
                        try:
                            level = int(level)
                            treasure.append(level)
                        except:
                            pass
                tmp_monster \
                    = Tmpmonster(row[2], row[3], row[4], row[5], row[6],
                                 level, row[8], ac, row[10], count, row[12],
                                 row[13], row[14], row[15], row[16], poison, paraly,
                                 stone, critical, drain, row[22], heal,
                                 regdeathp, regfire, regcold, regpoison,
                                 regspellp, weakmaka, weaksleep, friendly,
                                 exp, row[33], floors, row[35], fellowp, agi,
                                 treasure)
                tmp_dic[row[1]] = tmp_monster

        monster_def = {}
        for wizname, m in tmp_dic.items():
            if m.fellowwiz == '':
                fellow = ''
            else:
                fellow = tmp_dic[m.fellowwiz].name
            monster = Monster(m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8],
                              m[9], (m[10], m[11], m[12], m[13], m[14]), m[15],
                              m[16], m[17], m[18], m[19], m[20], m[21], m[22],
                              m[23], m[24], m[25], m[26], m[27], m[28], m[29],
                              m[30], m[31], m[32], fellow, m[34], m[35], m[36])
            monster_def[m.name] = monster
        self.mondef = monster_def

    def load_spelldef(self):
        """
        load spell definition file
        """
        Spell = collections.namedtuple(
            'Spell', ['categ', 'level', 'battle', 'camp', 'type', 'target', 'value', 'attr', 'desc'])
        with open('spells.csv') as csvfile:
            rdr = csv.reader(csvfile)
            spell_def = {}
            for i, row in enumerate(rdr):
                if i == 0:
                    continue
                attr = self.cell2strtup(row[10])
                # (0categ, 1level, 2battle, 3camp, 4type, 5target, 6value,
                #  7attr, 8desc)
                spell = Spell(row[1], int(row[2]), json.loads(row[5].lower()),
                              json.loads(row[6].lower()), row[7], row[8], row[9], attr, row[12])
                spell_def[row[3]] = spell
            self.spelldef = spell_def

    def load_itemdef(self):
        """
        load item definition file
        """
        Item = collections.namedtuple(
            'Item', ['level', 'unident', 'type', 'range', 'jobs', 'ac',
                     'st', 'at', 'dice', 'shop', 'price', 'curse',
                     'hp', 'use', 'brk', 'regist', 'twice', 'align',
                     'sp', 'target'])

        with open('items.csv') as csvfile:
            rdr = csv.reader(csvfile)
            item_def = {}
            for i, row in enumerate(rdr):
                if i == 0 or not row:
                    continue
                try:
                    level = int(row[1])
                except:
                    level = 0
                if not (name := row[2]):
                    name = row[4]
                if not (unident := row[3]):
                    unident = row[5]
                try:
                    ac = int(row[9])
                except:
                    ac = 0
                try:
                    st = int(row[10])
                except:
                    st = 0
                try:
                    at = int(row[11])
                except:
                    at = 0
                try:
                    shop = int(row[13])
                except:
                    shop = 0
                try:
                    price = int(row[14])
                except:
                    price = 0
                if row[15] == 'TRUE':
                    curse = True
                else:
                    curse = False
                try:
                    hp = int(row[16])
                except:
                    hp = 0
                try:
                    brk = int(row[18])
                except:
                    brk = 0
                regist = self.cell2strtup(row[19])
                twice = self.cell2strtup(row[20])
                align = self.cell2strtup(row[21])
                # (0level, 1unident, 2type, 3range, 4jobs, 5ac, 6st, 7at,
                #  8dice, 9shop, 10price, 11curse, 12hp, 13use, 14brk,
                #  15regist, 16twice, 17align, 18sp, 19target)
                item = Item(level, unident, row[6], row[7], row[8], ac,
                            st, at, row[12], shop, price,
                            curse, hp, row[17], brk, regist, twice, align,
                            row[22], row[23])
                item_def[name] = item
            self.itemdef = item_def
            self.shopitems = {}
            for name in self.itemdef:
                self.shopitems[name] = self.itemdef[name].shop

    def cell2strtup(self, cell):
        if cell == '':
            rtn = ()
        else:
            tmp = re.split(r',\s*', cell)
            rtn = []
            for t in tmp:
                rtn.append(t)
            rtn = tuple(rtn)
        return rtn


class Party:
    # Represents a party
    def __init__(self, x, y, floor):
        self.x = self.px = x
        self.y = self.py = y
        self.floor = self.pfloor = floor
        self.tsubasa_floor = 1  # to which floor? (valid when floor_move=3)
        self.floor_move = 0  # floor move flag
        self.resumed = False  # resume flag
        self.place = Place.EDGE_OF_TOWN
        self.floor_obj = ''
        self.members = []
        self.light_cnt = 0  # milwa=+30-45, lomilwa=+9999
        self.ac = 0  # -2 if maporfic
        self.silenced = False  # can't cast spell
        self.identify = False  # latumapic
        self.gps = False  # eternal dumapic

    def injured(self):
        """
        Check if someone is injured and return True/False
        dead, ashed, lost members are not counted
        """
        for mem in self.members:
            if mem.state in [State.DEAD, State.ASHED, State.LOST]:
                continue
            if mem.hp < mem.maxhp:
                return True
        return False

    def cast_spell(self, game, spell, target='party'):
        """
        If someone can cast the spell, cast it and return True
        If not, return False
        Only support heal and etc spells for now
        """
        for mem in self.members:
            if mem.state in [State.DEAD, State.ASHED, State.LOST]:
                continue
            if game.spell.cancast(mem, spell, consume=True):
                game.vscr.meswins[-1].print(f"{mem.name} casted {spell}")
                if spell in ['gps', 'hogo', 'shikibetsu', 'hikarinotama', 'kanzen']:
                    game.spell.etc(mem, spell, target)
                else:
                    game.spell.heal(mem, spell, target)
                game.vscr.disp_scrwin()
                getch(wait=True)
                return True
        return False

    def prep(self, game):
        """
        Cast hogo, shikibetsu, gps and lomilwa
        """
        if self.ac == 0:
            self.cast_spell(game, 'hogo')
        if not self.identify:
            self.cast_spell(game, 'shikibetsu')
        if not self.gps:
            self.cast_spell(game, 'gps')
        if self.light_cnt < 1000:
            self.cast_spell(game, 'hikarinotama')

    def heal(self, game):
        """
        Heal all members in the party
        """
        while self.injured():
            if not self.cast_spell(game, 'zenkai'):
                if not self.cast_spell(game, 'zenjiai'):
                    break
        for mem in self.members:
            if mem.state in [State.DEAD, State.ASHED, State.LOST]:
                continue
            if mem.hp == mem.maxhp:
                continue
            if not self.cast_spell(game, 'kanzen', mem):
                if not self.cast_spell(game, 'daikaifuku', mem):
                    if not self.cast_spell(game, 'iyashi', mem):
                        if not self.cast_spell(game, 'jiai', mem):
                            return

    def defeated(self):
        """
        Party defeat check after a battle, a boss battle or a chest
        """
        if sum(1 for m in self.members
               if m.state in [State.OK, State.ASLEEP]):
            return False  # at least one survives
        return True  # defeated

    def move(self, x, y, floor=None):
        """
        Move party to the specified (x, y) and optional floor
        """
        self.px = self.x
        self.py = self.y
        self.x = x
        self.y = y
        self.pfloor = self.floor
        if floor:
            self.floor = floor

    def calc_hpplus(self, game):
        for mem in self.members:
            mem.hpplus = sum(game.itemdef[item[0]].hp for item in mem.items)
            if mem.poisoned:
                mem.hpplus -= 1

    def consume_item(self, item):
        """
        Consume one item in the party member inventory
        """
        for mem in self.members:
            if item in mem.items:
                mem.items.remove(item)
                break

    def have_items(self, itemlist):
        """
        Return True someone in the party has one in itemlist
        """
        for it in itemlist:
            if it in [item[0] for mem in self.members
                      for item in mem.items]:
                return True
        return False

    def reorder(self, game):
        """
        Reorder party members
        """
        v = game.vscr
        mw = v.meswins[-1]
        dst = []
        idx = 1
        while True:
            c = mw.input_char(f"Who comes #{idx}? - # or l)eave")
            if c == 'l':
                break
            try:
                i = int(c)
                mem = self.members[i-1]
            except:
                mw.print("What?")
                continue
            if mem in dst:
                mw.print("Already chosen.")
                continue
            dst.append(mem)
            if len(dst) == len(self.members):
                self.members = dst
                break
            idx += 1

    def pay(self, gold):
        """
        Pay the price as a party.  Each member tries to pay their
        share but if they can't afford, someone will pay.
        """
        total = 0
        for mem in self.members:
            total += mem.gold
        if total < gold:
            return False  # Can't afford

        num = len(self.members)
        each = gold // num
        remain = gold % num
        for mem in self.members:
            if mem.gold >= each:
                mem.gold -= each
            else:
                remain += each - mem.gold
                mem.gold = 0

        for mem in self.members:
            if mem.gold >= remain:
                mem.gold -= remain
                return True
            else:
                remain -= mem.gold
                mem.gold = 0

    def can_open(self, game, ch=b'*'):
        """
        Check if they can unlock the door
        Returns True if they can, False otherwise
        """
        if ch == b'%':
            if game.party.floor == 3:
                keys = ['ivory key', 'bronze key', 'silver key', 'gold key']
            elif game.party.floor == 6:
                keys = ['bronze key', 'silver key', 'gold key']
            elif game.party.floor == 9:
                keys = ['silver key', 'gold key']
            elif game.party.floor == 10:
                keys = ['gold key']
            elif game.party.floor >= 11:
                keys = ['one time password']
            if game.party.have_items(keys):
                return True
            return False

        lvl = 1
        for mem in self.members:
            if mem.job in [Job.THIEF, Job.NINJA]:
                lvl = max(lvl, mem.level)
            else:
                lvl = max(lvl, mem.level//5+1)
        chance = max((lvl+1-self.floor)*10, 5)
        if random.randrange(100) < chance:
            return True
        else:
            return False

    def choose_character(self, game):
        """
        Choose and return a party member
        Return False if not chosen
        """
        mw = game.vscr.meswins[-1]
        while True:
            ch = mw.input_char(f"Who? - # or l)eave")
            if ch == 'l':
                break
            try:
                if 0 <= (chid := int(ch)-1) < len(game.party.members):
                    break
            except:
                pass
        if ch == 'l':
            return False
        return self.members[chid]

    def remove_character(self, game):
        """
        Choose and remove a party member
        """
        mw = game.vscr.meswins[-1]
        while True:
            ch = mw.input_char(f"Remove who? - # or l)eave")
            if ch == 'l':
                break
            try:
                if 0 <= (chid := int(ch)-1) < len(game.party.members):
                    del self.members[chid]
                    game.vscr.disp_scrwin()
            except:
                pass


class Member:
    # Represents a character
    def __init__(self, name, align, race):
        self.name = name
        self.align = align
        self.race = race
        self.level = 1
        self.ac = 10
        self.acplus = 0  # valid only in battle
        self.job = Job.UNEMPLOYED
        self.state = State.OK
        self.silenced = False  # valid only in battle
        self.poisoned = False
        self.inspected = False  # valid only for inspecting chest
        self.deepest = 1  # deepest floor visited at least once
        self.floor = 0  # for defeated party member
        self.in_maze = False  # for defeated party member
        self.gold = random.randrange(100, 200)
        self.exp = 0
        self.nextexp = 0
        self.marks = 0
        self.rip = 0
        self.items = []  # 0name, 1equipped, 2cursed, 3unidentified
        self.stat = [0, 0, 0, 0, 0, 0]
        self.stat[0], self.stat[1], self.stat[2], self.stat[3], self.stat[4], \
            self.stat[5] = race_status[race]
        self.maxhp = 0
        self.hp = self.maxhp
        self.hpplus = 0  # -1 if poisoned, >0 if healing item
        self.mspells = []
        self.pspells = []
        self.mspell_cnt = [0, 0, 0, 0, 0, 0, 0]
        self.pspell_cnt = [0, 0, 0, 0, 0, 0, 0]
        self.mspell_max = [0, 0, 0, 0, 0, 0, 0]
        self.pspell_max = [0, 0, 0, 0, 0, 0, 0]

    def __repr__(self):
        return f"<{self.name}, {self.align.name[:1]}-{self.race.name[:3]}-{self.job.name[:3]} {self.stat[0]}/{self.stat[1]}/{self.stat[2]}/{self.stat[3]}/{self.stat[4]}>"

    def __str__(self):
        return f"{self.name[:16].ljust(16)} Lv{self.level:3d} {self.race.name[:3].lower()}-{self.align.name[:1].lower()}-{self.job.name[:3].lower()}"

    def disp_character(self, game):
        """
        Display a character information in the message window
        """
        vscr = game.vscr
        mw = vscr.meswins[-1]
        mw.mes_lines = []
        mw.print(
            f"{self.name.ljust(16)} L{self.level:3d} {self.align.name[:1].lower()}-{self.job.name[:3].lower()} {self.race.name.lower()}", start=' ')
        mw.print(f"", start=' ')
        mw.print(
            f"strength {self.stat[0]:2d}  gold {self.gold:16d}   lvl {self.level:5d}", start=' ')
        mw.print(
            f"    i.q. {self.stat[1]:2d}  e.p. {self.exp:16d}   rip {self.rip:5d}", start=' ')
        mw.print(
            f"   piety {self.stat[2]:2d}  next {self.nextexp:16d}   a.c.{self.ac:5d}", start=' ')
        mw.print(
            f"vitality {self.stat[3]:2d}  marks {self.marks:15d}   depth{self.deepest:4d}", start=' ')
        mw.print(
            f" agility {self.stat[4]:2d}  h.p.  {self.hp:7d}/{self.maxhp:7d}", start=' ')
        if self.state == State.OK and self.poisoned:
            mw.print(
                f"    luck {self.stat[5]:2d}  status   POISONED", start=' ')
        else:
            mw.print(
                f"    luck {self.stat[5]:2d}  status   {self.state.name}", start=' ')
        mw.print(f"", start=' ')
        mw.print(f"mage  {self.mspell_cnt[0]}/{self.mspell_cnt[1]}/{self.mspell_cnt[2]}/{self.mspell_cnt[3]}/{self.mspell_cnt[4]}/{self.mspell_cnt[5]}/{self.mspell_cnt[6]}   priest  {self.pspell_cnt[0]}/{self.pspell_cnt[1]}/{self.pspell_cnt[2]}/{self.pspell_cnt[3]}/{self.pspell_cnt[4]}/{self.pspell_cnt[5]}/{self.pspell_cnt[6]}/", start=' ')
        for idx in range(8):
            try:
                item = self.items[idx]
                m = ' '
                if self.job.name[:1].lower() not in \
                   game.itemdef[item[0]].jobs.lower():
                    m = '#'  # can't equip
                if item[1]:
                    m = '*'  # equipped
                if item[2]:
                    m = '&'  # cursed
                if self.items[idx][3]:  # unidentified
                    l = f"{m}?{game.itemdef[item[0]].unident}"
                else:
                    l = f"{m}{item[0]}"
            except:
                l = ''
            if idx % 2:
                mw.print(f"{idx}) {ol.ljust(18)} {idx+1}) {l.ljust(18)}",
                         start=' ')
            ol = l

    def inspect_character(self, game):
        """
        Inspect a character
        Show the character info and dispatch item or spell menus
        """
        mw = game.vscr.meswins[-1]
        while game.party.members:
            if game.party.floor_move and game.party.place == Place.CAMP:
                break
            self.disp_character(game)
            mw.print(f"", start=' ')
            c1 = mw.input_char("i)tems s)pells c)lass jk)change member l)leave",
                               values=['i', 's', 'c', 'j', 'k', 'l'])
            if c1 == 'l':
                mw.cls()
                return 0  # leave
            elif c1 == 'i':
                self.item_menu(game)
            elif c1 == 's':
                self.spell_menu(game)
            elif c1 == 'c' and game.party.place == Place.TRAINING_GROUNDS:
                self.change_classes(game)
            elif c1 == 'j':
                return 1  # next member
            elif c1 == 'k':
                return -1  # previous member
        return 0

    def view_spells(self, game):
        """
        View mage and priest spell list that he/she has mastered
        """
        v = game.vscr
        sw = Meswin(v, 1, 2, 76, 14)
        v.meswins.append(sw)
        d = game.spelldef
        lines = []
        if self.mspells:
            lines.append("Mage spells:")
            for name in self.mspells:
                lines.append(
                    f"{d[name].level} {name.ljust(13)}{d[name].desc[:57]}")
            lines.append("")
        if self.pspells:
            lines.append("Priest spells:")
            for name in self.pspells:
                lines.append(
                    f"{d[name].level} {name.ljust(13)}{d[name].desc[:57]}")
        if len(lines) <= 14-1:
            for l in lines:
                sw.print(l, start=' ')
            sw.print("Press any key.")
            v.disp_scrwin()
            getch()
        else:
            idx = 0
            while True:
                sw.cls()
                for l in lines[idx:idx+14-1]:
                    sw.print(l, start=' ')
                sw.print("j)down k)up l)eave")
                v.disp_scrwin()
                c = getch(wait=True)
                if c == 'j' and idx < len(lines)-14+1:
                    idx += 1
                elif c == 'k' and idx > 0:
                    idx -= 1
                elif c == 'l':
                    break
        # sw.cls()
        v.disp_scrwin()
        v.meswins.pop()
        v.cls()

    def spell_menu(self, game):
        """
        Spell menu.  Cast, read spells.
        """
        v = game.vscr
        mw = Meswin(v, 14, 4, 44, 12, frame=True)
        v.meswins.append(mw)
        while not game.party.floor_move or \
                game.party.place not in \
                [Place.MAZE, Place.CAMP, Place.BATTLE]:  # if not tsubasa
            mw.print("Spell memu:")
            c = mw.input_char("c)ast spell v)iew list l)eave",
                              values=['c', 'v', 'l'])
            if c == 'l':
                break
            elif c == 'c':
                if game.party.place in [Place.CAMP, Place.BATTLE]:
                    game.spell.cast_spell(self)
                else:
                    mw.print("Can't cast spell now.")
                    v.disp_scrwin()
            elif c == 'v':
                self.view_spells(game)
        # mw.cls()
        v.disp_scrwin()
        v.meswins.pop()
        v.cls()

    def item_menu(self, game):
        """
        Item menu.  Use, equip, trade, drop an item.
        """
        vscr = game.vscr
        iw = Meswin(vscr, 14, 2, 44, 8, frame=True)
        vscr.meswins.append(iw)
        while True:
            iw.print("which item?  # or l)leave")
            vscr.disp_scrwin()
            c = getch()
            if c == 'l':
                vscr.meswins.pop()
                vscr.cls()
                return
            try:
                if (inum := int(c)-1) > len(self.items)-1:
                    continue
            except:
                continue
            dispname = self.items[inum][0]
            if self.items[inum][3]:  # unidentified
                dispname = ''.join(['?', game.itemdef[dispname].unident])
            iw.print(f"{inum+1}) {dispname}", start=' ')
            c = iw.input_char("u)se e)quip t)rade d)rop l)eave",
                              values=['u', 'e', 't', 'd', 'l'])
            if c == 'l':
                continue
            elif c == 'u':
                if self.items[inum][3]:  # unidentified:
                    iw.print(f"Tried to use {dispname}.")
                    iw.print(
                        ".. but don't know how to use it.", start=' ')
                    vscr.disp_scrwin()
                else:
                    itemdef = game.itemdef[self.items[inum][0]]
                    if not itemdef.use:
                        iw.print(f"Tried to use {dispname}.")
                        iw.print(".. but wasn't able to.", start=' ')
                        vscr.disp_scrwin()
                    elif itemdef.use == 'etc':
                        iw.print(f"Used {dispname}.")
                        vscr.disp_scrwin()
                        if self.items[inum][0] == 'muramasa blade':
                            self.stat[0] += 1  # str+1
                        elif self.items[inum][0] == 'kaiser knuckles':
                            self.maxhp += 1  # hp+1
                        elif self.items[inum][0] == 'armor of lords':
                            for m in game.party.members:
                                m.hp = m.maxhp
                        elif self.items[inum][0] == 'ninja dagger':
                            self.job = Job.NINJA
                            for i in self.items:
                                i[1] = False
                        if itemdef.brk > random.randrange(100):
                            self.items[inum][0] = 'broken item'
                        getch(wait=True)
                        vscr.meswins.pop()
                        vscr.cls()
                        return
                    else:  # magic spell
                        sdef = game.spelldef[itemdef.use]
                        if not sdef.camp:
                            iw.print("Can't use it now.")
                        if sdef.target == 'member':
                            target = game.party.choose_character(
                                game)
                            if not target:
                                #mw = game.vscr.meswins[-1]
                                iw.print("Aborted.", start=' ')
                                continue
                        else:
                            target = sdef.target
                        iw.print(f"Used {dispname}.")
                        vscr.disp_scrwin()
                        game.spell.cast_spell_dispatch(
                            self, itemdef.use, target)
                        if itemdef.brk > random.randrange(100):
                            self.items[inum][0] = 'broken item'
                        vscr.meswins.pop()
                        vscr.cls()
                        return
            elif c == 't':
                if self.items[inum][2]:
                    iw.print(f"Cursed.")
                    vscr.disp_scrwin()
                    continue
                elif self.items[inum][1]:
                    iw.print(f"Equipped.")
                    vscr.disp_scrwin()
                    continue
                target = game.party.choose_character(game)
                if target and len(target.items) < 8:
                    target.items.append(self.items[inum])
                    self.items.pop(inum)
                    iw.print(f"Gave to {target.name}.")
                    vscr.disp_scrwin()
                    getch(wait=True)
                vscr.meswins.pop()
                vscr.cls()
                break
            elif c == 'd':
                if self.items[inum][2]:
                    iw.print(f"Cursed.")
                    vscr.disp_scrwin()
                    continue
                elif self.items[inum][1]:
                    iw.print(f"Equipped.")
                    vscr.disp_scrwin()
                    continue
                c = iw.input_char(f"Drop {dispname}? (y/n)",
                                  values=['y', 'n'])
                if c == 'y':
                    self.items.pop(inum)
                    iw.print(f"Dropped {dispname}.")
                    vscr.disp_scrwin()
                    vscr.meswins.pop()
                    vscr.cls()
                    break
            elif c == 'e':
                if self.job.name[:1] not in game.itemdef[self.items[inum][0]].jobs:
                    iw.print("Can't equip the item.")
                    continue
                for item in self.items:
                    if game.itemdef[self.items[inum][0]].type \
                       == game.itemdef[item[0]].type:
                        if item[2]:  # already cursed
                            iw.print("Already equipped a cursed item.")
                            break
                        elif item[1]:  # equipped
                            item[1] = False
                            if item is self.items[inum]:
                                self.calc_ac(game)
                                vscr.meswins.pop()
                                vscr.cls()
                                return
                if game.itemdef[self.items[inum][0]].curse:
                    self.items[inum][2] = True  # cursed
                    iw.print("Cursed!")
                    vscr.disp_scrwin()
                    getch()
                self.items[inum][1] = True  # equipped
                self.calc_ac(game)
                vscr.meswins.pop()
                vscr.cls()
                # vscr.disp_scrwin()
                return

    def calc_ac(self, game):
        """
        Utility method to calculate AC
        """
        self.ac = 10
        for item in self.items:
            if item[1] or item[2]:
                self.ac += game.itemdef[item[0]].ac

    def job_applicable(self, sp, jobnum):
        """
        Utility function to check if the character is applicable for the job
        """
        for i in range(6):
            if sp[i]+self.stat[i] < job_requirements[Job(jobnum)][i]:
                return False
        if job_requirements[Job(jobnum)][6][self.align.value]:
            return True
        else:
            return False

    def calc_bonus(self):
        """
        Calculate bonus points (on creating a character)
        """
        bonus = random.randrange(5, 10)
        for _ in range(3):
            if random.randrange(6) == 0:
                bonus += 10
        return bonus

    def bonus_disp(self, game, bonus, y, sp):
        """
        Display bonus assignment screen
        """
        vscr = game.vscr
        mw = vscr.meswins[-1]
        mw.cls()
        mw.print("Distribute bonus points -")
        mw.print("  h)minus j)down k)up l)plus", start=' ')
        mw.print("  .)change bonus x)done", start=' ')
        mw.print("", start=' ')
        mw.print(f"  strength  {sp[0]+self.stat[0]:2d}", start=' ')
        mw.print(f"  iq        {sp[1]+self.stat[1]:2d}", start=' ')
        mw.print(f"  piety     {sp[2]+self.stat[2]:2d}", start=' ')
        mw.print(f"  vitality  {sp[3]+self.stat[3]:2d}", start=' ')
        mw.print(f"  agility   {sp[4]+self.stat[4]:2d}", start=' ')
        mw.print(f"  luck      {sp[5]+self.stat[5]:2d}", start=' ')
        mw.print(f"\n  bonus     {bonus:2d}", start=' ')
        mw.print("", start=' ')
        mw.mes_lines[y+4] = mw.mes_lines[y+4][:13] + \
            '>' + mw.mes_lines[y+4][14:]
        line = ''
        job = False
        for jobnum in range(8):
            if self.job_applicable(sp, jobnum):
                job = True
                line = ''.join([line, Job(jobnum).name[:].lower(), ' '])
        mw.print(line, start=' ')
        vscr.disp_scrwin()
        return job

    def change_classes(self, game):
        """
        Change classes
        """
        v = game.vscr
        mw = v.meswins[-1]
        statplus = [0, 0, 0, 0, 0, 0]
        jobs = [';']
        jobnames = ''
        line = ''
        for jobnum in range(8):
            if self.job_applicable(statplus, jobnum) and self.job != Job(jobnum):
                jobnames = ' '.join([jobnames, Job(jobnum).name.lower()])
                line = '/'.join([line, Job(jobnum).name[:1].lower()])
                jobs.append(Job(jobnum).name[:1].lower())
        line = line[1:]  # remove the first '/'
        mw.print(f"{self.name} can apply for:")
        mw.print(f"  {jobnames}")
        c = mw.input_char(f"Which job to apply? ({line} or ;)leave)")
        if c == ';' or mw.input_char("Are you sure? (y/n)",
                                     values=['y', 'n']) != 'y':
            mw.print("Cancelled.")
            v.disp_scrwin()
            return
        for jobnum in range(8):
            if c == Job(jobnum).name[:1].lower():
                break
        self.job = Job(jobnum)
        self.nextexp = level_table[Job(jobnum)][0]
        self.exp = 0
        self.level = 1
        for item in self.items:
            item[1] = item[2] = False
        self.calc_ac(game)
        for i in range(6):
            self.stat[i] = race_status[self.race][i]
        if self.job not in [Job.MAGE, Job.SAMURAI, Job.BISHOP]:
            for spell_level in range(7):
                mastered = sum([
                    1 for spell in game.spelldef
                    if game.spelldef[spell].level == spell_level+1 and
                    spell in self.mspells])
                self.mspell_max[spell_level] = mastered
                self.mspell_cnt[spell_level] = mastered
        if self.job not in [Job.PRIEST, Job.LORD, Job.BISHOP]:
            for spell_level in range(7):
                mastered = sum([
                    1 for spell in game.spelldef
                    if game.spelldef[spell].level == spell_level+1 and
                    spell in self.pspells])
                self.pspell_max[spell_level] = mastered
                self.pspell_cnt[spell_level] = mastered
        if self.job == Job.MAGE:
            self.mspells.append('onibi')
            self.mspells.append('shunmin')
            self.mspells = list(set(self.mspells))
            self.mspell_max[0] = self.mspell_cnt[0] = max(
                2, self.mspell_max[0])
        elif self.job == Job.PRIEST:
            self.pspells.append('jiai')
            self.pspells.append('ikari')
            self.pspells = list(set(self.pspells))
            self.pspell_max[0] = self.pspell_cnt[0] = max(
                2, self.pspell_max[0])
        mw.print(f"{self.name} has become a novice {self.job.name.lower()}.")
        v.disp_scrwin()

    def distribute_bonus(self, game):
        """
        Bonus assignment and deciding class main routine
        """
        v = game.vscr
        newwin = False
        mw = v.meswins[-1]
        if mw.height < 14:  # if exisiting window is too narrow
            mw = Meswin(v, 13, 2, 55, 14, frame=True)
            v.meswins.append(mw)
            newwin = True
        bonus = self.calc_bonus()
        y = 0
        statplus = [0, 0, 0, 0, 0, 0]
        while True:
            job = self.bonus_disp(game, bonus, y, statplus)
            c = getch()
            if c == 'x' and bonus == 0 and job:
                break
            elif c == 'j' and y < 5:
                y += 1
            elif c == 'k' and y > 0:
                y -= 1
            elif c == 'h' and statplus[y] > 0:
                statplus[y] -= 1
                bonus += 1
            elif c == 'l' and statplus[y]+self.stat[y] < \
                    race_status[self.race][y]+10 and bonus > 0:
                statplus[y] += 1
                bonus -= 1
            elif c == '.':
                statplus = [0, 0, 0, 0, 0, 0]
                bonus = self.calc_bonus()
        jobs = []
        line = "Choose class ("
        for jobnum in range(8):
            if self.job_applicable(statplus, jobnum):
                line = ''.join([line, Job(jobnum).name[:1].lower(), '/'])
                jobs.append(Job(jobnum).name[:1].lower())
        line = ''.join([line[:-1], ')'])
        mw = game.vscr.meswins[-1]
        c = mw.input_char(line, values=jobs)
        for jobnum in range(8):
            if c == Job(jobnum).name[:1].lower():
                break
        self.job = Job(jobnum)
        self.nextexp = level_table[Job(jobnum)][0]
        if self.job == Job.FIGHTER:
            self.maxhp = self.hp = random.randint(8, 15)
        elif self.job == Job.MAGE:
            self.maxhp = self.hp = random.randint(2, 7)
            self.mspells = ['onibi', 'shunmin']
            self.mspell_max = [2, 0, 0, 0, 0, 0, 0]
            self.mspell_cnt = [2, 0, 0, 0, 0, 0, 0]
        elif self.job == Job.PRIEST:
            self.maxhp = self.hp = random.randint(6, 13)
            self.pspells = ['jiai', 'ikari']
            self.pspell_max = [2, 0, 0, 0, 0, 0, 0]
            self.pspell_cnt = [2, 0, 0, 0, 0, 0, 0]
        elif self.job == Job.THIEF or Job.BISHOP:
            self.maxhp = self.hp = random.randint(4, 9)
        elif self.job == Job.SAMURAI:
            self.maxhp = self.hp = random.randint(12, 19)
        elif self.job == Job.LORD:
            self.maxhp = self.hp = random.randint(12, 19)
        else:  # ninja
            self.maxhp = self.jp = random.randint(8, 17)

        for i in range(6):
            self.stat[i] += statplus[i]
        game.characters.append(self)
        mw.print("Character created")
        game.vscr.disp_scrwin()
        getch(wait=True)
        if newwin:
            v.meswins.pop()
        v.cls()


class Spell:
    """
    Has actual spell implementation here
    """

    def __init__(self, game):
        self.game = game

    def cancast(self, mem, spell, consume=False):
        """
        Check if mem has mastered the spell and has MP
        Return True if can (and consumed if concume=True)
        Return False if can not
        """
        if mem.state not in [State.OK]:
            return False
        spelldef = self.game.spelldef[spell]
        if spell in mem.mspells:
            if mem.mspell_cnt[spelldef.level-1] > 0:
                if consume:
                    mem.mspell_cnt[spelldef.level-1] -= 1
                return True
        elif spell in mem.pspells:
            if mem.pspell_cnt[spelldef.level-1] > 0:
                if consume:
                    mem.pspell_cnt[spelldef.level-1] -= 1
                return True
        return False

    def spell_counts(self, start, diff, level):
        """
        Utility funciton to calculate spell counts.
        """
        clist = []
        l = level - start
        clist.append(l)
        for _ in range(6):
            l = l - diff
            clist.append(min(max(l, 0), 9))
        return clist

    def cast_spell(self, mem):
        game = self.game
        v = game.vscr
        mw = v.meswins[-1]
        s = mw.input("What spell to cast?")
        if s not in game.spelldef:  # No such spell
            mw.print("What?", start=' ')
            return
        elif s not in list(itertools.chain(mem.mspells, mem.pspells)):
            mw.print("Haven't mastered the spell.", start=' ')
            return

        sdef = game.spelldef[s]
        if game.party.place == Place.BATTLE:
            if not sdef.battle:
                mw.print("Can't cast now.", start=' ')
                return
        elif not sdef.camp:  # note: you can use it at tavern, too.
            mw.print("Can't cast it now.", start=' ')
            return

        if sdef.categ == 'mage':
            splcntlst = mem.mspell_cnt
        else:
            splcntlst = mem.pspell_cnt
        if splcntlst[sdef.level-1] <= 0:
            mw.print("MP exhausted.", start=' ')
            return

        if sdef.target == 'member':
            target = self.game.party.choose_character(self.game)
            if not target:
                mw = self.game.vscr.meswins[-1]
                mw.print("Aborted.", start=' ')
                return
        elif sdef.target in ['enemy', 'group']:
            gnum = self.game.battle.choose_group()
            target = self.game.battle.monp[gnum]
        else:
            target = sdef.target

        splcntlst[sdef.level-1] -= 1

        mw.print(f"{mem.name} started casting {s}", start=' ')
        v.disp_scrwin()
        self.cast_spell_dispatch(mem, s, target)

    def cast_spell_dispatch(self, invoker, spell, target):
        sdef = self.game.spelldef[spell]
        if sdef.type == 'heal':
            self.heal(invoker, spell, target)
        elif sdef.type in ['attack', 'death']:
            self.attack(invoker, spell, target)
        elif sdef.type == 'ac':
            self.ac(invoker, spell, target)
        elif sdef.type == 'status':
            self.status(invoker, spell, target)
        elif sdef.type == 'cure':
            self.cure(invoker, spell, target)
        else:  # etc
            self.etc(invoker, spell, target)

    def cure(self, invoker, spell, target):
        v = self.game.vscr
        mw = v.meswins[-1]
        spelldef = self.game.spelldef[spell]
        if spell == 'okiro':
            if target.state in [State.ASLEEP, State.PARALYZED]:
                target.state = State.OK
                mw.print(f"{target.name} is awaken.", start=' ')
                v.disp_scrwin()
        elif spell == 'gedoku':
            if target.poisoned:
                target.poisoned = False
                target.hpplus += 1
                mw.print(f"{target.name} is cured.", start=' ')
                v.disp_scrwin()

    def etc(self, invoker, spell, target):
        v = self.game.vscr
        mw = v.meswins[-1]
        spelldef = self.game.spelldef[spell]
        if spell == 'gps':
            self.game.party.gps = True
        elif spell == 'tsubasa':
            party = self.game.party
            fl = mw.input(f"To which floor? (1-{invoker.deepest})")
            try:
                fl = int(fl)
                if 0 < fl <= invoker.deepest:
                    party.floor_move = 3  # tsubasa; on the upstairs
                    party.tsubasa_floor = fl
                    return
            except:
                pass
            mw.print("What?")
            v.disp_scrwin()
        elif spell == 'shikibetsu':
            self.game.party.identify = True
        elif spell == 'hogo':
            self.game.party.ac = int(spelldef.value)
        elif spell == 'akari':
            self.game.party.light_cnt += random.randrange(15) + 30
        elif spell == 'hikarinotama':
            self.game.party.light_cnt += 9999
        elif spell == 'kanzen':
            if target.state not in [State.DEAD, State.ASHED, State.LOST]:
                target.hp = target.maxhp
                target.state = State.OK
                if target.poisoned:
                    target.poisoned = False
                self.game.party.calc_hpplus(self.game)
                mw.print(f"{target.name} is completely healed.", start=' ')
        elif spell == 'senmetsu':
            monptmp = self.game.battle.monp[:]
            for mong in monptmp:
                mondef = self.game.mondef[mong.name]
                if mong.identified:
                    dispname = mondef.names
                else:
                    dispname = mondef.unidents
                if mondef.weakmaka:
                    self.game.battle.exp += len(mong.monsters) * \
                        mondef.exp
                    monsterg = mong.monsters
                    for mon in monsterg:
                        mon.state = State.DEAD
                        # mong.monsters.remove(mon)
                    mw.print(f"{dispname} are perished.", start=' ')
                    # self.game.battle.monp.remove(mong)
                    v.disp_scrwin()
        elif spell == 'hinshi':
            if isinstance(invoker, Member):
                mondef = self.game.mondef[target.name]
                if target.identified:
                    disptarget = target.name
                else:
                    disptarget = mondef.unident
                if random.randrange(100) >= mondef.regspellp:
                    damage = max(
                        target.monsters[0].hp - random.randrange(7) - 1, 0)
                    target.monsters[0].hp -= damage
                    mw.print(
                        f"{disptarget} incurred {damage} damage.", start=' ')
                else:
                    mw.print(f"{disptarget} registed the spell.", start=' ')
            else:
                target = random.choice([mem for mem in self.game.party.members
                                        if mem.state in [State.OK, State.ASLEEP]])
                regspellp = target.stat[5] * 100/20  # luck
                if random.randrange(100) >= regspellp:
                    damage = max(target.hp - random.randint(7) - 1, 0)
                    target.hp -= damage
                    mw.print(
                        f"{target.name} incurred {damage} damage.", start=' ')
                else:
                    mw.print(f"{target.name} registed the spell.", start=' ')
        elif spell == 'sosei':  # party member only
            if target.state != State.DEAD:
                mw.print(f"{target.name} is not dead.", start=' ')
            else:
                chance = (target.stat[3]+target.stat[5]) * 100//45
                if random.randrange(100) < chance:
                    mw.print(f"{target.name} is resurrected.", start=' ')
                    target.stat[3] -= 1
                    target.state = State.OK
                    target.hp = min(target.maxhp, random.randrange(7)+1)
                else:
                    mw.print(f"Failed to resurrect {target.name}.", start=' ')
                    target.state = State.ASHED
        elif spell == 'fukkatsu':
            if target.state not in [State.DEAD, State.ASHED]:
                mw.print(f"{target.name} is not dead or ashed.", start=' ')
            else:
                chance = (target.stat[3]+target.stat[5]) * 100//40
                if random.randrange(100) < chance:
                    mw.print(f"{target.name} is resurrected.", start=' ')
                    target.stat[3] -= 1
                    target.state = State.OK
                    target.hp = target.maxhp
                else:
                    mw.print(f"Failed to resurrect {target.name}.", start=' ')
                    if target.state == State.DEAD:
                        target.state = State.ASHED
                    else:  # was ashed
                        target.state = State.LOST

    def ac(self, invoker, spell, target):
        """
        Decrease peer(s)' or increase opponent(s)' AC
        """
        v = self.game.vscr
        mw = v.meswins[-1]
        spelldef = self.game.spelldef[spell]
        if spelldef.target == 'self':
            if isinstance(invoker, Member):
                invoker.acplus += int(spelldef.value)
            else:
                invoker.ac += int(spelldef.value)
        elif spelldef.target == 'party':
            if isinstance(invoker, Member):
                for m in self.game.party.members:
                    m.acplus += int(spelldef.value)
            else:
                for m in self.game.battle.monp[0].monsters:
                    m.ac += int(spelldef.value)
        elif spelldef.target == 'enemy':
            if isinstance(invoker, Member):
                target.monsters[0].ac += int(spelldef.value)
            else:
                mem = random.choice(self.game.party.members)
                mem.acplus += int(spelldef.value)
        elif spelldef.target == 'group':
            if isinstance(invoker, Member):
                for mon in target.monsters:
                    mon.ac += int(spelldef.value)
            else:
                for mem in self.game.party.members:
                    mem.acplus += int(spelldef.value)
        else:  # 'all'
            if isinstance(invoker, Member):
                for mong in self.game.battle.monp:
                    for mon in mong:
                        mon.ac += int(spelldef.value)
            else:
                for mem in self.game.party.members:
                    mem.acplus += int(spelldef.value)

    def status(self, invoker, spell, target):
        """
        Spells that could put to sleep and silence the target group.
        """
        v = self.game.vscr
        mw = v.meswins[-1]
        spelldef = self.game.spelldef[spell]
        if isinstance(invoker, Member):
            if target.identified:
                disptarget = target.name
            else:  # unidentified
                disptarget = self.game.mondef[target.name].unident
            for mon in target.monsters:
                if 'sleep' in spelldef.attr and mon.state == State.OK:
                    if mon.mdef.weaksleep:
                        chance = 80
                    else:
                        chance = 35
                    if random.randrange(100) < chance and \
                       random.randrange(100) >= mon.mdef.regspellp:
                        mon.state = State.ASLEEP
                    if mon.state == State.ASLEEP:
                        mw.print(f"{disptarget} is slept.", start=' ')
                    else:
                        mw.print(f"{disptarget} is not slept.", start=' ')
                if 'silence' in spelldef.attr:
                    chance = 50 * mon.mdef.regspellp // 100
                    if random.randrange(100) < chance or mon.silenced:
                        mon.silenced = True
                        mw.print(f"{disptarget} is silenced.", start=' ')
                    else:
                        mw.print(f"{disptarget} is not silenced.", start=' ')
        else:
            for mem in self.game.party.members:
                if 'sleep' in spelldef.attr and mem.state == State.OK:
                    if random.randrange(100) < 35:
                        mem.state = State.ASLEEP
                    if mem.state == State.ASLEEP:
                        mw.print(f"{mem.name} is slept.", start=' ')
                    else:
                        mw.print(f"{mem.name} is not slept.", start=' ')
                if 'slience' in spelldef.attr and \
                   (mem.mspells or mem.pspells):
                    if random.randrange(100) < 50:
                        mem.silenced = True
                    if mem.silenced:
                        mw.print(f"{mem.name} is slept.", start=' ')
                    else:
                        mw.print(f"{mem.name} is not slept.", start=' ')

    def death_single(self, target, disptarget):
        mw = self.game.vscr.meswins[-1]
        if isinstance(target, Monster):
            regdeathp = self.game.mondef[target.name].regdeathp
        else:
            # vitality + luck
            regdeathp = (target.stat[3] + target.stat[5]) * 100//40
        if random.randrange(100) >= regdeathp:
            mw.print(f"{disptarget} is killed.", start=' ')
            target.hp = 0
            target.state = State.DEAD
            if isinstance(target, Member):
                target.rip += 1
        else:
            mw.print(f"{disptarget} is alive.", start=' ')

    def attack(self, invoker, spell, target):
        v = self.game.vscr
        mw = v.meswins[-1]
        spelldef = self.game.spelldef[spell]
        if not isinstance(invoker, Member):
            if spelldef.target == 'enemy':
                if spell == 'butsumetsu':
                    return
                targets = [mem for mem in self.game.party.members
                           if mem.state in [State.OK, State.ASLEEP]]
                mem = random.choice(targets)
                if spelldef.type == 'death':
                    self.death_single(mem, mem.name)
                else:
                    damage = dice(spelldef.value)
                    mw.print(
                        f"{mem.name} incurred {damage} damage.", start=' ')
                    v.disp_scrwin()
                    mem.hp = max(0, mem.hp - dice(spelldef.value))
                    if mem.hp <= 0 and \
                       mem.state not in [State.DEAD, State.ASHED, State.LOST]:
                        mem.state = State.DEAD
                        mem.rip += 1
                        mw.print(f"{mem.name} is killed.", start=' ')
            else:  # 'group' or 'all
                for mem in self.game.party.members:
                    if mem.state in [State.DEAD, State.ASHED, State.LOST]:
                        continue
                    if spelldef.type == 'death':
                        self.death_single(mem, mem.name)
                    else:
                        damage = dice(spelldef.value)
                        mw.print(
                            f"{mem.name} incurred {damage} damage.", start=' ')
                        mem.hp = max(0, mem.hp - dice(spelldef.value))
                        if mem.hp <= 0 and \
                           mem.state not in [State.DEAD, State.ASHED, State.LOST]:
                            mem.state = State.DEAD
                            mem.rip += 1
                            mw.print(f"{mem.name} is killed.", start=' ')
            return
        if spelldef.target == 'group':
            if target.identified:
                disptarget = target.name
            else:  # unidentified
                disptarget = self.game.mondef[target.name].unident
            if spell == 'shinoroi':  # lakanito
                for mon in target.monsters:
                    self.death_single(mon, disptarget)
            else:
                for mon in target.monsters:
                    self.attack_single(
                        mon, disptarget,
                        spelldef.value, spelldef.attr, target, invoker)
        elif spelldef.target == 'all':
            for mong in self.game.battle.monp:
                if mong.identified:
                    disptarget = mong.name
                else:
                    disptarget = self.game.mondef[mong.name].unident
                for mon in mong.monsters:
                    self.attack_single(mon, disptarget,
                                       spelldef.value, spelldef.attr, mong, invoker)
        elif spelldef.target == 'enemy':
            if target.identified:
                disptarget = target.name
            else:
                disptarget = self.game.mondef[target.name].unident
            if spelldef.type == 'death':
                self.death_single(target, disptarget)
            elif spell != 'butsumetsu' or \
                    self.game.mondef[target.name].type != 'undead':
                self.attack_single(target.monsters[0], disptarget,
                                   spelldef.value, spelldef.attr, target, invoker)
        monptmp = self.game.battle.monp[:]
        for mong in monptmp:
            mongtmp = mong.monsters[:]
            for mon in mongtmp:
                if mon.hp <= 0:
                    mong.monsters.remove(mon)
            if not mong.monsters:
                self.game.battle.monp.remove(mong)

    def attack_single(self, mon, dispname, value, attr, mong, invoker):
        if mon.state == State.DEAD:
            return
        v = self.game.vscr
        mw = v.meswins[-1]
        damage = dice(value)
        mondef = self.game.mondef[mon.name]
        if mondef.regspellp > random.randrange(100):
            mw.print(f"{dispname} registed.")
            return
        if 'fire' in attr:
            if mondef.regfire:
                damage = damage // 2
        elif 'cold' in attr:
            if mondef.regcold:
                damage = damage // 2
        if 'poison' in attr:
            if not mondef.regpoison and random.randrange(100) < 50:
                mon.poisoned = True
                mon.hpplus = -1
                mw.print(f"{dispname} was poisoned.", start=' ')
        mon.hp = max(mon.hp-damage, 0)
        mw.print(f"{dispname} incurred {damage} damage.", start=' ')
        if mon.hp <= 0:
            mw.print(f"{dispname} is killed.", start=' ')
            mon.state = State.DEAD
            self.game.battle.exp += mondef.exp
            invoker.marks += 1

    def heal(self, invoker, spell, target):
        sdef = self.game.spelldef[spell]
        if not isinstance(invoker, Member):
            if sdef.target == 'party':
                for mon in self.game.battle.monp[0].monsters:
                    self.heal_single(spell, sdef, mon)
            else:
                self.heal_single(spell, sdef, invoker)
            return
        if sdef.target == 'party':
            for target in self.game.party.members:
                self.heal_single(spell, sdef, target)
        else:
            self.heal_single(spell, sdef, target)

    def heal_single(self, sname, sdef, target):
        plus = dice(sdef.value)
        target.hp = min(target.hp+plus, target.maxhp)
        mw = self.game.vscr.meswins[-1]
        if target.hp == target.maxhp:
            mw.print(f"{target.name}'s HP was fully restored.", start=' ')
        else:
            mw.print(f"{plus} HP was restored to {target.name}.", start=' ')


class Dungeon:
    """
    Represents the dungeon
    """

    def __init__(self, game):
        self.game = game
        self.floors = []  # list of floor objects
        self.events = []  # list of events (floor, eventid)
        self.generate_events()

    def generate_events(self):
        """
        Generate important events when creating a dungeon.
        Later, events need to be placed on creating floors
        """
        # generate keys
        self.events.append((Evloctype.RANDOM, 3, Eventid.KEY))
        self.events.append((Evloctype.RANDOM, 6, Eventid.KEY))
        self.events.append((Evloctype.RANDOM, 9, Eventid.KEY))
        self.events.append((Evloctype.RANDOM, 10, Eventid.KEY))

        # generate bosses
        self.events.append((Evloctype.DOWNSTAIRS, 3, Eventid.BOSS))
        self.events.append((Evloctype.DOWNSTAIRS, 6, Eventid.BOSS))
        self.events.append((Evloctype.DOWNSTAIRS, 9, Eventid.BOSS))
        self.events.append((Evloctype.DOWNSTAIRS, 10, Eventid.BOSS))

    def generate_move_floors(self):
        """
        Check if floor_move, generate floors if not generated yet,
        and place party on the upstairs or the downstairs
        """
        party = self.game.party
        if not party.floor_move:
            return

        floor = party.floor
        if party.floor_move == 1:
            floor += 1
        elif party.floor_move == 3:
            floor = party.tsubasa_floor
        for idx in range(floor):
            if len(self.floors) < idx+1:
                floor_obj = self.generate_floor(idx+1)
                self.floors.append(floor_obj)

        if party.floor_move == 1:  # down; on the upstairs
            floor_obj = self.floors[party.floor]
            party.floor_obj = floor_obj
            party.move(floor_obj.rooms[0].center_x,
                       floor_obj.rooms[0].center_y,
                       floor=party.floor+1)
        elif party.floor_move == 2:  # 2: up; on the downstairs
            floor_obj = self.floors[party.floor-2]
            party.floor_obj = floor_obj
            party.move(floor_obj.rooms[-1].center_x,
                       floor_obj.rooms[-1].center_y,
                       floor=party.floor-1)
        else:  # tsubasa; on the upstairs
            floor_obj = self.floors[party.tsubasa_floor-1]
            party.floor_obj = floor_obj
            party.move(floor_obj.rooms[0].center_x,
                       floor_obj.rooms[0].center_y,
                       floor=party.tsubasa_floor)
        party.floor_move = 0

        for m in party.members:
            m.deepest = max(m.deepest, party.floor)

    def generate_floor(self, floor):
        """
        Generate a dungeon floor.
        Create rooms, connect among them and place doors
        """
        floor_x_size = min(256, 48 + 24*floor)
        floor_y_size = min(128, 20 + 10*floor)
        floor_data = bytearray(b'#' * floor_x_size *
                               floor_y_size)  # rock only floor
        floor_obj = Floor(floor_x_size, floor_y_size, floor, floor_data)

        rooms = floor_obj.prepare_rooms()
        for r in rooms:
            for y in range(r.y_size):
                start = (r.y + y)*floor_x_size + r.x
                floor_obj.floor_view[start:start+r.x_size] = b'.'*r.x_size
        floor_obj.connect_all_rooms(rooms)
        floor_obj.place_doors(self.game, rooms)
        floor_obj.rooms = rooms
        floor_obj.floor_orig = floor_obj.floor_data
        floor_obj.place_events(self)
        floor_obj.floor_data = bytearray(b'^' * floor_x_size * floor_y_size)
        return floor_obj

    def check_move_floor(self, floor_obj):
        """
        Check if move to upper/lower floor.
        Return True if exit, False not.
        """
        game = self.game
        party = game.party
        vscr = game.vscr
        meswin = vscr.meswins[0]

        if floor_obj.get_tile(party.x, party.y) == b'<':  # upstairs
            vscr.disp_scrwin(floor_obj)
            if party.floor == 1:
                c = meswin.input_char("Exit from dungeon? (y/n)",
                                      values=['y', 'n'])
            else:
                c = meswin.input_char(
                    "Stairs.  Go up? (y/n)", values=['y', 'n'])
            if c == 'y':
                party.floor_move = 2  # go up
        elif floor_obj.get_tile(party.x, party.y) == b'>':  # downstairs
            vscr.disp_scrwin(floor_obj)
            c = meswin.input_char(
                "Stairs.  Go down? (y/n)", values=['y', 'n'])
            if c == 'y':
                party.floor_move = 1  # go down

        if party.floor_move:
            if party.floor <= 1 and party.floor_move == 2:  # exit from dungeon
                meswin.cls()
                party.place = Place.EDGE_OF_TOWN
                return True  # Exit from dungeon

        return False


class Floor:
    # Represents a floor in the dungeon
    def __init__(self, x_size, y_size, floor, floor_data):
        self.x_size = x_size
        self.y_size = y_size
        self.floor = floor
        self.floor_data = floor_data
        self.floor_view = memoryview(floor_data)
        self.battled = []
        self.rooms = None
        self.up_x = self.up_y = 0
        self.down_x = self.down_y = 0
        self.events = {}  # event list. key is (x, y), value is [eventID, done]

    def __repr__(self):
        s = self.floor_data.decode()
        return f"Floor(size: {self.x_size}x{self.y_size}, floor: {self.floor} - {s})"

    def ending(self, game):
        """
        Show ending messages
        """
        v = game.vscr
        v.cls()
        mw = v.meswins[-1]
        mw.print("Although defeated, the demonic figure looks intact.")
        mw.print("He talked in a calm voice.")
        v.disp_scrwin()
        getch(wait=True)
        mw.print(
            "'Good.  You are exceptionally good soldiers.  I am impressed.'",
            start=' ')
        v.disp_scrwin()
        getch(wait=True)
        mw.print(
            "'You earthlings have defeated a self of mine.  It was a good battle.'",
            start=' ')
        v.disp_scrwin()
        getch(wait=True)
        mw.print(
            "'You have just broken the self of order.  Now, chaos has been brought to your world.  Ancient gods and daemomns are released.  You will see all kinds of plagues and disasters.'",
            start=' ')
        v.disp_scrwin()
        getch(wait=True)
        mw.print(
            "'To prevent it from happening, you will need to go further deep.  Look for those gods and daemons, and defeat them.'",
            start=' ')
        v.disp_scrwin()
        getch(wait=True)
        mw.print(
            "'But, they are immortals.  You can not just kill them.  You need to defeat them again and again.'",
            start=' ')
        v.disp_scrwin()
        getch(wait=True)
        mw.print(
            "'I will also wait for you again.  Meet me at further deep down.  My other selves want to have fun, too.'",
            start=' ')
        v.disp_scrwin()
        getch(wait=True)
        mw.print(
            "The demonic figure fell slient.  And before your eyes, he started to become transparent, and disappeared in the air.")
        v.disp_scrwin()
        getch(wait=True)
        mw.print(
            "You just knew that you have changed something important in a non-reversal way.")
        v.disp_scrwin()
        getch(wait=True)

    def boss(self, game):
        v = game.vscr
        mw = Meswin(v, v.width//8, v.height//6,
                    v.width*3//4, 4, frame=True)
        v.meswins.append(mw)
        if game.party.floor == 3:
            mw.print("You saw a small child standing on downstairs.")
            v.disp_scrwin()
            getch(wait=True)
            mw.print("Suddenly, he srated running toward you.")
            v.disp_scrwin()
            getch(wait=True)
        elif game.party.floor == 6:
            mw.print(
                "You see a skinny woman wearing a chic black dress, as if she is going to a dinner party.")
            v.disp_scrwin()
            getch(wait=True)
            mw.print("You thought you know her.  She smiled at you.")
            v.disp_scrwin()
            getch(wait=True)
        elif game.party.floor == 9:
            mw.print("In this high-ceiling room is a huge blue giant.")
            v.disp_scrwin()
            getch(wait=True)
            mw.print(
                "You can't see his face, but it's evident that he is excited to see new preys.")
            v.disp_scrwin()
            getch(wait=True)
        elif game.party.floor == 10:
            mw.print("'Welcome.' The demonic figure said.")
            mw.print("'It has been long since I last met earthlings like you.'")
            v.disp_scrwin()
            getch(wait=True)
            mw.print("He looks to be enjoying this encounter.")
            v.disp_scrwin()
            getch(wait=True)
        game.vscr.meswins[-2].print("*** boss battle ***")
        game.battle.boss = True
        game.battle.battle()
        game.battle.boss = False
        if not game.battle.treasure or \
           not game.party.members:  # lost the battle
            v.meswins.pop()
            return
        game.chest.chest()
        if game.party.defeated():
            v.meswins.pop()
            return
        survnum = sum(1 for m in game.party.members
                      if m.state in [State.OK, State.ASLEEP,
                                     State.PARALYZED, State.STONED])
        mw.print(f"Each survivor gets {game.battle.exp//survnum} e.p.",
                 start=' ')
        mw.print(f"Each survivor gets {game.battle.gold//survnum} gold.",
                 start=' ')
        v.disp_scrwin()
        for mem in game.party.members:
            if mem.state == State.ASLEEP:
                mem.state = State.OK
            if mem.state in [State.OK, State.PARALYZED, State.STONED]:
                mem.exp += game.battle.exp//survnum
                mem.gold += game.battle.gold//survnum
        getch(wait=True)
        mw.cls()
        if game.party.floor == 10:  # The last boss?
            self.ending(game)
        else:
            mw.print("You won the battle, but it was no ordinary monster.")
        mw.print("You see downstairs appearing in front of you.")
        v.disp_scrwin()
        getch(wait=True)
        v.meswins.pop()

    def key(self, game):
        if game.party.floor == 3:
            key = 'ivory'
            keys = ['ivory ley', 'bronze key', 'silver key', 'gold key']
        elif game.party.floor == 6:
            key = 'bronze'
            keys = ['bronze key', 'silver key', 'gold key']
        elif game.party.floor == 9:
            key = 'silver'
            keys = ['silver key', 'gold key']
        elif game.party.floor == 10:
            key = 'gold'
            keys = ['gold key']
        elif game.party.floor >= 11:
            key = 'one time password'
            keys = [key]
        if not game.party.have_items(keys):
            v = game.vscr
            mw = Meswin(v, v.width//8, v.height//6,
                        v.width*3//4, 8, frame=True)
            v.meswins.append(mw)
            mw.print(f"You see a {key} statue on a small stone table.")
            mw.print(f"The {key} statue is intricate and lively.")
            mw.print(f"You thought you need to touch the statue.")
            if mw.input_char("Search? (y/n)") == 'y':
                game.chest.get_item(key+' key')
            v.meswins.pop()
            v.disp_scrwin()

    def random_message(self, game):
        v = game.vscr
        mw = Meswin(v, v.width//8, v.height//6,
                    v.width*3//4, 8, frame=True)
        v.meswins.append(mw)
        messages = random.choice(random_messages)
        for i, message in enumerate(messages):
            if i == 0:
                mw.print(message)
                v.disp_scrwin()
            else:
                getch(wait=True)
                mw.print(message, start=' ')
                v.disp_scrwin()
        mw.print(" - press space bar")
        v.disp_scrwin()
        while True:
            if getch(wait=True) == ' ':
                break
        v.meswins.pop()
        v.disp_scrwin()

    def check_event(self, game):
        """
        Check and process an event.
        Return True if processed an event.
        """
        x = game.party.x
        y = game.party.y
        if (x, y) not in self.events or self.events[(x, y)][1]:
            return False
        evid = self.events[(x, y)][0]
        if evid == Eventid.RNDMSG:
            self.random_message(game)
            self.events[(x, y)][1] = True  # processed
            return True
        elif evid == Eventid.KEY:
            self.key(game)
        elif evid == Eventid.BOSS:
            self.boss(game)
            if game.party.members and not game.battle.ran:
                self.events[(x, y)][1] = True  # processed
                return True
        return False  # Will see the event again

    def place_events(self, dungeon):
        """
        Place events on random or specific type location
        """
        for ev in dungeon.events:
            if ev[1] != self.floor:  # event[1] is floor
                continue
            if ev[0] == Evloctype.RANDOM:
                while True:
                    x = random.randrange(self.x_size)
                    y = random.randrange(self.y_size)
                    if self.get_tile(x, y) == b'.':  # floor tile
                        break
                self.put_tile(x, y, b',')
                self.events[(x, y)] = [ev[2], False]  # event[2] is eventid
            elif ev[0] == Evloctype.DOWNSTAIRS:
                x = self.rooms[-1].center_x
                y = self.rooms[-1].center_y
                self.events[(x, y)] = [ev[2], False]  # eventid

        if self.floor >= 11:
            while True:
                x = random.randrange(self.x_size)
                y = random.randrange(self.y_size)
                if self.get_tile(x, y) == b'.':  # floor tile
                    break
            self.put_tile(x, y, b',')
            self.events[(x, y)] = [Eventid.KEY, False]

        # place random messages
        for _ in range(2 + random.randrange(3)):  # 2 to 4 messages
            while True:
                x = random.randrange(self.x_size)
                y = random.randrange(self.y_size)
                if self.get_tile(x, y) == b'.':  # floor tile
                    break
            self.put_tile(x, y, b',')
            self.events[(x, y)] = [Eventid.RNDMSG, False]

    def get_tile(self, x, y):
        """
        Return the byte character representing the tile on
        the specified (x, y) location
        """
        if x >= self.x_size or x < 0:
            return b'^'
        if y >= self.y_size or y < 0:
            return b'^'
        pos = y * self.x_size + x
        return self.floor_orig[pos:pos+1]

    def put_tile(self, x, y, bc, orig=True):
        """
        Place the tile byte character to (x, y) location.
        If orig flag is False, place it on the virtual map
        """
        if 0 <= x < self.x_size and 0 <= y < self.y_size:
            pos = y * self.x_size + x
            if orig:
                self.floor_orig[pos:pos+1] = bc
            else:
                self.floor_data[pos:pos+1] = bc

    def can_move(self, x, y):
        """
        Utility function to check if they can move to
        (x, y).
        """
        bc = self.get_tile(x, y)
        if bc in b"*+%#^":
            return False
        return True

    def open_door(self, game, mw):
        """
        Open a door.  If it's a locked door ('*'), unlock and
        open it.  Unlock could fail.
        """
        x = game.party.x
        y = game.party.y
        c = mw.input_char("Which direction? - ;)leave",
                          values=['h', 'j', 'k', 'l', ';'])
        if c == ';':
            return
        elif c == 'h':
            x -= 1
        elif c == 'l':
            x += 1
        elif c == 'j':
            y += 1
        elif c == 'k':
            y -= 1
        tile = self.get_tile(x, y)
        if tile == b'+':
            mw.print("Opened.")
            self.put_tile(x, y, b'.')
        elif tile == b'*':
            if game.party.can_open(game):
                mw.print("Unlocked.")
                self.put_tile(x, y, b'.')
            else:
                mw.print("No luck.")
        elif tile == b'%':
            if game.party.can_open(game, ch=b'%'):
                mw.print("Unlocked.")
                self.put_tile(x, y, b'.')
                if game.party.floor >= 11:
                    game.party.consume_item('one time password')
            else:
                mw.print("You need the key.")
        else:
            mw.print("Not a door.")

    def draw_line(self, x1, y1, x2, y2):
        """
        Utility generator function to draw a straight line.
        Must eithr be vertical (x1==x2) or horizontal (y1==y2).
        """
        if x1 < x2:
            x1, x2 = x2, x1
        if y1 < y2:
            y1, y2 = y2, y1
        while x1 > x2 or y1 > y2:
            yield x2, y2
            if x1 > x2:
                x2 += 1
            if y1 > y2:
                y2 += 1
        yield x2, y2

    def connect_rooms(self, r1, r2):
        """
        Create a hallway between two rooms and connect them.
        """
        if random.randrange(2) == 0:  # 1/2
            cx = r1.center_x
            cy = r2.center_y
        else:
            cx = r2.center_x
            cy = r1.center_y
        for x, y in self.draw_line(r1.center_x, r1.center_y, cx, cy):
            pos = self.x_size * y + x
            self.floor_view[pos:pos+1] = b'.'
        for x, y in self.draw_line(r2.center_x, r2.center_y, cx, cy):
            pos = self.x_size * y + x
            self.floor_view[pos:pos+1] = b'.'

    def prepare_rooms(self):
        """
        Return a list filled with Rooms objects on a floor.
        """
        rooms = []
        for _ in range(1024):
            rx = 3 + random.randrange(10)
            ry = 3 + random.randrange(4)
            room = Room(random.randrange(self.x_size-rx+1),
                        random.randrange(self.y_size-ry+1),
                        rx, ry)
            intersect = False
            for r in rooms:
                if room.rooms_intersect(r):
                    intersect = True
                    break
            if not intersect:
                rooms.append(room)
                self.battled.append(False)
        return rooms

    def connect_all_rooms(self, rooms):
        """
        Connect all rooms with hallways.
        Try to find and connect with the nearest room.
        """
        rooms.sort(key=lambda room: room.y+room.y_size//2)
        rooms.sort(key=lambda room: room.x+room.x_size//2)
        rs = rooms[:]
        r_src = rs.pop()
        newrooms = [r_src]
        while rs:
            idx_near = 0
            len_rs = len(rs)
            for i in range(len_rs):  # look for the nearest room
                if r_src.distsq_rooms(rs[i]) < r_src.distsq_rooms(rs[idx_near]):
                    idx_near = i
            r_near = rs.pop(idx_near)
            self.connect_rooms(r_src, r_near)
            r_src = r_near
            newrooms.append(r_src)
        rooms = newrooms

    def place_door(self, x, y, dc):
        """
        Utility function to check and place a door
        """
        if 0 <= x < self.x_size and 0 <= y < self.y_size:
            pos = y*self.x_size + x
            c = self.floor_view[pos:pos+1]
            if c == b'.' or c == b'+':
                self.floor_view[pos:pos+1] = dc

    def place_doors(self, game, rooms):
        """
        Place locked or unlocked doors in front of rooms.
        """
        for r in rooms:
            dc = b'+'  # door character
            if random.randrange(10) == 0:  # 10%
                dc = b'*'  # locked door
            if (self.floor in [3, 6, 9, 10] or self.floor >= 11) \
               and r is rooms[-1]:
                dc = b'%'  # special locked door that requires a key
            for x in range(r.x_size):  # top and bottom edges
                self.place_door(r.x+x, r.y-1, dc)
                self.place_door(r.x+x, r.y+r.y_size, dc)

            for y in range(r.y_size):  # left and right edges
                self.place_door(r.x-1, r.y+y, dc)
                self.place_door(r.x+r.x_size, r.y+y, dc)

            if r == rooms[0]:
                pos = r.center_y*self.x_size + r.center_x
                self.floor_view[pos:pos+1] = b'<'  # up stair
                self.up_x = r.center_x
                self.up_y = r.center_y

            if r == rooms[-1]:
                pos = r.center_y*self.x_size + r.center_x
                self.floor_view[pos:pos+1] = b'>'  # down stair
                self.down_x = r.center_x
                self.down_y = r.center_y


class Room:
    # Represents a room on a dungeon floor
    def __init__(self, x, y, x_size, y_size):
        self.x = x
        self.y = y
        self.x_size = x_size
        self.y_size = y_size
        self.center_x = x + x_size//2
        self.center_y = y + y_size//2

    def __repr__(self):
        return f"Room(x/y: {self.x}/{self.y}, size: {self.x_size}/{self.y_size})"

    def in_room(self, x, y):
        """
        Return if (x, y) is in the room
        """
        if self.x <= x < self.x+self.x_size:
            if self.y <= y < self.y+self.y_size:
                return True
        return False

    def rooms_intersect(self, r):
        """
        Return True if two rooms are intersected.
        """
        return max(self.x, r.x) <= min(self.x+self.x_size, r.x+r.x_size) \
            and max(self.y, r.y) <= min(self.y+self.y_size, r.y+r.y_size)

    def distsq_rooms(self, r):
        """
        Calculate distance between two rooms.
        Will return distance**2.
        """
        return (self.x+self.x_size//2 - (r.x+r.x_size//2))**2 \
            + (self.y+self.y_size//2 - (r.y+r.y_size//2))**2


class Monster:
    """
    Represents a monster
    """

    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.mdef = self.game.mondef[name]
        self.hp = self.maxhp = dice(self.mdef.hp)
        self.hpplus = 0
        self.ac = self.mdef.ac
        self.state = State.OK
        self.silenced = False
        self.poisoned = False


class Monstergrp:
    """
    Represents a monster group
    """

    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.mdef = self.game.mondef[name]
        self.monsters = []
        self.identified = False


class Battle:
    """
    Represents battles
    """

    def __init__(self, game):
        self.game = game
        self.boss = False
        self.ran = False  # ran from the battle flag
        v = game.vscr
        self.mw = Meswin(v, v.width//8, v.height//8+4,
                         v.width*3//4, 10, frame=True)
        self.ew = Meswin(v, v.width//8, v.height//8-1,
                         v.width*3//4, 4, frame=True)

    def new_battle(self):
        """
        Clear variables for a new battle
        """
        self.friendly = False
        self.exp = 0  # gained exp from this battle
        self.gold = 0  # gained gold from this battle
        self.room_index = -1  # random encounter
        self.monp = []  # includes monster group(s)
        self.entities = []  # includes party member or monster
        self.treasure = True  # treasure
        self.game.party.alarm = False  # alarm flag
        if random.randrange(100) < 10:
            self.surprised = 1  # you surprised the monsters
        elif random.randrange(100) < 10:
            self.surprised = 2  # monsters surprised you
        else:
            self.surprised = 0
        self.ran = False  # ran flag
        for m in self.game.party.members:
            m.action = '????????????'
            m.drained = False
            m.acplus = 0
            m.silenced = False

    def draw_ew(self):
        """
        draw enemy window that lists the monster groups and number
        of monsters in them
        """
        self.ew.cls()
        for i, mg in enumerate(self.monp, 1):
            active = 0
            if self.friendly or self.game.party.identify:
                mg.identified = True
            if mg.identified:
                dispname = mg.name
                if len(mg.monsters) > 1:
                    dispname = mg.mdef.names
            else:
                dispname = mg.mdef.unident
                if len(mg.monsters) > 1:
                    dispname = mg.mdef.unidents
            for m in mg.monsters:
                if m.state in [State.OK]:
                    active += 1
            self.ew.print(
                f"{i}) {len(mg.monsters)} {dispname.ljust(24)} ({active})", start=' ')

    def create_monsterparty(self):
        """
        Create a monster party and save it to self.monp
        """
        if self.boss:
            bosses = {
                3: 'daemon kid',
                6: 'the lady',
                9: 'atlas',
                10: 'daemon lord',
            }
            mname = bosses[self.game.party.floor]
        else:
            candidates = []
            for mname in self.game.mondef:
                if self.game.party.floor <= 10:
                    if self.game.party.floor in self.game.mondef[mname].floors:
                        candidates.append(mname)
                else:
                    if 0 in self.game.mondef[mname].floors:
                        candidates.append(mname)
            while True:
                mname = random.choice(candidates)
                # Hidden monsters shouldn't appear too often
                if mname not in ['Nobunaga', 'Shenlong'] or \
                   random.randrange(10) == 0:  # 1/10
                    break
        if mname == '':
            breakpoint()  # +++++++++++++++++++++
        self.friendly = False
        while len(self.monp) < 4:  # up to 4 groups
            mdef = self.game.mondef[mname]
            if len(self.monp) == 0:  # 1st group
                if mdef.friendly and random.randrange(100) < 10:  # 1/10
                    self.friendly = True

            mong = Monstergrp(self.game, mname)
            self.monp.append(mong)
            for _ in range(dice(mdef.number)):
                mon = Monster(self.game, mname)
                mong.monsters.append(mon)
                self.gold += mdef.level * (random.randrange(15) + 10)
            if mdef.fellowp <= random.randrange(100):
                break
            mname = mdef.fellow
        # top monster defines treasure levels
        self.game.chest.items = self.monp[0].mdef.treasure
        return

    def canrun(self, entity):
        """
        Return True if party was able to run away from the battle
        """
        if isinstance(entity, Monster):
            if 65 > random.randrange(100):
                return True
            else:
                return False
        success = pl = el = 0
        for mg in self.monp:
            for m in mg.monsters:
                if m.state == State.OK:
                    el += self.game.mondef[m.name].level
        for mem in self.game.party.members:
            if mem.state == State.OK:
                pl += mem.level
        if pl > el:
            success += 20

        if len(self.game.party.members) == 1:
            success += 15
        elif len(self.game.party.members) == 2:
            success += 10
        elif len(self.game.party.members) == 3:
            success += 5

        if success + 75 > random.randrange(100):
            return True
        else:
            return False

    def handle_friendly(self, place):
        """
        Handle friendly monsters.
        Return True if leave, False if fight
        """
        v = self.game.vscr
        if len(self.monp) > 1:
            dispname = 'monsters'
        else:
            mong = self.monp[0]
            if mong.identified:
                dispname = mong.name
                if len(mong.monsters) > 1:
                    dispname = mong.mdef.names
            else:
                dispname = mong.mdef.unident
                if len(mong.monsters) > 1:
                    dispname = mong.mdef.unidents
        if self.friendly:
            self.surprised = 0
            self.mw.print(f"You encountered friendly {dispname}.")
            c = self.mw.input_char("Leave? (y/n)", values=['y', 'n'])
            if c == 'y':
                idx = self.room_index
                if idx >= 0:  # room encounter
                    self.game.party.floor_obj.battled[idx] = True
                return True
        else:
            self.mw.print(f"You encountered {dispname}.")
        return False

    def enemy_action(self):
        """
        Decide enemy/monster actions
        """
        if self.surprised == 1:  # you surprised the monsters
            return
        mondef = self.game.mondef
        party = self.game.party
        for mong in self.monp:
            for mon in mong.monsters:
                if mon.state != State.OK:
                    continue
                action = mondef[mong.name].act[random.randrange(5)]
                agi = mondef[mong.name].agi + random.randrange(4)
                if action == 'run':
                    self.entities.append(
                        Entity(mon, mong.name, mong, agi, 'run', None))
                elif action == 'breath':
                    self.entities.append(
                        Entity(mon, mong.name, mong, agi, 'breath', None))
                elif action == 'atk' or self.surprised == 2:
                    targets = [mem for mem in party.members
                               if mem.state in [State.OK, State.ASLEEP]]
                    if len(targets) > 3:
                        if party.floor > 3 and random.randrange(100) < 25:
                            target = random.choice(targets)
                        else:
                            target = targets[random.randrange(3)]
                    else:
                        target = random.choice(targets)
                    self.entities.append(
                        Entity(mon, mong.name, mong, agi, 'fight', target))
                elif action == 'help':
                    self.entities.append(
                        Entity(mon, mong.name, mong, agi, action, None))
                else:
                    if action in self.game.spelldef:
                        self.entities.append(
                            Entity(mon, mong.name, mong, agi, action, None))
                    else:
                        self.entities.append(
                            Entity(mon, mong.name, mong, agi, 'parry', None))

    def input_action(self):
        """
        Input party member actions
        return True if ran successfully
        """
        self.entities = []
        for mem in self.game.party.members:
            mem.action = '????????????'
        if self.surprised == 2:  # monsters surprised you
            return False
        while True:
            self.mw.print(f"Options - f)ight s)pell u)se")
            self.mw.print(f"d)ispell p)arry r)un t)ake back", start=' ')
            for idx, mem in enumerate(self.game.party.members, 1):
                if mem.state not in [State.OK]:
                    continue
                while True:
                    c = self.mw.input_char(f"{mem.name}'s action?",
                                           values=['f', 's', 'u', 'p', 'r', 't', 'd'])
                    agi = mem.stat[4] + random.randrange(5)
                    if c == 'r':
                        if self.canrun(mem):
                            return True
                        else:
                            return False  # failed
                    elif c == 't':
                        self.entities = []
                        for mem in self.game.party.members:
                            mem.action = '????????????'
                        self.mw.print("..taking back")
                        self.game.vscr.disp_scrwin()
                        break
                    elif c == 'p':
                        mem.action = 'parry'
                        self.entities.append(
                            Entity(mem, mem.name, None, agi, 'parry', None))
                        self.game.vscr.disp_scrwin()
                        break
                    elif c == 'f':
                        wrange = 'short'
                        for item in mem.items:
                            idef = self.game.itemdef[item[0]]
                            if item[1] and idef.type.lower() == 'weapon' \
                               and idef.range.lower() == 'long':
                                wrange = 'long'
                        if idx > 3 and wrange == 'short':
                            self.mw.print("Weapon range too short.")
                            self.game.vscr.disp_scrwin()
                            continue
                        mong = self.monp[self.choose_group()]
                        self.entities.append(
                            Entity(mem, mem.name, None, agi, 'fight', mong))
                        mem.action = 'fight'
                        self.game.vscr.disp_scrwin()
                        break
                    elif c == 'd':
                        if mem.job not in [Job.PRIEST, Job.BISHOP, Job.LORD]:
                            continue
                        mong = self.monp[self.choose_group()]
                        self.entities.append(
                            Entity(mem, mem.name, None, agi, 'dispell', mong))
                        mem.action = 'dispell'
                        self.game.vscr.disp_scrwin()
                        break
                    elif c == 's':
                        if self.surprised == 1:  # you surprised the monsters
                            continue
                        s, target = self.choose_spell(mem)
                        self.entities.append(
                            Entity(mem, mem.name, None, agi, s, target))
                        mem.action = s
                        self.game.vscr.disp_scrwin()
                        break
                    elif c == 'u':
                        item, target = self.choose_item(mem)
                        if not item:
                            continue
                        self.entities.append(
                            Entity(mem, mem.name, None, agi, item, target))
                        mem.action = item
                        self.game.vscr.disp_scrwin()
                        break
                if c == 't':
                    break
            if c != 't':
                self.mw.print("Press any key or t)ake back >")
                self.game.vscr.disp_scrwin()
                c = getch(wait=True)
                if c == 't':
                    self.entities = []
                    for mem in self.game.party.members:
                        mem.action = '????????????'
                    continue
                break

    def choose_group(self):
        """
        choose monster group and return group #
        """
        if len(self.monp) == 1:
            return 0
        while True:
            self.mw.print(f"Which group? (#)")
            self.game.vscr.disp_scrwin()
            n = getch(wait=True)
            try:
                n = int(n)
            except:
                continue
            if n > len(self.monp):
                continue
            return n-1

    def choose_spell(self, mem):
        """
        Choose spell to cast and the target monster group or the party member
        """
        mw = self.mw
        s = mw.input("What spell to cast?")
        s = s.lower()
        if s not in self.game.spelldef:  # No such spell
            return s, None
        elif s not in list(itertools.chain(mem.mspells, mem.pspells)):
            return s, None  # not mastered yet
        sdef = self.game.spelldef[s]
        if sdef.target == 'enemy' or sdef.target == 'group':
            target = self.monp[self.choose_group()]
        elif sdef.target == 'member':
            while True:
                ch = mw.input_char(f"To who? (#)")
                try:
                    if 0 <= (chid := int(ch)-1) < len(self.game.party.members):
                        break
                except:
                    pass
            target = self.game.party.members[chid]
        else:
            target = None
        return s, target

    def choose_item(self, mem):
        """
        Choose item to use.  If the item has spell power and the
        spell needs target to choose, have player specify target.
        """
        mw = self.mw
        mw.print("Which item to use?")
        for i, item in enumerate(mem.items, 1):
            if item[3]:
                dispitem = ''.join(['?', self.game.itemdef[item[0]].unident])
            else:
                dispitem = item[0]
            mw.print(f"{i}) {dispitem}")
        idx = mw.input_char("Item # or l)eave",
                            values=['1', '2', '3', '4', '5', '6', '7', '8', 'l'])
        if idx == 'l':
            return False, None
        idef = mem.items[int(idx)-1]
        if idef[3]:
            iname = ''.join(['?', self.game.itemdef[idef[0]].unident])
        else:
            iname = idef[0]
        spell = self.game.itemdef[idef[0]].use
        if spell != '' and spell in self.game.spelldef and \
           iname == idef[0]:
            target = self.game.spelldef[spell].target
            if target == 'member':
                m = self.game.party.choose_character(self.game)
                if not m:
                    return False, None
                return iname, m
            elif target in ['group', 'enemy']:
                mong = self.monp[self.choose_group()]
                return iname, mong
        return iname, None

    def monster_attack(self, e):
        """
        Monster attacks a member
        """
        mdef = self.game.mondef[e.name]
        if e.group.identified:
            dispname = e.name
        else:
            dispname = mdef.unident
        if mdef.type in ['animal', 'undead', 'dragon', 'insect']:
            verb = random.choice(['tears', 'rips', 'gnaws', 'bites', 'claws'])
        else:
            verb = random.choice(
                ['swings', 'thrusts', 'stabs', 'slashes', 'chops'])
        if e.target.state in [State.DEAD, State.ASHED, State.LOST]:
            self.mw.print(f"{e.name} lost its target.")
            return

        apoint = 19
        if e.target.action == 'parry':
            apoint += 2
        apoint -= self.game.mondef[e.name].level + 2
        bpoint = apoint - e.target.ac - e.target.acplus - self.game.party.ac

        if bpoint >= 19:
            val = 19
        elif 0 <= bpoint < 19:
            val = bpoint
        elif -36 <= bpoint < 0:
            val = 0
        else:
            if apoint < 0:
                val = 0
            else:
                val = 19
        hitp = (19 - val)*100//20  # hit percent

        hitcnt = 0
        damage = 0
        for _ in range(self.game.mondef[e.name].count):
            if hitp > random.randrange(100):
                hitcnt += 1
                damage += dice(self.game.mondef[e.name].attack)
        e.target.hp -= damage
        if e.target.state != State.OK:
            e.target.hp -= damage  # twice the damage if not status OK
        self.mw.print(f"{dispname} {verb} at {e.target.name}.")
        self.mw.print(f"{e.target.name} incurred {damage} damage.", start=' ')
        self.game.vscr.disp_scrwin()
        if e.target.hp <= 0:
            e.target.hp = 0
            e.target.state = State.DEAD
            e.target.rip += 1
            self.mw.print(f"{e.target.name} is killed.", start=' ')
            return
        if hitcnt == 0:
            return

        regist = set()
        for item in e.target.items:
            if item[1]:  # equipped
                regist |= set(self.game.itemdef[item[0]].regist)

        if self.game.mondef[e.name].poison:
            if (e.target.stat[5]+1)*100//20 < random.randrange(100):
                if 'poison' not in regist and not e.target.poisoned:
                    e.target.poisoned = True
                    e.target.hpplus -= 1
                    self.mw.print(f"{e.target.name} is poisoned.")

        if self.game.mondef[e.name].paraly:
            if (e.target.stat[5]+1)*100//20 < random.randrange(100):
                if 'paraly' not in regist:
                    e.target.state = State.PARALYZED
                    self.mw.print(f"{e.target.name} is paralyzed.")

        if self.game.mondef[e.name].stone:
            if (e.target.stat[5]+1)*100//20 < random.randrange(100):
                if 'stone' not in regist:
                    e.target.state = State.STONED
                    self.mw.print(f"{e.target.name} is petrified.")

        if not e.target.drained and self.game.mondef[e.name].drain > 0:
            if (e.target.stat[5]+1)*100//20 < random.randrange(100):
                if 'drain' not in regist:
                    prevlevel = e.target.level
                    e.target.level -= self.game.mondef[e.name].drain
                    if e.target.level-1 < 13:
                        e.target.exp = level_table[e.target.job][e.target.level-2]
                    else:
                        e.target.exp = level_table[e.target.job][11] +\
                            level_table[e.target.job][12]*(e.target.level-13)
                    if e.target.level < 13:
                        e.target.nextexp = level_table[e.target.job][e.target.level-1]
                    else:
                        e.target.nextexp = level_table[e.target.job][11] +\
                            level_table[e.target.job][12]*(e.target.level-12)
                    self.mw.print(
                        f"{e.target.name} is drained by {self.game.mondef[e.name].drain} level.")
                    if e.target.level < 1:
                        e.target.hp = 0
                        e.target.state = State.LOST
                        self.mw.print(f"{e.target.name} is lost.")
                        return
                    e.target.maxhp = \
                        e.target.maxhp * \
                        (prevlevel - self.game.mondef[e.name].drain) \
                        // prevlevel
                    if e.target.hp > e.target.maxhp:
                        e.target.hp = e.target.maxhp
                    e.target.drained = True

        if self.game.mondef[e.name].critical:
            if (e.target.stat[5]+1)*100//20 < random.randrange(100):
                if 'critical' not in regist:
                    if (49 - self.game.mondef[e.name].level) * 100 / 50 \
                       < random.randrange(100):
                        e.target.state = State.DEAD
                        e.target.hp = 0
                        e.target.rip += 1
                        self.mw.print(f"{e.target.name} is decapitated.")

    def dispell(self, e):
        """
        Party member dispells a monster group
        """
        mondef = self.game.mondef[e.target.name]
        if e.target.identified:
            dispname = e.target.name
        else:
            dispname = mondef.unident
        self.mw.print(f"{e.name} tried to dispell.")
        if mondef.type != 'undead':
            self.mw.print("Not undead.", start=' ')
            return
        dspl_power = e.entity.level * 5 + 50
        dspl_regist = 10 * mondef.level
        if dspl_power > 255:
            chance = 100
        else:
            chance = max(5, dspl_power - dspl_regist)
        target_cp = e.target.monsters[:]
        for mon in target_cp:
            if random.randrange(100) < chance:
                mon.state = State.DEAD
                mon.hp = 0
                self.mw.print(f"{dispname} is dispelled.", start=' ')
                e.target.monsters.remove(mon)
                if not e.target.monsters:
                    self.game.battle.monp.remove(e.target)
            else:
                self.mw.print(f"{dispname} registed to dispell.", start=' ')

    def member_attack(self, e):
        """
        Party member attacks a monster
        """
        if e.entity.job in [Job.MAGE, Job.THIEF, Job.BISHOP]:
            lvbonus = e.entity.level // 5
        else:
            lvbonus = e.entity.level // 3 + 2
        strbonus = 0
        if e.entity.stat[0] >= 16:
            strbonus = e.entity.stat[0] - 15
        elif e.entity.stat[0] < 6:
            strbonus = e.entity.stat[0] - 6
        st_bonus = weapat = 0
        weapon = None
        for item in e.entity.items:
            if item[1]:  # equpped?
                # (check align)
                itemdef = self.game.itemdef[item[0]]
                if not itemdef.align or e.entity.align in itemdef.align:
                    st_bonus += itemdef.st
                else:
                    st_bonus = -1
                if itemdef.type.lower() == 'weapon':
                    weapon = itemdef  # for later use
                    weapat = weapon.at
        hitability = lvbonus + strbonus + st_bonus
        for idx, g in enumerate(self.monp):
            if g == e.entity:
                break
        hitpercent = (self.game.mondef[e.target.name].ac
                      - idx + hitability) * 100 // 20

        if e.entity.job == Job.NINJA:
            atkcnt = max(e.entity.level//5+2, weapat)
        elif e.entity.job in [Job.FIGHTER, Job.SAMURAI, Job.LORD]:
            atkcnt = max(e.entity.level//5+1, weapat)
        else:
            atkcnt = max(e.entity.level//10+1, weapat)
        if atkcnt > 10 and not e.entity.have_item('kaiden book', equip=True):
            atkcnt = 10

        damage = hitcnt = 0
        for _ in range(atkcnt):
            if hitpercent > random.randrange(100):
                if weapon is None:
                    damage += dice('2D2')  # w/o weapon
                else:
                    # twice the damage depending on monster type
                    if self.game.mondef[e.target.name].type in weapon.twice:
                        damage += dice(weapon.dice) * 2
                    else:
                        damage += dice(weapon.dice)
                hitcnt += 1
        if e.target.identified:
            dispname = e.target.name
        else:
            dispname = self.game.mondef[e.target.name].unident
        if e.target.monsters[0].state != State.OK:
            damage *= 2
        verb = random.choice(['swings', 'thrusts', 'stabs', 'slashes'])
        self.mw.print(
            f"{e.name} {verb} violently at {dispname} and hits {hitcnt} times for {damage} damage.")
        e.target.monsters[0].hp -= damage

        if e.entity.job == Job.NINJA:
            crit = (e.entity.level -
                    self.game.mondef[e.target.name].level) + 20
            if crit > 80:
                crit = 80
            elif crit < 5:
                crit = 5
            if crit > random.randrange(100):
                e.target.monsters[0].hp = 0
                e.target.monsters[0].state = State.DEAD
                self.mw.print(f"{dispname} is decapitated!")

        if e.target.monsters[0].hp <= 0:
            e.target.monsters[0].state = State.DEAD
            self.mw.print(f"{dispname} is killed.", start=' ')
            self.exp += self.game.mondef[e.target.name].exp
            e.entity.marks += 1
            e.target.monsters.pop(0)
            if not e.target.monsters:
                self.monp.remove(e.target)
            self.draw_ew()

    def reorder_party(self):
        """
        Members with bad status move back.
        """
        mems = self.game.party.members
        for mem in mems:
            if mem.state not in [State.OK]:
                mems.remove(mem)
                mems.append(mem)

    def identify_check(self):
        """
        Identify the monster (group) at 50% possibility
        """
        for mong in self.monp:
            if random.randrange(100) % 2:
                mong.identified = True

    def battle(self):
        """
        battle main
        """
        self.new_battle()
        place = self.game.party.place
        self.game.party.place = Place.BATTLE
        v = self.game.vscr
        v.meswins.append(self.ew)
        v.meswins.append(self.mw)
        self.mw.cls()

        self.create_monsterparty()
        self.draw_ew()

        if self.handle_friendly(place):
            party = self.game.party
            self.treasure = False
            for idx, room in enumerate(party.floor_obj.rooms):
                if room.in_room(party.x, party.y):
                    party.floor_obj.battled[idx] = True
                    break
            v.meswins.pop()
            v.meswins.pop()
            self.game.party.place = place
            return

        if self.surprised == 1:
            self.mw.print("You surprised the monsters.\n - press space bar")
            self.game.vscr.disp_scrwin()
            while getch(wait=True) != ' ':
                pass
        elif self.surprised == 2:
            self.mw.print("Monsters surprised you.\n - press space bar")
            self.game.vscr.disp_scrwin()
            while getch(wait=True) != ' ':
                pass

        while True:
            for m in self.game.party.members:
                m.action = '????????????'
            self.recover_state()
            self.reorder_party()
            self.identify_check()
            self.draw_ew()
            v.disp_scrwin()
            if self.input_action():
                self.ran = True
                v.meswins[0].print("Ran away from the battle.")
                v.disp_scrwin()
                self.game.party.x, self.game.party.px =\
                    self.game.party.px, self.game.party.x
                self.game.party.y, self.game.party.py =\
                    self.game.party.py, self.game.party.y
                self.game.party.floor, self.game.party.pfloor =\
                    self.game.party.pfloor, self.game.party.floor
                self.game.party.floor_obj =\
                    self.game.dungeon.floors[self.game.party.floor-1]
                self.treasure = False
                break  # ran successfully
            self.enemy_action()
            self.surprised = 0

            self.entities.sort(key=attrgetter('agi'), reverse=True)
            entities_tmp = self.entities[:]
            for e in entities_tmp:
                if not e.valid:
                    continue
                dispname = e.name
                if isinstance(e.target, Monstergrp):
                    if not self.monp:
                        break
                    if not e.target.monsters:  # already the gorup is gone
                        e.target = self.monp[0]
                if isinstance(e.entity, Monster):
                    if not e.group.identified:
                        dispname = self.game.mondef[e.name].unident
                if e.entity.state is State.ASLEEP:
                    self.mw.print(f"{dispname} is asleep.")
                    continue
                if e.entity.state not in [State.OK]:
                    continue
                if not self.monp:
                    break

                if e.action == 'parry':
                    self.mw.print(f"{dispname} parried.")
                elif e.action == 'breath':  # monster only
                    self.mw.print(f"{dispname} breathed on the party.")
                    for mem in self.game.party.members:
                        if mem.state in [State.DEAD, State.ASHED, State.LOST]:
                            continue
                        damage = e.entity.hp // 2
                        mem.hp = max(0, mem.hp - damage)
                        self.mw.print(f"{mem.name} incurred {damage} damage.",
                                      start=' ')
                        if mem.hp <= 0 and mem.state not in \
                           [State.DEAD, State.ASHED, State.LOST]:
                            mem.state = State.DEAD
                            mem.rip += 1
                            self.mw.print(f"{mem.name} is killed.",
                                          start=' ')
                elif e.action == 'fight':
                    if isinstance(e.entity, Member):
                        self.member_attack(e)
                    else:
                        self.monster_attack(e)
                elif e.action == 'dispell':
                    self.dispell(e)
                elif e.action == 'run':  # monster only
                    if self.canrun(e.entity):
                        e.group.monsters.remove(e.entity)
                        self.mw.print(f"{dispname} ran away.")
                        if not e.group.monsters:
                            self.monp.remove(e.group)
                        self.draw_ew()
                    else:
                        self.mw.print(f"{dispname} tried to run away")
                        self.mw.print(f".. but wasn't able to.", start=' ')
                elif e.action == 'help':  # monster only
                    self.mw.print(f"{dispname} called for help.")
                    if len(e.group.monsters) < 9 and \
                       random.randrange(100) < 40:  # 40%
                        self.mw.print(
                            f".. and a fellow monster appeared.", start=' ')
                        mon = Monster(self.game, e.name)
                        e.group.monsters.append(mon)
                        self.gold += self.game.mondef[e.name].level * \
                            (random.randrange(15) + 10)
                    else:
                        self.mw.print(
                            f".. but no help came.", start=' ')
                elif '?' in e.action:  # tried to use unidentified item
                    self.mw.print(f"{dispname} tried to use {e.action}.")
                    self.mw.print(
                        f".. but doesn't know how to use it.", start=' ')
                elif e.action in self.game.itemdef:  # item
                    item = self.game.itemdef[e.action]
                    if item.use and (spell := self.game.spelldef[item.use].battle):
                        self.mw.print(f"{dispname} used {e.action}.")
                        self.mw.print(f".. and invoked {spell}.")
                        v.disp_scrwin()
                        getch(wait=True)
                        self.game.spell.cast_spell_dispatch(
                            e.entity, spell, e.target)
                    else:
                        self.mw.print(f"{dispname} tried to use {e.action}.")
                        self.mw.print(f".. but wasn't able to.", start=' ')
                elif e.action in self.game.spelldef:  # spell
                    spelldef = self.game.spelldef[e.action]
                    if isinstance(e.entity, Member):
                        if (not spelldef.battle) or \
                           e.action not in list(itertools.chain(
                               e.entity.mspells, e.entity.pspells)):
                            self.mw.print(
                                f"{dispname} tried to cast {e.action}")
                            self.mw.print(
                                f".. but nothing happend.", start=' ')
                            v.disp_scrwin()
                            getch(wait=True)
                            continue
                        else:
                            if e.action in e.entity.mspells:
                                if e.entity.mspell_cnt[spelldef.level-1] > 0:
                                    e.entity.mspell_cnt[spelldef.level-1] -= 1
                                else:
                                    self.mw.print(
                                        f"{dispname} tried to cast {e.action}")
                                    self.mw.print(f".. but MP is exhausted.")
                                    v.disp_scrwin()
                                    getch(wait=True)
                                    continue
                            else:
                                if e.entity.pspell_cnt[spelldef.level-1] > 0:
                                    e.entity.pspell_cnt[spelldef.level-1] -= 1
                                else:
                                    self.mw.print(
                                        f"{dispname} tried to cast {e.action}")
                                    self.mw.print(f".. but MP is exhausted.")
                                    v.disp_scrwin()
                                    getch(wait=True)
                                    continue
                    if e.entity.silenced:
                        self.mw.print(
                            f"{dispname} tried to cast {e.action} but silenced.")
                    else:
                        self.mw.print(f"{dispname} casted {e.action}.")
                        self.game.spell.cast_spell_dispatch(
                            e.entity, e.action, e.target)
                self.clean_dead()  # clean up dead monsters
                v.disp_scrwin()
                if not self.monp:
                    break
                getch(wait=True)

            # Battle end?
            party = self.game.party
            if not self.monp:
                for idx, room in enumerate(party.floor_obj.rooms):
                    if room.in_room(party.x, party.y):
                        party.floor_obj.battled[idx] = True
                        break
                v.disp_scrwin()
                getch(wait=True)
                break
            defeated = True
            for mem in party.members:
                if mem.state in [State.OK, State.ASLEEP]:
                    defeated = False
                    break
            if defeated:
                self.mw.print("The party lost the battle and defeated.")
                self.mw.input_char(" - press space bar", values=[' '])
                party.place = Place.EDGE_OF_TOWN
                members = party.members[:]
                for mem in members:
                    mem.hp = 0
                    if mem.state in [State.PARALYZED, State.STONED]:
                        mem.state = State.DEAD
                        mem.rip += 1
                    mem.in_maze = True
                    mem.floor = party.floor  # last known place for him/her
                    party.members.remove(mem)
                party.floor = 0
                party.floor_move = 2
                party.light_cnt = 0
                party.ac = 0
                party.silenced = False
                party.identify = False
                party.gps = False
                break

        v.disp_scrwin()
        # getch()

        v.meswins.pop()
        v.meswins.pop()
        self.game.party.place = place
        return

    def clean_dead(self):
        """
        clean up dead monsters from monp and entities so that
        dead monsters don't attack or continue to be target
        """
        monp_tmp = self.monp[:]
        for mong in monp_tmp:
            mong_tmp = mong.monsters[:]
            for mon in mong_tmp:
                if mon.state in [State.DEAD, State.ASHED, State.LOST]:
                    mon.hp = 0
                    mong.monsters.remove(mon)
                    e = [e for e in self.entities if e.entity is mon]
                    if e:
                        e[0].valid = False
                    if not mong.monsters:  # no alive monsters in grp
                        self.monp.remove(mong)

    def recover_state(self):
        """
        Every turn, asleep members/monsers might wake up.
        Also, hpplus to members/momsters
        """
        v = self.game.vscr
        mw = v.meswins[-1]
        for mem in self.game.party.members:
            if mem.state == State.ASLEEP and random.randrange(100) < 50:
                mem.state = State.OK
            if mem.state in [State.DEAD, State.ASHED, State.LOST]:
                continue
            mem.hp = min(max(0, mem.hp+mem.hpplus), mem.maxhp)
        for mong in self.monp:
            for mon in mong.monsters:
                mon.hp = min(max(0, mon.hp+mon.hpplus), mon.maxhp)
                if mon.state == State.ASLEEP:
                    if self.game.mondef[mon.name].weaksleep:
                        chance = 15
                    else:
                        chance = 40
                    if random.randrange(100) < chance:
                        mon.state = State.OK

    def check_battle(self):
        """
        Check if they'll have a battle
        Return 0 if False, 1 if random encounter, 2 if room battle.
        """
        party = self.game.party
        rooms = party.floor_obj.rooms
        for idx, room in enumerate(rooms):
            if idx == 0:
                continue
            if room.in_room(party.x, party.y) \
               and not party.floor_obj.battled[idx]:
                if random.randrange(100) < min(95, party.floor*10):
                    self.room_index = idx
                    return 2  # with room guardian
                else:
                    party.floor_obj.battled[idx] = True
        if random.randrange(64) == 0:
            self.room_index = -1  # random encounter
            return 1  # random encounter

        return 0


class Entity:
    """
    Represents a battle entity, either a monster or a party member
    """

    def __init__(self, entity, name, group, agi, action, target):
        self.entity = entity  # member or monster object
        self.name = name  # member name or monster name (identified)
        self.group = group
        self.agi = agi  # relative agility
        self.action = action  #
        self.target = target  # member obj, mongrp obj ('self', 'all'?)
        self.valid = True  # valid flag


class Chest:
    """
    Represents a chest
    """

    def __init__(self, game):
        self.game = game
        self.mw = Meswin(game.vscr, 14, 3, 44, 10, frame=True)
        self.trap = Trap.TRAPLESS_CHEST
        self.items = None

    def chest(self):
        """
        Chest main.  Determine the trap, inspect, disarm, activate
        the trap, find items, etc.
        """
        game = self.game
        v = game.vscr
        mw = self.mw
        v.meswins.append(mw)
        mw.cls()

        self.trap = self.choose_trap()
        for mem in game.party.members:
            mem.inspected = False
        mw.print("A chest!")
        while True:
            mw.print("o)pen k)antei i)nspect d)isarm")
            mw.print("l)eave alone", start=' ')
            c = mw.input_char("Option?", values=['o', 'k', 'i', 'd', 'l'])
            if c == 'l':  # leave alone
                getch(wait=True)
                v.meswins.pop()
                return
            elif c == 'o':
                mem = game.party.choose_character(game)
                if not mem:
                    continue
                self.trap_activated(mem)
                self.treasure()
                v.meswins.pop()
                return
            elif c == 'd':  # disarm
                mem = game.party.choose_character(game)
                if not mem:
                    continue
                ans = mw.input("Trap name?")
                if ans == self.trap.name.lower().replace('_', ' '):
                    if mem.job in [Job.THIEF, Job.NINJA]:
                        chance = mem.level - game.party.floor + 50
                    else:
                        chance = mem.level - game.party.floor
                else:
                    self.trap_activated(mem)
                    self.treasure()
                    v.meswins.pop()
                    return
                if random.randrange(70) < chance:
                    mw.print("Disarmed the trap.", start=' ')
                    self.treasure()
                    v.meswins.pop()
                    return
                if random.randrange(20) < mem.stat[4]:  # agility
                    mw.print("Failed to disarm.", start=' ')
                    v.disp_scrwin()
                    continue
                self.trap_activated(mem)
                self.treasure()
                v.meswins.pop()
                return
            elif c == 'k':  # calfo
                mem = game.party.choose_character(game)
                if not mem:
                    continue
                if 'kantei' in mem.pspells and mem.pspell_cnt[1]:
                    mem.pspell_cnt[1] -= 1
                    mw.print(f"{mem.name} casted kantei.")
                    if random.randrange(100) < 95:
                        ans = self.trap
                    else:
                        ans = self.choose_trap()
                    mw.print(f"It is {ans.name.lower().replace('_', ' ')}.",
                             start=' ')
                else:
                    mw.print(f"{mem.name} failed to cast kantei.", start=' ')
                v.disp_scrwin()
                getch(wait=True)
            elif c == 'i':  # inspect
                mem = game.party.choose_character(game)
                if not mem:
                    continue
                if mem.inspected:
                    mw.print("Already inspected.", start=' ')
                    continue
                if mem.job == Job.THIEF:
                    chance = mem.stat[4] * 6  # agility
                elif mem.job == Job.NINJA:
                    chance = mem.stat[4] * 4
                else:
                    chance = mem.stat[4]
                chance = min(chance, 95)
                if random.randrange(100) >= chance:  # failed?
                    if random.randrange(20) > mem.stat[4]:
                        self.trap_activated(mem)
                        self.treasure()
                        v.meswins.pop()
                        return
                    else:
                        ans = self.choose_trap()
                else:  # succeeded to identify
                    ans = self.trap
                mem.identified = True
                mw.print(f"It is {ans.name.lower().replace('_', ' ')}.",
                         start=' ')
                v.disp_scrwin()

    def treasure(self):
        """
        Find and get up to 4 items from the chest.
        """
        mw = self.game.vscr.meswins[-1]
        got = False
        if len(self.items) > 0:
            if random.randrange(100) < 80:  # 80%
                item = self.choose_item(self.items[0])
                self.get_item(item)
                got = True
            self.items.pop(0)
        if len(self.items) > 0:
            if random.randrange(100) < 40:  # 40%
                item = self.choose_item(self.items[0])
                self.get_item(item)
                got = True
            self.items.pop(0)
        if len(self.items) > 0:
            if random.randrange(100) < 8:  # 8%
                item = self.choose_item(self.items[0])
                self.get_item(item)
                got = True
            self.items.pop(0)
        if len(self.items) > 0:
            if random.randrange(100) < 1:  # 1%
                item = self.choose_item(self.items[0])
                self.get_item(item)
                got = True
        if not got:
            mw.print("There was no interesting item.")
            self.game.vscr.disp_scrwin()
            getch(wait=True)

    def choose_item(self, item_lvl):
        """
        Randomly pick one item of the specified item level.
        """
        items = []
        for item in self.game.itemdef:
            if self.game.itemdef[item].level == item_lvl:
                items.append(item)
        item = random.choice(items)
        return item

    def get_item(self, item):
        """
        Someone in the party get the item found.
        """
        v = self.game.vscr
        mw = v.meswins[-1]
        if sum(len(mem.items) for mem in self.game.party.members) == \
           8 * len(self.game.party.members):
            mw.print("Item full.")
            v.disp_scrwin()
            getch(wait=True)
            return
        mem = random.choice(
            [mem for mem in self.game.party.members if len(mem.items) < 8])
        mem.items.append([item, False, False, True])
        mw.print(
            f"{mem.name} found {self.game.itemdef[item].unident}", start=' ')
        v.disp_scrwin()
        getch(wait=True)

    def trap_activated(self, mem):
        """
        Trap is activated and do harm to party member(s).
        """
        game = self.game
        v = game.vscr
        mw = self.mw
        if self.trap == Trap.TRAPLESS_CHEST:
            mw.print(f"It was a trapless chest.")
            v.disp_scrwin()
            getch(wait=True)
            return
        mw.print(f"Oops, {self.trap.name.lower().replace('_', ' ')}!")
        if self.trap == Trap.POISON_NEEDLE:
            # if not mem.poisoned:
            #    mem.hpplus -= 1
            mem.poisoned = True
            mw.print(f"{mem.name} was poisoned.", start=' ')
        elif self.trap == Trap.GAS_BOMB:
            for m in game.party.members:
                if random.randrange(100) < 50:
                    # if not m.poisoned:
                    #    mem.hpplus -= 1
                    m.poisoned = True
                    mw.print(f"{m.name} was poisoned.", start=' ')
            v.disp_scrwin()
        elif self.trap == Trap.CROSSBOW_BOLT:
            damage = dice('1D8')*game.party.floor
            mem.hp = max(mem.hp-damage, 0)
            mw.print(f"{mem.name} incurred {damage} damage.", start=' ')
            if mem.hp <= 0:
                mem.state = State.DEAD
                mem.rip += 1
                mw.print(f"{mem.name} is killed.", start=' ')
            v.disp_scrwin()
        elif self.trap == Trap.EXPLODING_BOX:
            for m in game.party.members:
                if random.randrange(100) < 75 and \
                   m.state not in [State.DEAD, State.ASHED, State.LOST]:
                    if random.randrange(100) < 67:
                        damage = dice('1D5') * game.party.floor
                    else:
                        damage = dice('1D8') * game.party.floor
                    m.hp = max(m.hp-damage, 0)
                    mw.print(f"{m.name} incurred {damage} damage.", start=' ')
                if m.hp <= 0:
                    m.state = State.DEAD
                    m.rip += 1
                    mw.print(f"{m.name} is killed.", start=' ')
            v.disp_scrwin()
        elif self.trap == Trap.STUNNER:
            mem.state = State.PARALYZED
            mw.print(f"{mem.name} got stunned.", start=' ')
            v.disp_scrwin()
        elif self.trap == Trap.TELEPORTER:
            mw.print(f"Oops, teleporter!", start=' ')
            v.disp_scrwin()
            game.party.move(random.randrange(game.dungeon.floors[game.party.floor-1].x_size),
                            random.randrange(game.dungeon.floors[game.party.floor-1].y_size))
        elif self.trap == Trap.ALARM:
            v.disp_scrwin()
            getch(wait=True)
            exp_sv = game.battle.exp
            gold_sv = game.battle.gold
            game.battle.battle()
            game.battle.exp += exp_sv
            game.battle.gold += gold_sv
            v.disp_scrwin()
            # getch(wait=True)
        elif self.trap == Trap.MAGE_BLASTER:
            for m in game.party.members:
                if m.job == Job.MAGE:
                    if random.randrange(20) >= m.stat[5]:
                        if m.state in [State.OK]:
                            m.state = State.PARALYZED
                            mw.print(f"{m.name} is paralyzed.", start=' ')
                    else:
                        if m.state in [State.OK, State.PARALYZED]:
                            m.state = State.STONED
                            mw.print(f"{m.name} is petrified.", start=' ')
                elif m.job == Job.SAMURAI:
                    if random.randrange(20) >= m.stat[5]:
                        if m.state in [State.OK]:
                            m.state = State.PARALYZED
                            mw.print(f"{m.name} is paralyzed.", start=' ')
            v.disp_scrwin()
        elif self.trap == Trap.PRIEST_BLASTER:
            for m in game.party.members:
                if m.job == Job.PRIEST:
                    if random.randrange(20) >= m.stat[5]:
                        if m.state in [State.OK]:
                            m.state = State.PARALYZED
                            mw.print(f"{m.name} is paralyzed.", start=' ')
                    else:
                        if m.state in [State.OK, State.PARALYZED]:
                            m.state = State.STONED
                            mw.print(f"{m.name} is petrified.", start=' ')
                elif m.job == Job.LORD:
                    if random.randrange(20) >= m.stat[5]:
                        if m.state in [State.OK]:
                            m.state = State.PARALYZED
                            mw.print(f"{m.name} is paralyzed.", start=' ')
        v.disp_scrwin()
        getch(wait=True)

    def choose_trap(self):
        """
        Decide which trap the chest has.
        """
        game = self.game
        if game.party.floor <= 2:
            trap = random.choice([Trap.TRAPLESS_CHEST, Trap.POISON_NEEDLE,
                                  Trap.CROSSBOW_BOLT])
        elif game.party.floor <= 5:
            trap = random.choice(
                [Trap.TRAPLESS_CHEST, Trap.POISON_NEEDLE, Trap.CROSSBOW_BOLT,
                 Trap.GAS_BOMB, Trap.EXPLODING_BOX, Trap.STUNNER])
        elif game.party.floor <= 8:
            trap = random.choice(
                [Trap.TRAPLESS_CHEST, Trap.GAS_BOMB, Trap.EXPLODING_BOX,
                 Trap.STUNNER, Trap.MAGE_BLASTER, Trap.PRIEST_BLASTER])
        else:
            trap = random.choice(
                [Trap.TRAPLESS_CHEST, Trap.GAS_BOMB, Trap.EXPLODING_BOX,
                 Trap.STUNNER, Trap.MAGE_BLASTER, Trap.PRIEST_BLASTER,
                 Trap.TELEPORTER, Trap.ALARM])
        return trap


def terminal_size():
    """
    Get terminal size
    Will return width and height
    """
    h, w, hp, wp = struct.unpack('HHHH',
                                 fcntl.ioctl(0, termios.TIOCGWINSZ,
                                             struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h


def getch(wait=False):
    """
    realtime key scan
    wait - if it waits (blocks) for user input
    """
    if os_windows:
        while True:
            if msvcrt.kbhit() or wait:  # msvcrt.kbhit() is non-blocking
                c = msvcrt.getch()  # msvcrt.getch() is blocking
                if c == 'Q':
                    sys.exit()
                return c

    fd = sys.stdin.fileno()
    oattr = termios.tcgetattr(fd)
    ch = ''
    try:
        while ch == '':
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if not wait:
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, oattr)
    if ch == 'Q':
        sys.exit()
    return ch


def dice(valstr):
    """
    valstr as "2D+4", "10D+300", etc.
    """
    pattern = r"(\d+)[dD](\d+)(\+(\d+))?"
    m = re.search(pattern, valstr)
    total = 0
    if m[4] is None:
        plus = 0
    else:
        plus = int(m[4])
    for _ in range(int(m[1])):
        total += random.randint(1, int(m[2]))
    return total + plus


def create_character(game):
    """
    Create a character (a training grounds menu item)
    """
    vscr = game.vscr
    mw = vscr.meswins[-1]
    while True:
        if (name := mw.input("Enter new name")):
            if name in [char.name for char in game.characters]:
                mw.print("The name is already used", start=' ')
                vscr.disp_scrwin()
            else:
                break
    vscr.disp_scrwin()

    mw.print("Choose race -")
    c = mw.input_char("  h)uman e)lf d)warf g)nome o)hobbit",
                      values=['h', 'e', 'd', 'g', 'o'])
    if c == 'h':
        race = Race.HUMAN
    elif c == 'e':
        race = Race.ELF
    elif c == 'd':
        race = Race.DWARF
    elif c == 'g':
        race = Race.GNOME
    else:
        race = Race.HOBBIT
    mw.print(f"{race.name.lower()}")
    vscr.disp_scrwin()

    c = mw.input_char(
        "Choose alignment - g)ood n)eutral e)vil", values=['g', 'n', 'e'])
    if c == 'g':
        align = Align.GOOD
    elif c == 'n':
        align = Align.NEUTRAL
    else:
        align = Align.EVIL
    mw.print(f"Alignment: {align.name.lower()}")
    vscr.disp_scrwin()

    ch = Member(name, align, race)
    ch.distribute_bonus(game)


def inspect_characters(game):
    """
    Inspect characters (a training grounds menu item)
    Can delete a character from here, too.
    """
    vscr = game.vscr
    newwin = False
    mw = vscr.meswins[-1]
    if mw.height < 16:
        mw = Meswin(vscr, 10, 2, 60, 16, frame=True)
        vscr.meswins.append(mw)
        newwin = True
    mw.mes_lines = []
    vscr.disp_scrwin()
    cnum = 0
    while True:
        chlist = game.party.members
        if game.party.place == Place.TRAINING_GROUNDS:
            chlist = game.characters
        mw.mes_lines = []
        mw.print("Inspect characters")
        mw.print(" - j)down k)up i)nspect d)elete l)eave")
        for i, mem in enumerate(chlist):
            if i == cnum:
                cur = ' >'
            else:
                cur = '  '
            mw.print(''.join([cur, str(i+1), ' ', str(mem)]), start=' ')
        vscr.disp_scrwin()
        c = getch()
        if c == 'l':
            break
        elif c == 'j' and cnum < len(chlist)-1:
            cnum += 1
        elif c == 'k' and cnum > 0:
            cnum -= 1
        elif c == 'i' and len(chlist) > 0:
            while True:
                rtn = chlist[cnum].inspect_character(game)
                if rtn == 0:
                    break
                cnum += rtn
                if cnum < 0:
                    cnum = len(chlist)-1
                elif cnum >= len(chlist):
                    cnum = 0
        elif c == 'd' and len(chlist) > 0 and \
                mem not in game.party.members:
            mem = chlist[cnum]
            nw = Meswin(vscr, 16, 8, 54, 3, frame=True)
            vscr.meswins.append(nw)
            c = nw.input_char(f"Delete {mem.name} permanently? (y/n)",
                              values=['y', 'n'])
            if c == 'y':
                chlist.remove(mem)
                nw.print(f"{mem.name} is deleted.")
                if cnum >= len(chlist):
                    cnum -= 1
                vscr.disp_scrwin()
                getch(wait=True)
            vscr.meswins.pop()
    if newwin:
        vscr.meswins.pop()
    vscr.cls()


def training(game):
    """
    Training grounds main (an edge of town menu item)
    """
    vscr = game.vscr
    game.party.place = Place.TRAINING_GROUNDS
    mw = vscr.meswins[-1]
    vscr.cls()
    vscr.disp_scrwin()
    while True:
        mw.print(
            "\n*** training grounds ***\nc)reate a character\ni)nspect a character\nl)eave", start=' ')
        vscr.disp_scrwin()
        c = mw.input_char("Command?", values=['c', 'i', 'l'])
        if c == 'l':
            break
        elif c == 'c':
            create_character(game)
        elif c == 'i':
            inspect_characters(game)


def tavern_add(game):
    """
    Add members to the party (a tavern item)
    """
    vscr = game.vscr
    mw = vscr.meswins[-1]
    if len(game.party.members) >= 6:
        mw.print("Party full.")
        vscr.disp_scrwin()
        return

    vscr.disp_scrwin()
    chwin = Meswin(vscr, 12, 2, 40, 16)
    vscr.meswins.append(chwin)
    top = idx = 0
    while True:
        chlines = []
        i = 0
        charlist = [
            ch for ch in game.characters
            if (ch not in game.party.members and not ch.in_maze)]
        for i, ch in enumerate(charlist):
            cur = ' '
            if i == idx:
                cur = '>'
                cur_ch = ch
            chline = f"| {cur}{i+1:2} {ch.name.ljust(16)} Lv{ch.level:3d} {ch.race.name[:3]}-{ch.align.name[:1]}-{ch.job.name[:3]}"
            chlines.append(chline)
        chwin.mes_lines = []
        chwin.mes_lines.append(
            "| Add who to the party?".ljust(chwin.width-1)+'|')
        chwin.mes_lines.append(
            "|  - j)down k)up x)choose l)eave".ljust(chwin.width-1)+'|')
        for chl in chlines[top:top+chwin.height-2]:
            chwin.mes_lines.append(chl.ljust(chwin.width-1)+'|')
        vscr.disp_scrwin()
        c = getch(wait=True)
        if c == 'l':
            break
        elif c == 'j' and idx < len(charlist)-1:
            idx += 1
            top = max(0, idx-chwin.height+3)
        elif c == 'k' and idx > 0:
            idx -= 1
            top = min(top, idx)
        elif c == 'x':
            game.party.members.append(cur_ch)
            if idx >= len(charlist)-1:
                idx -= 1
            if len(game.party.members) >= 6 or len(charlist) <= 1:
                break
    vscr.meswins.pop()
    vscr.cls()
    vscr.disp_scrwin()


def tavern(game):
    """
    tavern (a castle item)
    add/remove members to the party, inspect, divide golds, etc.
    """
    game.party.place = Place.HAWTHORNE_TAVERN
    vscr = game.vscr
    mw = vscr.meswins[-1]
    newwin = False
    if mw.height < 16:
        mw = Meswin(vscr, 8, 2, 64, 16, frame=True)
        vscr.meswins.append(mw)
        newwin = True
    ch = ''
    while True:
        mw.print("\n*** The Hawthorne Tavern ***", start=' ')
        vscr.disp_scrwin()
        ch = mw.input_char("Command? - a)dd r)emove i)nspect d)ivvy gold l)eave",
                           values=['a', 'r', 'i', 'd', 'l', '^'])
        if ch == 'l':
            game.party.place = Place.CASTLE
            break
        elif ch == '^' and config['debug']:
            mw.print("debug twice!")
            for mem in game.party.members:
                mem.exp *= 2
                mem.gold *= 2
        elif ch == 'd':
            if not game.party.members:
                continue
            total = sum(mem.gold for mem in game.party.members)
            each = total // len(game.party.members)
            for mem in game.party.members:
                total -= each
                mem.gold = each
            mem.gold += total  # remaining
        elif ch == 'a':
            if len(game.party.members) < len(game.characters):
                tavern_add(game)
            else:
                mw.print("No characters to add")
        elif ch == 'i':
            if not game.party.members:
                continue
            idx = 0
            while True:
                mem = game.party.members[idx]
                rtn = mem.inspect_character(game)
                if rtn == 0:
                    break
                idx += rtn
                if idx < 0:
                    idx = len(game.party.members) - 1
                elif idx >= len(game.party.members):
                    idx = 0
        elif ch == 'r':
            game.party.remove_character(game)
    if newwin:
        vscr.meswins.pop()
        vscr.cls()


def trader_buy(game, mem):
    """
    a member chooses and buys items from shop inventory
    """
    vscr = game.vscr
    iw = Meswin(vscr, 12, 1, 48, 12, frame=True)
    vscr.meswins.append(iw)
    top = idx = page = 0
    pages = (('weapon'), ('armor'), ('shield', 'helm', 'gloves'),
             ('ring', 'item'))
    while True:
        items = [item for item in game.shopitems if game.shopitems[item] > 0
                 and game.itemdef[item].type in pages[page]]
        ilines = []
        for i, item in enumerate(items):
            cur = ' '
            if i == idx:
                cur = '>'
                cur_item = i
            afford = canequip = ' '
            if mem.job.name[:1].lower() not in game.itemdef[item].jobs.lower():
                canequip = '#'
            if mem.gold >= game.itemdef[item].price:
                afford = '$'
            iline = f"{cur}{i+1:2} {item.ljust(iw.width-24)[:iw.width-24]} {game.itemdef[item].price:10d}{canequip}{afford}"
            ilines.append(iline)
        iw.mes_lines = []
        iw.mes_lines.append(
            f"{mem.name} has {mem.gold} gold")
        iw.mes_lines.append("  jk)cursor x)choose hl)page ;)leave")
        for il in ilines[top:top+iw.height-2]:
            iw.mes_lines.append(il.ljust(iw.width-6))
        for _ in range(iw.width - len(iw.mes_lines)):
            iw.mes_lines.append(' '*(iw.width-6))
        vscr.disp_scrwin()
        c = getch(wait=True)
        if c == ';':
            break
        elif c == 'j' and idx < len(items)-1:
            idx += 1
            top = max(0, idx-iw.height+3)
        elif c == 'k' and idx > 0:
            idx -= 1
            top = min(top, idx)
        elif c == 'h':
            idx = top = 0
            page -= 1
            if page < 0:
                page = len(pages)-1
        elif c == 'l':
            idx = top = 0
            page += 1
            if page >= len(pages):
                page = 0
        elif c == 'x':
            if len(mem.items) >= 8:
                iw.mes_lines[0] = "Looks like, your bag is full."
                vscr.disp_scrwin()
                getch()
            elif mem.gold < game.itemdef[items[idx]].price:
                iw.mes_lines[0] = "Sorry, you can't afford it."
                iw.mes_lines[1] = f"Will someone else pay? (y/n)>"
                vscr.disp_scrwin()
                c = getch(wait=True)
                if c == 'y':
                    if game.party.pay(game.itemdef[items[idx]].price):
                        bought = [items[idx], False, False, False]
                        mem.items.append(bought)
                        game.shopitems[items[idx]] -= 1
                        iw.mes_lines[0] = "Anything else, noble sir?"
                    else:
                        iw.mes_lines[0] = "Oh, I'm sorry."
                    iw.mes_lines[1] = ""
                    vscr.disp_scrwin()
                    getch(wait=True)

            else:
                iw.mes_lines[0] = "Anything else, noble sir?"
                mem.gold -= game.itemdef[items[idx]].price
                bought = [items[idx], False, False, False]
                mem.items.append(bought)
                game.shopitems[items[idx]] -= 1
                vscr.disp_scrwin()
                getch()
    vscr.cls()
    vscr.meswins.pop()


def trader_sell(game, mem, op):
    """
    sell, uncurse or identify items
    """
    vscr = game.vscr
    mw = vscr.meswins[-1]
    if op == 's':
        opword = 'sell'
        div = 2
    elif op == 'u':
        opword = 'uncurse'
        div = 2
    else:
        opword = 'identify'
        div = 4

    mw.print(f"Which item to {opword}? -  # or leave")
    idic = {}
    for i, item in enumerate(mem.items, 1):
        dispname = item[0]
        mark = ' '
        if op == 'u':  # uncurse
            if not item[2]:
                continue
            mark = '&'
            if item[3]:
                dispname = ''.join(['?', game.itemdef[item[0]].unident])
        elif op == 'i':  # identify
            if (not item[3]) or item[2]:
                continue
            dispname = ''.join(['?', game.itemdef[item[0]].unident])
        else:  # sell
            if item[1] or item[2] or item[3]:
                continue
        price = game.itemdef[item[0]].price//div
        if op == 'i':
            price = min(1000, max(price, 20))
        mw.print(
            f"{i}){mark}{dispname.ljust(24)} {price}",
            start=' ')
        idic[i] = (item[0], dispname, price)

    while True:
        c = mw.input_char("# or l)eave")
        if c == 'l':
            return
        try:
            if int(c) in idic:
                break
        except:
            continue
    if idic[int(c)][0] not in game.shopitems:
        game.shopitems[idic[int(c)][0]] = 0
    price = idic[int(c)][2]
    if op == 's':
        if price == 0:
            mw.print("Sorry, but not interested.")
        else:
            mem.gold += price
            del mem.items[int(c)-1]
            mw.print("I'm sure fellows'll want it.")
            game.shopitems[idic[int(c)][0]] += 1
    elif op == 'i':
        if mem.gold < price:
            mw.print("Oh, you can't afford it.")
            yn = mw.input_char("Someone else will pay? (y/n)",
                               values=['y', 'n'])
            if yn == 'y':
                game.party.pay(price)
            else:
                mw.print("Ok, fine.")
                return
        else:
            mem.gold -= price
        mem.items[int(c)-1][3] = False  # identified
        mw.print(f"Identified as {mem.items[int(c)-1][0]}.")
    else:
        if mem.gold < price:
            mw.print("Um, you can't afford it.")
            yn = mw.input_char("Someone else will pay? (y/n)",
                               values=['y', 'n'])
            if yn == 'y':
                game.party.pay(price)
            else:
                mw.print("Ok, fine.")
                return
        else:
            mem.gold -= price
        mw.print(f"Uncursed {mem.items[int(c)-1][0]}.")
        del mem.items[int(c)-1]

    game.vscr.disp_scrwin()
    getch()


def trader(game):
    """
    shop (a castle item)
    choose a member and he/she buys, sells items, etc.
    """
    if not game.party.members:
        return
    game.party.place = Place.TRADER_JAYS
    vscr = game.vscr
    mw = vscr.meswins[-1]
    while True:
        mw.print("\n*** Trader Jay's ***", start=' ')
        vscr.disp_scrwin()
        mem = game.party.choose_character(game)
        if not mem:
            break
        while True:
            mw.print(f"Welcome, {mem.name}.")
            mw.print(f"  You have {mem.gold} gold.")
            ch = mw.input_char(f"b)uy s)ell u)ncurse i)dentify p)ool gold l)eave",
                               values=['b', 's', 'u', 'i', 'p', 'l'])
            if ch == 'l':
                break
            elif ch == 'b':
                trader_buy(game, mem)
            elif ch in 'sui':
                trader_sell(game, mem, ch)
            elif ch == 'p':
                gold = 0
                for c in game.party.members:
                    gold += c.gold
                    c.gold = 0
                mem.gold = gold


def levelup(game, m):
    """
    Check and levelup the member.
    Returns the number of level-ups and if learned spell(s).
    """
    levelup = 0
    learned = False
    while True:
        if m.level < 13:
            next = level_table[m.job][m.level-1]
        else:
            next = level_table[m.job][11] + \
                level_table[m.job][12]*(m.level-12)
        m.nextexp = next
        if next > m.exp:
            return levelup, learned

        levelup += 1

        for i in range(6):
            if random.randrange(100) < 45:  # 45%
                m.stat[i] += 1
            elif random.randrange(100) < 25:  # (100-45) * 25% = 13.75%
                m.stat[i] -= 1
            m.stat[i] = max(m.stat[i], race_status[m.race][i])
            m.stat[i] = min(m.stat[i], race_status[m.race][i]+10)

        m.level += 1
        newhp = 0
        if m.stat[3] <= 3:
            plus = -2
        elif m.stat[3] <= 5:
            plus = -1
        elif m.stat[3] >= 20:
            plus = 4
        elif m.stat[3] >= 18:
            plus = 3
        elif m.stat[3] >= 16:
            plus = 2
        elif m.stat[3] >= 15:
            plus = 1
        else:
            plus = 0

        jobdice = {
            Job.FIGHTER: '1D10',
            Job.LORD: '1D10',
            Job.PRIEST: '1D8',
            Job.SAMURAI: '1D8',
            Job.THIEF: '1D6',
            Job.BISHOP: '1D6',
            Job.NINJA: '1D6',
            Job.MAGE: '1D4',
        }
        d = jobdice[m.job]
        times = m.level
        if m.job == Job.SAMURAI:
            times += 1
        for _ in range(times):
            p = dice(d) + plus
            if p < 1:
                p = 1
            newhp += p

        if newhp > m.maxhp:
            m.maxhp = newhp
        else:
            m.maxhp += 1

        m.hp = m.maxhp

        if m.job == Job.MAGE:
            sc = game.spell.spell_counts(0, 2, m.level)
            for i in range(len(sc)):
                m.mspell_max[i] = min(9, max(sc[i], m.mspell_max[i]))
        elif m.job == Job.PRIEST:
            sc = game.spell.spell_counts(0, 2, m.level)
            for i in range(len(sc)):
                m.pspell_max[i] = min(9, max(sc[i], m.pspell_max[i]))
        elif m.job == Job.BISHOP:
            sc = game.spell.spell_counts(0, 4, m.level)
            for i in range(len(sc)):
                m.mspell_max[i] = min(9, max(sc[i], m.mspell_max[i]))
            sc = game.spell.spell_counts(3, 4, m.level)
            for i in range(len(sc)):
                m.pspell_max[i] = min(9, max(sc[i], m.pspell_max[i]))
        elif m.job == Job.SAMURAI:
            sc = game.spell.spell_counts(3, 3, m.level)
            for i in range(len(sc)):
                m.mspell_max[i] = min(9, max(sc[i], m.mspell_max[i]))
        elif m.job == Job.LORD:
            sc = game.spell.spell_counts(3, 2, m.level)
            for i in range(len(sc)):
                m.pspell_max[i] = min(9, max(sc[i], m.pspell_max[i]))

        for sname in game.spelldef:
            if game.spelldef[sname].categ == 'mage':
                # memorize the spell if iq > randrange(30), he/she
                # has not learned it yet and the spell count of the level > 0
                if m.stat[1] > random.randrange(30):  # iq
                    if sname not in m.mspells and \
                       m.mspell_max[game.spelldef[sname].level-1] > 0:
                        m.mspells.append(sname)
                        learned = True
                # memorize the 1st spell of the level if he/she
                # has not memorized any spell of the level but
                # his/her spell count of the level > 0
                if m.mspell_max[game.spelldef[sname].level-1] > 0 and \
                   sum(1 for spl in m.mspells if
                       game.spelldef[spl].level == game.spelldef[sname].level) == 0:
                    m.mspells.append(sname)
                    learned = True
            else:
                if m.stat[2] > random.randrange(30):  # piety
                    if sname not in m.pspells and \
                       m.pspell_max[game.spelldef[sname].level-1] > 0:
                        m.pspells.append(sname)
                        learned = True
                if m.pspell_max[game.spelldef[sname].level-1] > 0 and \
                   sum(1 for spl in m.pspells if
                       game.spelldef[spl].level == game.spelldef[sname].level) == 0:
                    m.pspells.append(sname)
                    learned = True
        mspells = []
        pspells = []
        for sname in game.spelldef:  # reorder
            if sname in m.mspells:
                mspells.append(sname)
            elif sname in m.pspells:
                pspells.append(sname)
        m.mspells = mspells
        m.pspells = pspells

        for idx in range(7):
            know = sum(1 for s in m.mspells if
                       game.spelldef[s].level == idx+1 and
                       game.spelldef[s].categ == 'mage')
            m.mspell_max[idx] = max(m.mspell_max[idx], know)
            know = sum(1 for s in m.pspells if
                       game.spelldef[s].level == idx+1 and
                       game.spelldef[s].categ == 'priest')
            m.pspell_max[idx] = max(m.pspell_max[idx], know)


def sleep(game, m, healhp):
    """
    Sleep a night.  Heal hp, restore MPs and check for level-ups.
    """
    v = game.vscr
    mw = v.meswins[-1]
    mw.print(f"{m.name} went to bed...")
    v.disp_scrwin()
    getch(wait=True)

    oldstate = m.stat[:]
    oldhp = m.maxhp
    levels, learned = levelup(game, m)

    m.hp += healhp
    if m.hp > m.maxhp:
        m.hp = m.maxhp

    m.mspell_cnt = m.mspell_max[:]
    m.pspell_cnt = m.pspell_max[:]

    if levels > 0:
        mw.print(f"Level up!")
        if m.stat[0] > oldstate[0]:
            mw.print(f"Gained strength by {m.stat[0]-oldstate[0]} points.")
        elif m.stat[0] < oldstate[0]:
            mw.print(f"Lost strength by {oldstate[0]-m.stat[0]} points.")
        if m.stat[1] > oldstate[1]:
            mw.print(
                f"Gained i.q. by {m.stat[1]-oldstate[1]} points.", start=' ')
        elif m.stat[1] < oldstate[1]:
            mw.print(
                f"Lost i.q. by {oldstate[1]-m.stat[1]} points.", start=' ')
        if m.stat[2] > oldstate[2]:
            mw.print(
                f"Gained piety by {m.stat[2]-oldstate[2]} points.", start=' ')
        elif m.stat[2] < oldstate[2]:
            mw.print(
                f"Lost piety by {oldstate[2]-m.stat[2]} points.", start=' ')
        if m.stat[3] > oldstate[3]:
            mw.print(
                f"Gained vitality by {m.stat[3]-oldstate[3]} points.", start=' ')
        elif m.stat[3] < oldstate[3]:
            mw.print(
                f"Lost vitality by {oldstate[3]-m.stat[3]} points.", start=' ')
        if m.stat[4] > oldstate[4]:
            mw.print(
                f"Gained agility by {m.stat[4]-oldstate[4]} points.", start=' ')
        elif m.stat[4] < oldstate[4]:
            mw.print(
                f"Lost agility by {oldstate[4]-m.stat[4]} points.", start=' ')
        if m.stat[5] > oldstate[5]:
            mw.print(
                f"Gained luck by {m.stat[5]-oldstate[5]} points.", start=' ')
        elif m.stat[5] < oldstate[5]:
            mw.print(
                f"Lost luck by {oldstate[5]-m.stat[5]} points.", start=' ')
        if m.maxhp > oldhp:
            mw.print(
                f"Your hp increased by {m.maxhp-oldhp} points.", start=' ')
        elif m.maxhp < oldhp:
            mw.print(
                f"Your hp decreased by {oldhp-m.maxhp} points.", start=' ')
        if learned:
            mw.print(f"Leaned new spells.", start=' ')
        v.disp_scrwin()
        getch(wait=True)


def inn(game):
    if not game.party.members:
        return
    v = game.vscr
    game.party.place = Place.LAKEHOUSE_INN
    mw = v.meswins[-1]
    num = len(game.party.members)
    gold = sum(m.gold for m in game.party.members)
    mw.print("\n*** The Lakehouse Inn ***", start=' ')
    mw.print(f"Welcome.  You must be very tired.", start=' ')
    mw.print(f"You have {gold} gold in total.", start=' ')
    mw.print(f"c)ots                {2*num:4d} gold", start=' ')
    mw.print(f"s)tandard rooms      {20*num:4d} gold", start=' ')
    mw.print(f"d)elux rooms         {100*num:4d} gold", start=' ')
    mw.print(f"v)lake view suites   {500*num:4d} gold", start=' ')
    mw.print(f"p)residential suites {2000*num:4d} gold", start=' ')
    mw.print(f"or l)eave", start=' ')
    c = mw.input_char("Which rooms to stay today?",
                      values=['c', 's', 'd', 'v', 'p', 'l'])
    if c == 'l':
        return
    elif c == 'c':
        uprice = 2
        dinner = 'cabbage soup'
    elif c == 's':
        uprice = 20
        dinner = random.choice(['juicy hamburgers', 'pork and scallion',
                                'chiken pho', 'dana masala',
                                'beef and broccoli', 'pizza slices'])
    elif c == 'd':
        uprice = 100
        dinner = random.choice(['grilled sword fish', 'ribeye steak',
                                'temaki sushi', 'lamb chops', 'fillet mignon',
                                'maine lobster roll', 'juicy white asparagus'])
    elif c == 'v':
        uprice = 500
        dinner = random.choice(["wine and dry-aged beef fillet mignon",
                                "california wine and kobe beef NY strip steak",
                                "ooma kuromaguro toro tuna sushi"])
    else:  # presidential suites
        uprice = 2000
        dinner = random.choice(['supreme course w/ champagne',
                                "chef's special w/ vintage wine",
                                "jiro sushi w/ daiginjyo sake",
                                "manchu-han imperial feast course"])
    if not game.party.pay(uprice*num):
        mw.print("You can't afford the room.")
        v.disp_scrwin()
        return
    mw.print(f"Today's dinner is {dinner}.")
    for mem in game.party.members:
        sleep(game, mem, uprice*2)


def hospital(game):
    if not game.party.members:
        return
    v = game.vscr
    game.party.place = Place.MGH
    mw = v.meswins[-1]
    num = len(game.party.members)
    gold = sum(m.gold for m in game.party.members)
    pricing = {
        State.PARALYZED: 50,
        State.STONED: 100,
        State.DEAD: 200,
        State.ASHED: 500,
    }
    mw.print("\n *** Moss General Hospital ***", start=' ')
    v.disp_scrwin()
    hlist = game.hospitalized[:]
    for p in hlist:
        price = pricing[p.state] * p.level
        mw.print(
            f"{p.name} is in ER and in a dangerous condition.")
        mw.print(
            f"Would someone pay for {p.name}?  It would be {price} gold.")
        c = mw.input_char("Pay? (y/n)", values=['y', 'n'])
        if c == 'y':
            if not game.party.pay(price):
                mw.print("You can't afford it.")
                v.disp_scrwin()
                continue
            if p.state == State.DEAD and \
               random.randrange(100) > 50 + (3*p.stat[3]):
                mw.print("Oops..")
                v.disp_scrwin()
                p.state = State.ASHED
            elif p.state == State.ASHED and \
                    random.randrange(100) > 40 + (3*p.stat[3]):
                mw.print("...(oh my god)...")
                v.disp_scrwin()
                p.state = State.LOST
            else:
                mw.print(f"{p.name} was cured.")
                v.disp_scrwin()
                game.hospitalized.remove(p)
                p.state = State.OK
                p.hp = p.maxhp
            getch(wait=True)
    mw.print("They left MGH.")
    v.disp_scrwin()
    getch(wait=True)


def castle(game):
    """
    castle main
    dispatch to tavern, shop, inn or temple
    """
    vscr = game.vscr
    mw = vscr.meswins[-1]
    vscr.cls()
    vscr.disp_scrwin()
    ch = ''
    while True:
        mw.cls()
        game.party.place = Place.CASTLE
        mw.print("*** Castle ***", start=' ')
        mw.print("h)awthorne tavern\nt)rader jay's\ni)lakehouse inn", start=' ')
        mw.print("m)oss general hospital\ne)dge of town", start=' ')
        vscr.disp_scrwin()
        ch = mw.input_char("Command?", values=['h', 'e', 't', 'i', 'm'])
        if ch == 'h':
            tavern(game)
        elif ch == 'e':
            game.party.place = Place.EDGE_OF_TOWN
            break
        elif ch == 't':
            trader(game)
        elif ch == 'i':
            inn(game)
        elif ch == 'm':
            hospital(game)


def edge_town(game):
    """
    edge of town main
    dispatch to training grounds
    """
    vscr = game.vscr
    mw = vscr.meswins[-1]
    ch = ''
    while ch != 'c':
        mw.cls()
        game.party.place = Place.EDGE_OF_TOWN
        mw.print("*** Edge of Town ***", start=' ')
        mw.print(
            "m)aze\nt)raining grounds\nc)astle\nS)ave and quit game\nR)esume from saved data", start=' ')
        vscr.disp_scrwin()
        ch = mw.input_char("Command? ", values=['t', 'S', 'm', 'c', 'R'])
        if ch == 't':
            training(game)
        elif ch == 'c':
            game.party.place = Place.CASTLE
            break
        elif ch == 'm':
            if game.party.members:
                game.party.place = Place.MAZE
            else:
                mw.print("No party members.")
            break
        elif ch == 'S':
            game.save()
            mw.print("Thank you for playing.")
            mw.print("See you soon.")
            vscr.disp_scrwin()
            sys.exit()
        elif ch == 'R':
            if game.load():
                mw.print("loaded.")
            vscr.disp_scrwin()
            break


def camp(game, floor_obj):
    """
    Camp main
    """
    game.party.place = Place.CAMP
    v = game.vscr
    mw = Meswin(v, 10, 1, 64, 17, frame=True)
    v.meswins.append(mw)

    while not game.party.floor_move:  # tsubasa?
        mw.print(
            "*** Camp ***\ni)nspect\nr)eorder party\nh)eal all members\np)rep for adventure\nS)ave and quit game\nl)eave")
        c = mw.input_char("Command?", values=['i', 'r', 'S', 'l', 'h', 'p'])
        if c == 'l':
            break
        elif c == 'r':
            game.party.reorder(game)
        elif c == 'h':
            game.party.heal(game)
        elif c == 'p':
            game.party.prep(game)
        elif c == 'S':
            game.party.place = Place.MAZE
            game.save()
            mw.print("Thank you for playing.")
            mw.print("See you again soon.")
            v.disp_scrwin()
            sys.exit()
        elif c == 'i':
            idx = 1
            while not game.party.floor_move:  # tsubasa?
                mem = game.party.members[idx-1]
                rtn = mem.inspect_character(game)
                if rtn == 0:
                    break
                idx += rtn
                if idx < 0:
                    idx = len(game.party.members) - 1
                elif idx >= len(game.party.members):
                    idx = 0

    v.disp_scrwin(floor_obj)
    v.meswins.pop()
    game.party.place = Place.MAZE


def maze(game):
    """
    Maze (dungeon) main
    """

    vscr = game.vscr
    meswins_save = vscr.meswins
    meswin = vscr.meswins[0]
    vscr.meswins = [meswin]

    dungeon = game.dungeon
    party = game.party

    party.floor_move = 0
    if not party.resumed and\
       party.place in [Place.MAZE, Place.CAMP, Place.BATTLE]:
        party.place = Place.MAZE
        party.floor = 0
        party.floor_move = 1  # 0: no, 1: down, 2: up

        dungeon.floors = []  # initialize every time
        party.floor_obj = floor_obj = None
    party.resumed = False

    while True:
        dungeon.generate_move_floors()
        floor_obj = party.floor_obj

        if party.light_cnt > 0:  # milwa/lomilwa counter
            party.light_cnt -= 1

        party.calc_hpplus(game)
        for mem in party.members:
            if mem.state not in [State.DEAD, State.ASHED, State.LOST]:
                mem.hp = min(max(1, mem.hp+mem.hpplus), mem.maxhp)

        vscr.disp_scrwin()

        rt = floor_obj.check_event(game)
        if party.defeated():  # Defeated by boss monster?
            break
        if not rt:  # event processed
            rtn = game.battle.check_battle()
            if rtn:  # 1: random or 2: room (or 3?) if battle
                meswin.print("*** encounter ***")
                vscr.disp_scrwin(floor_obj)
                getch()
                game.battle.battle()
                if party.defeated():  # party defeated
                    break
                if rtn == 2 and game.battle.treasure:  # room battle
                    game.chest.chest()
                    game.battle.gold *= 2  # Twice the gold for a chest.
                    if party.defeated():
                        break
                if not game.battle.treasure:
                    game.battle.exp = 0
                    game.battle.gold = 0
                survnum = sum(1 for m in party.members
                              if m.state in [State.OK, State.ASLEEP,
                                             State.PARALYZED, State.STONED])
                meswin.print(f"Each survivor gets {game.battle.exp//survnum} e.p.",
                             start=' ')
                meswin.print(f"Each survivor gets {game.battle.gold//survnum} gold.",
                             start=' ')
                for mem in party.members:
                    if mem.state == State.ASLEEP:
                        mem.state = State.OK
                    if mem.state in [State.OK, State.PARALYZED, State.STONED]:
                        mem.exp += game.battle.exp//survnum
                        mem.gold += game.battle.gold//survnum
        if game.battle.ran:  # ran?
            if floor_obj != party.floor_obj:
                floor_obj = party.floor_obj
        vscr.disp_scrwin(floor_obj)

        exit = dungeon.check_move_floor(floor_obj)
        if exit:  # Exit from dungeon
            mlist = party.members[:]
            for mem in mlist:
                if mem.poisoned:
                    mem.poisoned = False
                    mem.hpplus = 0
                if mem.state in [State.PARALYZED, State.STONED, State.DEAD,
                                 State.ASHED]:
                    party.members.remove(mem)
                    # Carried away in an ambulance
                    game.hospitalized.append(mem)

            party.light_cnt = 0
            party.ac = 0
            party.silenced = False
            party.identify = False
            party.gps = False

            break
        if party.floor_move:
            continue

        c = getch(wait=True)
        draw = True
        if c:
            if c == 'c':
                camp(game, floor_obj)
                if game.party.floor_move:
                    continue
            elif c in 'hH' and party.x > 0:
                if (c == 'H' and config['debug']) or \
                   floor_obj.can_move(party.x-1, party.y):
                    party.move(party.x-1, party.y)
                    meswin.print("west")
            elif c in 'kK' and party.y > 0:
                if (c == 'K' and config['debug']) or \
                   floor_obj.can_move(party.x, party.y-1):
                    party.move(party.x, party.y-1)
                    meswin.print("north")
            elif c in 'jJ' and party.y < floor_obj.y_size-1:
                if (c == 'J' and config['debug']) or \
                   floor_obj.can_move(party.x, party.y+1):
                    party.move(party.x, party.y+1)
                    meswin.print("south")
            elif c in 'lL' and party.x < floor_obj.x_size-1:
                if (c == 'L' and config['debug']) or \
                   floor_obj.can_move(party.x+1, party.y):
                    party.move(party.x+1, party.y)
                    meswin.print("east")
            elif c == 'o':  # open or unlock door
                vscr.disp_scrwin(floor_obj)
                floor_obj.open_door(game, meswin)
            elif c == '*' and config['debug']:
                breakpoint()
            elif c == '.':
                meswin.print('.')
                vscr.disp_scrwin()
            elif c == '>' and config['debug']:
                party.floor_move = 1  # go down
                for m in party.members:
                    m.deepest = max(m.deepest, party.floor)
            elif c == '<' and config['debug']:
                party.floor_move = 2  # go up
            elif c == 'S':
                game.save()
                meswin.print("saved.")
                vscr.disp_scrwin()
            elif c == '#' and config['debug']:
                for y in range(party.y-10, party.y+10+1):
                    for x in range(party.x-32, party.x+32+1):
                        floor_obj.put_tile(
                            x, y, floor_obj.get_tile(x, y), orig=False)
            else:
                pass  # draw = False
        else:
            draw = False
        if draw:
            vscr.disp_scrwin(floor_obj)

    vscr.meswins = meswins_save
    vscr.cls()
    party.place = Place.EDGE_OF_TOWN
    vscr.disp_scrwin()


def dispatch(game):
    """
    dispatch either to edge of town, castle or maze
    """
    while game.party.place != Place.LEAVE_GAME:
        pl = game.party.place
        if pl == Place.EDGE_OF_TOWN:
            edge_town(game)
        elif pl == Place.CASTLE:
            castle(game)
        elif pl == Place.MAZE:
            maze(game)


def main():
    game = Game()  # singleton
    party = Party(0, 0, 1)
    game.party = party
    game.load_spelldef()
    game.load_itemdef()
    game.load_monsterdef()
    party.place = Place.CASTLE
    w, h = terminal_size()
    vscr = Vscr(w, h-1)  # singleton
    # vscr = Vscr(78, 24)  # +++++++++++++++
    game.vscr = vscr
    vscr.game = game
    # meswin for scrollwin
    vscr.meswins.append(Meswin(vscr, 43, vscr.height-7, vscr.width-42, 7))
    # meswin for castle/edge of town
    vscr.meswins.append(Meswin(vscr, 10, vscr.height//5, vscr.width-20,
                               (vscr.height-8)*2//3, frame=True))
    game.spell = Spell(game)  # singleton
    game.dungeon = Dungeon(game)  # singleton
    game.battle = Battle(game)  # singleton
    game.chest = Chest(game)  # singleton

    dispatch(game)


if __name__ == "__main__":
    main()
