import collections
import itertools
from operator import itemgetter, attrgetter
import csv
import json
import fcntl
import termios
from enum import Enum
import tty
import struct
import sys
import os
import random
import time
import textwrap
import re
import pickle

config = {
    'floor_xmin': 76,  # 40,
    'floor_ymin': 32,  # 16,
    'max_depth': 16,
    'debug': True,
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
    MAZE, EDGE_OF_TOWN, TRAINING_GROUNDS, CASTLE, HAWTHORNE_TAVERN, TRADER_JAYS, LAKEHOUSE_INN, CAMP, BATTLE, LEAVE_GAME = range(
        10)


class Trap(Enum):
    TRAPLESS_CHEST, POISON_NEEDLE, CROSSBOW_BOLT, GAS_BOMB, STUNNER, EXPLODING_BOX, TELEPORTER, MAGE_BLASTER, PRIEST_BLASTER, ALARM = range(
        10)


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
    Job.NINJA: (17, 17, 17, 17, 17, 17, (False, False, True)),
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
                    alcls = ''.join([m.align.name[0], '-', m.job.name[:3]])
                    ac = m.ac + party.ac
                    if party.place == Place.BATTLE:
                        ac += m.acplus
                    if party.place == Place.BATTLE and \
                       m.state in [State.OK]:
                        line = f" {y} {m.name[:10].ljust(10)} {alcls} {ac:3d} {m.hp:4d} {m.action.ljust(13)}"
                    else:
                        line = f" {y} {m.name[:10].ljust(10)} {alcls} {ac:3d} {m.hp:4d} {m.state.name[:13].ljust(13)}"
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
            view_range = 2
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
            print(f"\033[{self.height};0H", end='')
            print(f"\n{party.x:03d}/{party.y:03d}, {delta:.5f}, {self.prev_vscr_view}",
                  end='', flush=True)
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
            meswidth = self.width - 6

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
        ptpl = (p.x, p.y, p.px, p.py, p.floor,
                p.light_cnt, p.ac, p.gps, p.place, p.silenced, p.identify)
        self.savedata.append(ptpl)
        mems = []  # list of names
        for mem in self.party.members:
            mems.append(mem.name)
        self.savedata.append(mems)

        if p.place in [Place.MAZE, Place.CAMP, Place.BATTLE]:
            for f in self.dungeon.floors:
                ftpl = (f.x_size, f.y_size, f.floor, f.up_x, f.up_y,
                        f.down_x, f.down_y, f.floor_data, f.floor_orig,
                        f.rooms, f.battled)
                self.savedata.append(ftpl)
            self.savedata.append(None)
        with open('savedata.pickle', 'wb') as f:
            pickle.dump(self.savedata, f)

    def load(self):
        """
        Load savedata.pickle to resume game.
        """
        with open('savedata.pickle', 'rb') as f:
            self.savedata = pickle.load(f)
        self.characters = self.savedata.pop(0)

        ptup = self.savedata.pop(0)
        self.load_party(ptup)
        mems = self.savedata.pop(0)
        self.party.members = []
        for mem in mems:
            for ch in self.characters:
                if mem == ch.name:
                    self.party.members.append(ch)

        if self.party.place not in [Place.MAZE, Place.CAMP, Place.BATTLE]:
            return

        self.dungeon.floors = []
        while True:
            ftpl = self.savedata.pop(0)
            if not ftpl:
                break
            x_size, y_size, floor, up_x, up_y, down_x, down_y, floor_data, floor_orig, rooms, battled = ftpl
            f = Floor(x_size, y_size, floor, floor_data)
            f.up_x, f.up_y = up_x, up_y
            f.down_x, f.down_y = down_x, down_y
            f.floor_orig = floor_orig
            f.floor_data = floor_data
            f.rooms = rooms
            f.battled = battled
            self.dungeon.floors.append(f)
        self.party.floor_obj = self.dungeon.floors[self.party.floor-1]

    def load_party(self, ptup):
        p = self.party
        p.x, p.y, p.px, p.py, p.floor, p.light_cnt, p.ac, p.gps, \
            p.place, p.silenced, p.identify = ptup

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
        self.x = x
        self.y = y
        self.px = x
        self.py = x
        self.floor = floor
        self.floor_move = 0  # floor move flag
        self.place = Place.EDGE_OF_TOWN
        self.floor_obj = ''
        self.members = []
        self.light_cnt = 0  # milwa=+30-45, lomilwa=+9999
        self.ac = 0  # -2 if maporfic
        self.silenced = False  # can't cast spell
        self.identify = False  # latumapic
        self.gps = False  # eternal dumapic

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

    def can_open(self, game):
        """
        Check if they can unlock the door
        Returns True if they can, False otherwise
        """
        return True  # ++++++++++++++++++++++++++++++

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
    def __init__(self, name, align, race, age):
        self.name = name
        self.align = align
        self.race = race
        self.age = age
        self.level = 1
        self.ac = 10
        self.acplus = 0  # valid only in battle
        self.job = Job.UNEMPLOYED
        self.state = State.OK
        self.silenced = False  # valid only in battle
        self.poisoned = False
        self.inspected = False  # valid only for inspecting chest
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
            f"strength {self.stat[0]:2d}  gold {self.gold:16d} lvl {self.level:5d}", start=' ')
        mw.print(
            f"    i.q. {self.stat[1]:2d}  e.p. {self.exp:16d} age {self.age:5d}", start=' ')
        mw.print(
            f"   piety {self.stat[2]:2d}  h.p.  {self.hp:7d}/{self.maxhp:7d} a.c.{self.ac:5d}", start=' ')
        mw.print(
            f"vitality {self.stat[3]:2d}  rip  {self.rip:7d}     marks {self.marks:8d}", start=' ')
        mw.print(f" agility {self.stat[4]:2d}", start=' ')
        mw.print(
            f"    luck {self.stat[5]:2d}  status {self.state.name}", start=' ')
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
        while True:
            self.disp_character(game)
            mw.print(f"", start=' ')
            c1 = mw.input_char("i)tems s)pells jk)change member l)leave",
                               values=['i', 's', 'j', 'k', 'l'])
            if c1 == 'l':
                mw.cls()
                return 0  # leave
            elif c1 == 'i':
                self.item_menu(game)
            elif c1 == 's':
                self.spell_menu(game)
            elif c1 == 'j':
                return 1  # next member
            elif c1 == 'k':
                return -1  # previous member

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
            sw.print("Hit any key.")
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
        sw.cls()
        v.disp_scrwin()
        v.meswins.pop()

    def spell_menu(self, game):
        """
        Spell menu.  Cast, read spells.
        """
        v = game.vscr
        mw = Meswin(v, 14, 4, 44, 12, frame=True)
        v.meswins.append(mw)
        while True:
            mw.print("Spell memu:")
            c = mw.input_char("c)ast spell v)iew list l)eave",
                              values=['c', 'v', 'l'])
            if c == 'l':
                break
            elif c == 'c':
                game.spell.cast_spell(self)
            elif c == 'v':
                self.view_spells(game)
        mw.cls()
        v.disp_scrwin()
        v.meswins.pop()

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
                if game.itemdef[self.items[inum][0]].curse:
                    self.items[inum][2] = True  # cursed
                    iw.print("Cursed!")
                    vscr.disp_scrwin()
                    getch()
                self.items[inum][1] = True  # equipped
                self.calc_ac(game)
                vscr.meswins.pop()
                vscr.disp_scrwin()
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
        mw.print("Distribute bonus points")
        mw.print("  h)minus j)down k)up l)plus .)change bonus x)done\n", start=' ')
        mw.print(f"strength  {sp[0]+self.stat[0]:2d}", start=' ')
        mw.print(f"iq        {sp[1]+self.stat[1]:2d}", start=' ')
        mw.print(f"piety     {sp[2]+self.stat[2]:2d}", start=' ')
        mw.print(f"vitality  {sp[3]+self.stat[3]:2d}", start=' ')
        mw.print(f"agility   {sp[4]+self.stat[4]:2d}", start=' ')
        mw.print(f"luck      {sp[5]+self.stat[5]:2d}", start=' ')
        mw.print(f"\nbonus     {bonus:2d}", start=' ')
        mw.print
        mw.mes_lines[y+3] = mw.mes_lines[y+3][:11] + \
            '>' + mw.mes_lines[y+3][12:]
        line = ''
        job = False
        for jobnum in range(8):
            if self.job_applicable(sp, jobnum):
                job = True
                line = ''.join([line, Job(jobnum).name[:].lower(), ' '])
        mw.print(line)
        vscr.disp_scrwin()
        return job

    def distribute_bonus(self, game):
        """
        Bonus assignment and deciding class main routine
        """
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
            elif c == 'l' and statplus[y]+self.stat[y] < 18 and bonus > 0:
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


class Spell:
    """
    Has actual spell implementation here
    """

    def __init__(self, game):
        self.game = game

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
            mw.print("What?")
            return
        elif s not in list(itertools.chain(mem.mspells, mem.pspells)):
            mw.print("Haven't mastered the spell.")
            return

        sdef = game.spelldef[s]
        if game.party.place == Place.BATTLE:
            if not sdef.battle:
                mw.print("Can't cast now.")
                return
        elif not sdef.camp:  # note: you can use it at tavern, too.
            mw.print("Can't cast it now.")
            return

        if sdef.categ == 'mage':
            splcntlst = mem.mspell_cnt
        else:
            splcntlst = mem.pspell_cnt
        if splcntlst[sdef.level-1] <= 0:
            mw.print("MP exhausted.")
            return

        if sdef.target == 'member':
            target = self.game.party.choose_character(self.game)
            if target is False:
                mw = self.game.vscr.meswins[-1]
                mw.print("Aborted.")
                return
        elif sdef.target in ['enemy', 'group']:
            gnum = self.game.battle.choose_group()
            target = self.game.battle.monp[gnum]
        else:
            target = sdef.target

        splcntlst[sdef.level-1] -= 1

        mw.print(f"{mem.name} started casting {s}")
        v.disp_scrwin()
        self.cast_spell_dispatch(mem, s, target)

    def cast_spell_dispatch(self, invoker, spell, target):
        sdef = self.game.spelldef[spell]
        if sdef.type == 'heal':
            self.heal(invoker, spell, target)
        elif sdef.type == 'attack':
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
                mw.print(f"{target.name} is awaken.")
                v.disp_scrwin()
        elif spell == 'gedoku':
            if target.poisoned:
                target.poisoned = False
                mw.print(f"{target.name} is cured.")
                v.disp_scrwin()

    def etc(self, invoker, spell, target):
        v = self.game.vscr
        mw = v.meswins[-1]
        spelldef = self.game.spelldef[spell]
        if spell == 'gps':
            self.game.party.gps = True
        elif spell == 'shikibetsu':
            self.game.party.identify = True
        elif spell == 'hogo':
            self.game.party.ac = int(spelldef.value)
        elif spell == 'akari':
            self.game.party.light_cnt += random.randrange(15) + 30
        elif spell == 'hikarinotama':
            self.game.party.light_cnt += 9999
        elif spell == 'kanzen':
            if target.state not in {State.DEAD, State.ASHED, State.LOST}:
                target.hp = target.maxhp
                target.state = State.OK
                mw.print(f"{target.name} is completely healed.")
        elif spell == 'zakoisso':
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
                    mw.print(f"{dispname} are perished.", start=' ')
                    self.game.battle.monp.remove(mong)
                    v.disp_scrwin()

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
                mem.ac += int(spelldef.value)
        elif spelldef.target == 'group':
            if isinstance(invoker, Member):
                for mon in target.monsters:
                    mon.ac += int(spelldef.value)
            else:
                for mem in self.game.party.members:
                    mem.ac += int(spelldef.value)
        else:  # 'all'
            if isinstance(invoker, Member):
                for mong in self.game.battle.monp:
                    for mon in mong:
                        mon.ac += int(spelldef.value)
            else:
                for mem in self.game.party.members:
                    mem.ac += int(spelldef.value)

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
                       random.randrange(100) < mon.mdef.regspellp:
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

    def attack(self, invoker, spell, target):
        v = self.game.vscr
        mw = v.meswins[-1]
        spelldef = self.game.spelldef[spell]
        if not isinstance(invoker, Member):
            if spelldef.target == 'enemy':
                mem = random.choice(self.game.party.members)
                damage = dice(spelldef.value)
                mw.print(f"{mem.name} incurred {damage} damage.", start=' ')
                v.disp_scrwin()
                mem.hp = max(0, mem.hp - dice(spelldef.value))
                if mem.hp <= 0 and \
                   mem.state not in [State.DEAD, State.ASHED, State.LOST]:
                    mem.state = State.DEAD
                    mw.print(f"{mem.name} is killed.", start=' ')
            else:  # 'group' or 'all
                for mem in self.game.party.members:
                    mem = random.choice(self.game.party.members)
                    damage = dice(spelldef.value)
                    mw.print(
                        f"{mem.name} incurred {damage} damage.", start=' ')
                    mem.hp = max(0, mem.hp - dice(spelldef.value))
                    if mem.hp <= 0 and \
                       mem.state not in [state.DEAD, State.ASHED, State.LOST]:
                        mem.state = State.DEAD
                        mw.print(f"{mem.name} is killed.", start=' ')
            return
        if spelldef.target == 'group':
            if target.identified:
                disptarget = target.name
            else:  # unidentified
                disptarget = self.game.mondef[target.name].unident
            for mon in target.monsters:
                self.attack_single(mon, disptarget,
                                   spelldef.value, spelldef.attr, target)
        elif spelldef.target == 'all':
            for mong in self.game.battle.monp:
                if mong.identified:
                    disptarget = mong.name
                else:
                    disptarget = self.game.mondef[mong.name].unident
                for mon in mong.monsters:
                    self.attack_single(mon, disptarget,
                                       spelldef.value, spelldef.attr, mong)
        elif spelldef.target == 'enemy':
            if target.identified:
                disptarget = target.name
            else:
                disptarget = self.game.mondef[target.name].unident
            self.attack_single(target.monsters[0], disptarget,
                               spelldef.value, spelldef.attr, target)
        monptmp = self.game.battle.monp[:]
        for mong in monptmp:
            mongtmp = mong.monsters[:]
            for mon in mongtmp:
                if mon.hp <= 0:
                    mong.monsters.remove(mon)
            if not mong.monsters:
                self.game.battle.monp.remove(mong)

    def attack_single(self, mon, dispname, value, attr, mong):
        if mon.state == State.DEAD:
            return
        v = self.game.vscr
        mw = v.meswins[-1]
        damage = dice(value)
        mondef = self.game.mondef[mon.name]
        if 'fire' in attr:
            if mondef.regfire:
                damage = damage // 2
        elif 'cold' in attr:
            if mondef.regcold:
                damage = damage // 2
        if 'poison' in attr:
            if not mondef.regpoison and random.randrange(100) < 50:
                mon.poisoned = True
                mw.print(f"{dispname} was poisoned.")
        mon.hp = max(mon.hp-damage, 0)
        mw.print(f"{dispname} incurred {damage} damage.", start=' ')
        if mon.hp <= 0:
            mw.print(f"{dispname} is killed.", start=' ')
            mon.state = State.DEAD
            self.game.battle.exp += mondef.exp

    def heal(self, invoker, spell, target):
        sdef = self.game.spelldef[spell]
        if not isinstance(invoker, Member):
            if sdef.target == 'party':
                for mon in self.monp[0]:
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
        self.floors = []

    def generate_floor(self, floor):
        """
        Generate a dungeon floor.
        Create rooms, connect among them and place doors
        """
        floor_x_size = config['floor_xmin']  # ++++++++++++++++++++++++++++++
        floor_y_size = config['floor_ymin']
        floor_data = bytearray(b'#' * floor_x_size *
                               floor_y_size)  # rock only floor
        floor_obj = Floor(floor_x_size, floor_y_size, floor, floor_data)

        rooms = floor_obj.prepare_rooms()
        for r in rooms:
            for y in range(r.y_size):
                start = (r.y + y)*floor_x_size + r.x
                floor_obj.floor_view[start:start+r.x_size] = b'.'*r.x_size
        floor_obj.connect_all_rooms(rooms)
        floor_obj.place_doors(rooms)
        floor_obj.rooms = rooms
        floor_obj.floor_orig = floor_obj.floor_data
        floor_obj.floor_data = bytearray(b'^' * floor_x_size * floor_y_size)
        return floor_obj

    def move_floor(self, floor_obj):
        """
        Check and move to a upper/lower floor.  Generate floor_obj if
        not created yet.  Exit from dungeon.

        Return floor_obj.  Return None if exit from dungeon.
        """
        game = self.game
        party = game.party
        vscr = game.vscr
        meswin = vscr.meswins[0]

        if floor_obj:
            if floor_obj.get_tile(party.x, party.y) == b'<':  # upstairs
                vscr.disp_scrwin(floor_obj)
                if party.floor == 1:
                    c = meswin.input_char("Exit from dungeon? (y/n)",
                                          values=['y', 'n'])
                else:
                    c = meswin.input_char(
                        "Stairs.  Go up? (y/n)", values=['y', 'n'])
                if c == 'y':
                    party.floor -= 1
                    party.floor_move = 2  # go up
                    if party.floor > 0:
                        vscr.disp_scrwin(floor_obj)
            elif floor_obj.get_tile(party.x, party.y) == b'>':  # downstairs
                vscr.disp_scrwin(floor_obj)
                c = meswin.input_char(
                    "Stairs.  Go down? (y/n)", values=['y', 'n'])
                if c == 'y':
                    party.floor += 1
                    party.floor_move = 1  # go down
                    vscr.disp_scrwin(floor_obj)
            vscr.disp_scrwin(floor_obj)

        if party.floor_move:
            if party.floor <= 0:  # exit from dungeon
                party.place = Place.EDGE_OF_TOWN
                return None  # Exit from dungeon

            floor_obj = None
            for f in self.floors:
                if f.floor == party.floor:
                    floor_obj = f
            if not floor_obj:
                floor_obj = self.generate_floor(party.floor)
                self.floors.append(floor_obj)
            if party.floor_move == 1:
                party.x = floor_obj.up_x
                party.y = floor_obj.up_y
            elif party.floor_move == 2:
                party.x = floor_obj.down_x
                party.y = floor_obj.down_y
            party.floor_move = 0
            vscr.disp_scrwin(floor_obj)

        return floor_obj


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

    def __repr__(self):
        s = self.floor_data.decode()
        return f"Floor(size: {self.x_size}x{self.y_size}, floor: {self.floor} - {s})"

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
        if bc in b"*+#^":
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
        for _ in range(256):
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

    def place_doors(self, rooms):
        """
        Place locked or unlocked doors in front of rooms.
        """
        for r in rooms:
            dc = b'+'  # door character
            if random.randrange(10) == 0:  # 10%
                dc = b'*'  # locked door
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
        self.mw = Meswin(game.vscr, 14, 6, 44, 12, frame=True)
        self.ew = Meswin(game.vscr, 14, 1, 44, 4, frame=True)

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
        candidates = []
        for mname in self.game.mondef:
            if self.game.party.floor in self.game.mondef[mname].floors:
                candidates.append(mname)
        mname = random.choice(candidates)
        if mname == '':
            breakpoint()
        self.friendly = False
        # self.monp = []
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
                elif action == 'atk':
                    if len(party.members) > 3:
                        if party.floor > 3 and random.randrange(100) < 40:
                            target = random.choice(party.members)
                        else:
                            target = party.members[random.randrange(3)]
                    else:
                        target = random.choice(party.members)
                    self.entities.append(
                        Entity(mon, mong.name, mong, agi, 'fight', target))
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
        while True:
            self.mw.print(f"Options - f)ight s)pell")
            self.mw.print(f"u)se p)arry r)un t)ake back", start=' ')
            for idx, mem in enumerate(self.game.party.members, 1):
                if mem.state not in [State.OK]:
                    continue
                while True:
                    c = self.mw.input_char(f"{mem.name}'s action?",
                                           values=['f', 's', 'u', 'p', 'r', 't'])
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
                    elif c == 's':
                        s, target = self.choose_spell(mem)
                        self.entities.append(
                            Entity(mem, mem.name, None, agi, s, target))
                        mem.action = s
                        self.game.vscr.disp_scrwin()
                        break
                    elif c == 'u':
                        item, target = self.choose_item(mem)
                        if item is False:
                            continue
                        self.entities.append(
                            Entity(mem, mem.name, None, agi, item, target))
                        mem.action = item
                        self.game.vscr.disp_scrwin()
                        break
                if c == 't':
                    break
            if c != 't':
                self.mw.print("hit any key or t)ake back >")
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
                if m is False:
                    return False, None
                return iname, m
            elif target in ['group', 'enemy']:
                mong = self.monp[self.choose_group()]
                return iname, mong
        return iname, None

    def monster_attack(self, e):
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
                if 'poison' not in regist:
                    e.target.poisoned = True
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

        if e.target.drained is False and self.game.mondef[e.name].drain > 0:
            if (e.target.stat[5]+1)*100//20 < random.randrange(100):
                if 'drain' not in regist:
                    prevlevel = e.target.level
                    e.target.level -= self.game.mondef[e.name].drain
                    self.mw.print(
                        f"{e.target.name} is drained by {self.game.mondef[e.name].drain} level.")
                    if e.target.level < 1:
                        e.target.hp = 0
                        e.target.state = State.LOST
                        self.mw.print(f"{e.target.name} is lost.")
                        return
                    e.target.maxhp -= \
                        e.target.maxhp * \
                        (prevlevel - self.game.mondef[e.name].drain) \
                        // prelevel
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
                        self.mw.print(f"{e.target.name} is decapitated.")

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
            atkcnt = max(1, weapat)
        if atkcnt > 10:
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
        if e.target.monsters[0] != State.OK:
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
            v.meswins.pop()
            v.meswins.pop()
            self.game.party.place = place
            return

        while True:
            for m in self.game.party.members:
                m.action = '????????????'
            self.recover_state()
            self.reorder_party()
            self.identify_check()
            self.draw_ew()
            v.disp_scrwin()
            if self.input_action():
                self.mw.print("Ran away from the battle.")
                v.disp_scrwin()
                self.game.party.x, self.game.party.px =\
                    self.game.party.px, self.game.party.x
                self.game.party.y, self.game.party.py =\
                    self.game.party.py, self.game.party.y
                self.ran = True
                break  # ran successfully
            self.enemy_action()

            self.entities.sort(key=attrgetter('agi'), reverse=True)
            for e in self.entities:
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
                elif e.action == 'breath':
                    self.mw.print(f"{dispname} breathed on the party.")
                    for mem in self.game.party.members:
                        damage = e.entity.hp // 2
                        mem.hp = max(0, mem.hp - damage)
                        self.mw.print(f"{mem.name} incurred {damage} damage.",
                                      start=' ')
                        if mem.hp <= 0 and mem.state not in \
                           [State.DEAD, State.ASHED, State.LOST]:
                            mem.state = State.DEAD
                            self.mw.print(f"{mem.name} is killed.",
                                          start=' ')
                elif e.action == 'fight':
                    if isinstance(e.entity, Member):
                        self.member_attack(e)
                    else:
                        self.monster_attack(e)
                elif e.action == 'run':  # monster only
                    if self.canrun(e.entity):
                        e.group.monsters.remove(e.entity)
                        self.mw.print(f"{dispname} ran away")
                        if not e.group.monsters:
                            self.monp.remove(e.group)
                        self.draw_ew()
                    else:
                        self.mw.print(f"{dispname} tried to run away")
                        self.mw.print(f".. but wasn't able to.", start=' ')
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
                v.disp_scrwin()
                getch(wait=True)

            # Battle end?
            if not self.monp:
                survnum = sum(1 for m in self.game.party.members
                              if m.state in [State.OK, State.ASLEEP,
                                             State.PARALYZED])
                self.mw.print(f"Each survivor gets {self.exp//survnum} ep.",
                              start=' ')
                self.mw.print(f"Each survivor gets {self.gold//survnum} gold.",
                              start=' ')
                for mem in self.game.party.members:
                    if mem.state in [State.OK, State.ASLEEP, State.PARALYZED]:
                        mem.exp += self.exp//survnum
                        mem.gold += self.gold//survnum
                party = self.game.party
                for idx, room in enumerate(party.floor_obj.rooms):
                    if room.in_room(party.x, party.y):
                        party.floor_obj.battled[idx] = True
                        break
                v.disp_scrwin()
                break

        v.disp_scrwin()
        getch()

        v.meswins.pop()
        v.meswins.pop()
        self.game.party.place = place
        return

    def recover_state(self):
        v = self.game.vscr
        mw = v.meswins[-1]
        for mem in self.game.party.members:
            if mem.state == State.ASLEEP and random.randrange(100) < 50:
                mem.state = State.OK
        for mong in self.monp:
            for mon in mong.monsters:
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
        (3 if event battle?)
        """
        party = self.game.party
        rooms = party.floor_obj.rooms
        for idx, room in enumerate(rooms):
            if idx == 0:
                continue
            if room.in_room(party.x, party.y) \
               and party.floor_obj.battled[idx] is False:
                if random.randrange(20) > 0:
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


class Chest:
    def __init__(self, game):
        self.game = game
        self.mw = Meswin(game.vscr, 14, 3, 44, 10, frame=True)
        self.trap = Trap.TRAPLESS_CHEST
        self.items = None

    def chest(self):
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
                if mem is False:
                    continue
                r = random.randrange(4)
                if r > mem.level // 256:
                    self.trap_activated(mem)
                self.treasure()
                v.meswins.pop()
                return
            elif c == 'd':  # disarm
                mem = game.party.choose_character(game)
                if mem is False:
                    continue
                ans = mw.input("Trap name?")
                if ans == self.trap.name.lower().replace('_', ' '):
                    if mem.job in [Job.THIEF, Job.NINJA]:
                        chance = mem.level - game.party.floor + 50
                    else:
                        chance = mem.level - game.party.floor
                    if random.randrange(70) < chance:
                        self.treasure()
                        v.meswins.pop()
                        return
                    if random.randrange(20) < mem.stat[4]:  # agility
                        mw.print("Failed to disarm.")
                        v.disp_scrwin()
                        continue
                    self.trap_activated(mem)
                    self.treasure()
                    v.meswins.pop()
                    return
            elif c == 'k':  # calfo
                mem = game.party.choose_character(game)
                if mem is False:
                    continue
                if 'kantei' in mem.pspells and mem.pspell_cnt[1]:
                    mem.pspell_cnt[1] -= 1
                    mw.print(f"{mem.name} casted kantei.")
                    if random.randrange(100) < 95:
                        ans = self.trap
                    else:
                        ans = self.choose_trap()
                    mw.print(f"It is {ans.name.lower().replace('_', ' ')}.")
                else:
                    mw.print(f"{mem.name} failed to cast kantei.")
                v.disp_scrwin()
                getch(wait=True)
            elif c == 'i':  # inspect
                mem = game.party.choose_character(game)
                if mem is False:
                    continue
                if mem.inspected:
                    mw.print("Already inspected.")
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
                mw.print(f"It is {ans.name.lower().replace('_', ' ')}.")
                v.disp_scrwin()
                getch(wait=True)

    def treasure(self):
        if len(self.items) > 0:
            if random.randrange(100) < 80:  # 80%
                item = self.choose_item(self.items[0])
                self.get_item(item)
            self.items.pop(0)
        if len(self.items) > 0:
            if random.randrange(100) < 40:  # 40%
                item = self.choose_item(self.items[0])
                self.get_item(item)
            self.items.pop(0)
        if len(self.items) > 0:
            if random.randrange(100) < 8:  # 8%
                item = self.choose_item(self.items[0])
                self.get_item(item)
            self.items.pop(0)
        if len(self.items) > 0:
            if random.randrange(100) < 1:  # 1%
                item = self.choose_item(self.items[0])
                self.get_item(item)

    def choose_item(self, item_lvl):
        items = []
        for item in self.game.itemdef:
            if self.game.itemdef[item].level == item_lvl:
                items.append(item)
        item = random.choice(items)
        return item

    def get_item(self, item):
        v = self.game.vscr
        mw = v.meswins[-1]
        mem = random.choice(
            [mem for mem in self.game.party.members if len(mem.items) < 8])
        mem.items.append([item, False, False, True])
        mw.print(
            f"{mem.name} found {self.game.itemdef[item].unident}", start=' ')
        v.disp_scrwin()
        getch(wait=True)

    def trap_activated(self, mem):
        game = self.game
        v = game.vscr
        mw = self.mw
        mw.print(f"Oops, {self.trap.name.lower().replace('_', ' ')}!")
        if self.trap == Trap.POISON_NEEDLE:
            mem.poisoned = True
            mw.print(f"{mem.name} was poisoned.")
        elif self.trap == Trap.GAS_BOMB:
            for m in game.party.members:
                if random.randrange(100) < 50:
                    m.poisoned = True
                    mw.print(f"{m.name} was poisoned.")
        elif self.trap == Trap.CROSSBOW_BOLT:
            damage = dice('1D8')*game.party.floor
            mem.hp = max(mem.hp-damage, 0)
            mw.print(f"{mem.name} incurred {damage} damage.")
            if mem.hp <= 0:
                mem.state = State.DEAD
                mw.print(f"{mem.name} is killed.")
        elif self.trap == Trap.EXPLODING_BOX:
            for m in game.party.members:
                if random.randrange(100) < 75 and \
                   m.state not in [State.DEAD, State.ASHED, State.LOST]:
                    if random.randrange(100) < 67:
                        damage = dice('1D5') * game.party.floor
                    else:
                        damage = dice('1D8') * game.party.floor
                    m.hp = max(m.hp-damage, 0)
                    mw.print(f"{m.name} incurred {damage} damage.")
                if m.hp <= 0:
                    m.state = State.DEAD
                    mw.print(f"{m.name} is killed.")
        elif self.trap == Trap.STUNNER:
            mem.state = State.PARALYZED
            mw.print(f"{m.name} got stunned.")
        elif self.trap == Trap.TELEPORTER:
            party.x = random.randrange(game.party.floor.x_size)
            party.y = random.randrange(game.party.floor.y_size)
        elif self.trap == Trap.ALARM:
            party.alarm = True
        elif self.trap == Trap.MAGE_BLASTER:
            for m in game.party.members:
                if m.job == Job.MAGE:
                    if random.randrange(20) >= m.stat[5]:
                        if m.state in [State.OK]:
                            m.state = State.PARALYZED
                            mw.print(f"{m.name} is paralyzed.")
                    else:
                        if m.state in [State.OK, State.PARALYZED]:
                            m.state = State.STONED
                            mw.print(f"{m.name} is petrified.")
                elif m.job == Job.SAMURAI:
                    if random.randrange(20) >= m.stat[5]:
                        if m.state in [State.OK]:
                            m.state = State.PARALYZED
                            mw.print(f"{m.name} is paralyzed.")
        elif self.trap == Trap.PRIEST_BLASTER:
            for m in game.party.members:
                if m.job == Job.PRIEST:
                    if random.randrange(20) >= m.stat[5]:
                        if m.state in [State.OK]:
                            m.state = State.PARALYZED
                            mw.print(f"{m.name} is paralyzed.")
                    else:
                        if m.state in [State.OK, State.PARALYZED]:
                            m.state = State.STONED
                            mw.print(f"{m.name} is petrified.")
                elif m.job == Job.LORD:
                    if random.randrange(20) >= m.stat[5]:
                        if m.state in [State.OK]:
                            m.state = State.PARALYZED
                            mw.print(f"{m.name} is paralyzed.")

    def choose_trap(self):
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
    if ch == 'Q' and config['debug'] == True:
        sys.exit()
    return ch


def dice(valstr):
    pattern = r"(\d+)[dD](\d+)(\+(\d+))?"
    m = re.search(pattern, valstr)
    total = 0
    if m[4] is None:
        plus = 0
    else:
        plus = int(m[4])
    for _ in range(int(m[1])):
        total += random.randint(1, int(m[2])) + plus
    return total


def create_character(game):
    """
    Create a character (a training grounds menu item)
    """
    vscr = game.vscr
    mw = vscr.meswins[-1]
    while True:
        if (name := mw.input("Enter new name")):
            if name in [char.name for char in game.characters]:
                mw.print("The name is already used")
                vscr.disp_scrwin()
            else:
                break
    vscr.disp_scrwin()

    c = mw.input_char("Choose race - h)uman e)lf d)warf g)nome o)hobbit",
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

    while True:
        age = mw.input("How old is he/she? (13-199)")
        try:
            age = int(age)
            if 12 < age < 200:
                break
        except:
            pass
        vscr.disp_scrwin()
    mw.print(f"{age} years old.")
    vscr.disp_scrwin()

    ch = Member(name, align, race, age)
    ch.distribute_bonus(game)


def inspect_characters(game):
    """
    Inspect characters (a training grounds menu item)
    Can delete a character from here, too.
    """
    vscr = game.vscr
    mw = vscr.meswins[-1]
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
            "*** training grounds ***\nc)reate a character\ni)nspect a character\nl)eave")
        vscr.disp_scrwin()
        c = mw.input_char("Command?")
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
            ch for ch in game.characters if ch not in game.party.members]
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
    vscr.disp_scrwin()


def tavern(game):
    """
    tavern (a castle item)
    add/remove members to the party, inspect, divide golds, etc.
    """
    game.party.place = Place.HAWTHORNE_TAVERN
    vscr = game.vscr
    mw = vscr.meswins[-1]
    ch = ''
    while True:
        mw.print("*** The Hawthorne Tavern ***")
        vscr.disp_scrwin()
        ch = mw.input_char("Command? - a)dd r)emove i)nspect d)ivvy gold l)eave",
                           values=['a', 'r', 'i', 'd', 'l'])
        if ch == 'l':
            game.party.place = Place.CASTLE
            break
        elif ch == 'a':
            if len(game.party.members) < len(game.characters):
                tavern_add(game)
            else:
                mw.print("No characters to add")
        elif ch == 'i':
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


def trader_buy(game, mem):
    """
    a member chooses and buys items from shop inventory
    """
    vscr = game.vscr
    iw = Meswin(vscr, 12, 1, 41, 12)
    vscr.meswins.append(iw)
    top = idx = page = 0
    pages = ('weapon', 'armor', 'shield', 'helm', 'gloves',
             'ring', 'item')
    while True:
        items = [item for item in game.shopitems if game.shopitems[item] > 0
                 and game.itemdef[item].type == pages[page]]
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
            iline = f"| {cur}{i+1:2} {item.ljust(21)[:21]} {game.itemdef[item].price:10d}{canequip}{afford}|"
            ilines.append(iline)
        iw.mes_lines = []
        iw.mes_lines.append(
            f"| {mem.name} has {mem.gold} gold".ljust(40)+'|')
        iw.mes_lines.append("|  jk)cursor x)choose hl)page ;)leave   |")
        for il in ilines[top:top+iw.height-2]:
            iw.mes_lines.append(il.ljust(iw.width-1))
        for _ in range(iw.width - len(iw.mes_lines)):
            iw.mes_lines.append(''.join(['|', ' '*(iw.width-2), '|']))
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
                iw.mes_lines[0] = "| Looks like, your bag is full.".ljust(
                    iw.width-1)+'|'
                vscr.disp_scrwin()
                getch()
            elif mem.gold < game.itemdef[items[idx]].price:
                iw.mes_lines[0] = "| Sorry, you can't afford it.".ljust(
                    iw.width-1)+'|'
                #iw.mes_lines[1] = f"{mem.gold} < {game.itemdef[items[idx]][10]}"
                vscr.disp_scrwin()
                getch()
            else:
                iw.mes_lines[0] = "| Anything else, noble sir?".ljust(
                    iw.width-1)+'|'
                mem.gold -= game.itemdef[items[idx]].price
                bought = [items[idx], False, False, False]
                mem.items.append(bought)
                game.shopitems[items[idx]] -= 1
                vscr.disp_scrwin()
                getch()
    vscr.meswins.pop()


def trader_sell(game, mem, op):
    """
    sell, uncurse or identify items
    """
    vscr = game.vscr
    mw = vscr.meswins[-1]
    if op == 's':
        opword = 'sell'
    elif op == 'u':
        opword = 'uncurse'
    else:
        opword = 'identify'

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
            if item[2] or item[3]:
                continue
            if item[1]:  # equipped
                mark = '*'
        price = game.itemdef[item[0]].price//2
        mw.print(
            f"{i}){mark}{dispname.ljust(16)}{price}",
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
    game.shopitems[idic[int(c)][0]] += 1
    price = idic[int(c)][2]
    if op == 's':
        mem.gold += price
        del mem.items[int(c)-1]
        mw.print("I'm sure fellows'll want it.")
    elif op == 'i':
        mem.gold -= price
        mem.items[int(c)-1][3] = False  # identified
        mw.print(f"Identified as {mem.items[int(c)-1][0]}.")
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
    game.party.place = Place.TRADER_JAYS
    vscr = game.vscr
    mw = vscr.meswins[-1]
    while True:
        mw.print("*** Trader Jay's ***")
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
        if m.level <= 13:
            next = level_table[m.job][m.level-1]
        else:
            next = level_table[m.job][11] + \
                level_table[m.job][12]*(m.level-12)
        if next > m.exp:
            return levelup, learned

        levelup += 1

        for i in range(6):
            r = random.randrange(100)
            if r < 20:  # 20%
                m.stat[i] -= 1
            elif r > 60:  # 40%
                m.stat[i] += 1
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

        if m.job == Job.MAGE:
            sc = game.spell.spell_counts(0, 2, m.level)
            for i in range(len(sc)):
                m.mspell_max[i] = max(sc[i], m.mspell_max[i])
        elif m.job == Job.PRIEST:
            sc = game.spell.spell_counts(0, 2, m.level)
            for i in range(len(sc)):
                m.pspell_max[i] = max(sc[i], m.pspell_max[i])
        elif m.job == Job.BISHOP:
            sc = game.spell.spell_counts(0, 4, m.level)
            for i in range(len(sc)):
                m.mspell_max[i] = max(sc[i], m.mspell_max[i])
            sc = game.spell.spell_counts(3, 4, m.level)
            for i in range(len(sc)):
                m.pspell_max[i] = max(sc[i], m.pspell_max[i])
        elif m.job == Job.SAMURAI:
            sc = game.spell.spell_counts(3, 3, m.level)
            for i in range(len(sc)):
                m.mspell_max[i] = max(sc[i], m.mspell_max[i])
        elif m.job == Job.LORD:
            sc = game.spell.spell_counts(3, 2, m.level)
            for i in range(len(sc)):
                m.pspell_max[i] = max(sc[i], m.pspell_max[i])

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
    v = game.vscr
    mw = v.meswins[-1]
    num = len(game.party.members)
    gold = sum(m.gold for m in game.party.members)
    mw.print("*** The Lakehouse Inn ***")
    mw.print(f"Welcome.  You must be very tired.", start=' ')
    mw.print(f"You have {gold} gold in total.", start=' ')
    mw.print(f"c)ots                {2*num:4d} gold", start=' ')
    mw.print(f"s)tandard rooms      {20*num:4d} gold", start=' ')
    mw.print(f"d)elux rooms         {50*num:4d} gold", start=' ')
    mw.print(f"v)lake view suites   {200*num:4d} gold", start=' ')
    mw.print(f"p)residential suites {500*num:4d} gold", start=' ')
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
                                'chiken pho', 'dana masala'])
    elif c == 'd':
        uprice = 50
        dinner = random.choice(['grilled sword fish', 'ribeye steak',
                                'sushi', 'lamb chops', 'fillet mignon'])
    elif c == 'v':
        uprice = 200
        dinner = "wine and chef's special"
    else:  # presidential suites
        uprice = 500
        dinner = 'supreme course w/ champagne'
    if not game.party.pay(uprice*num):
        mw.print("You can't afford the room.")
        v.disp_scrwin()
        return
    mw.print(f"Today's dinner is {dinner}.")
    for mem in game.party.members:
        sleep(game, mem, uprice*2)


def hospital(game):
    v = game.vscr
    mw = v.meswins[-1]
    num = len(game.party.members)
    gold = sum(m.gold for m in game.party.members)
    pricing = {
        State.PARALYZED: 50,
        State.STONED: 100,
        State.DEAD: 200,
        State.ASHED: 500,
    }
    mw.print("*** Moss General Hospital ***")
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
        mw.print("*** Castle ***")
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
        mw.print("*** Edge of Town ***")
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
            game.load()
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

    while True:
        mw.print("*** Camp ***\ni)nspect\nS)ave and quit game\nl)eave")
        c = mw.input_char("Command?", values=['i', 'S', 'l'])
        if c == 'l':
            break
        elif c == 'S':
            game.party.place = Place.MAZE
            game.save()
            mw.print("Thank you for playing.")
            mw.print("See you again soon.")
            v.disp_scrwin()
            sys.exit()
        elif c == 'i':
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

    if not party.floor_obj:
        party.place = Place.MAZE
        party.floor = 1
        party.floor_move = 1  # 0: no, 1: down, 2: up

        game.dungeon.floors = []
        floor_obj = None
        party.floor_obj = floor_obj
    else:
        floor_obj = party.floor_obj

    while True:
        floor_obj = dungeon.move_floor(floor_obj)
        party.floor_obj = floor_obj
        if not floor_obj:  # Exit from dungeon
            mlist = party.members[:]
            for mem in mlist:
                if mem.state in [State.PARALYZED, State.STONED, State.DEAD,
                                 State.ASHED]:
                    party.members.remove(mem)
                    # Carried away in an ambulance
                    game.hospitalized.append(mem)
            break

        if party.light_cnt > 0:  # milwa/lomilwa counter
            party.light_cnt -= 1

        rtn = game.battle.check_battle()
        if rtn:  # 1 or 2 (or 3?) if battle
            meswin.print("*** encounter ***")
            vscr.disp_scrwin(floor_obj)
            getch()
            game.battle.battle()
            if rtn == 2 and not game.battle.ran:  # room battle
                game.chest.chest()
            meswin.print("battle ended.")
            vscr.disp_scrwin(floor_obj)

        c = getch(wait=True)
        draw = True
        if c:
            if c == 'c':
                camp(game, floor_obj)
            elif c in 'hH' and party.x > 0:
                if (c == 'H' and config['debug']) or \
                   floor_obj.can_move(party.x-1, party.y):
                    party.px = party.x
                    party.py = party.y
                    party.x -= 1
                    meswin.print("west")
            elif c in 'kK' and party.y > 0:
                if (c == 'K' and config['debug']) or \
                   floor_obj.can_move(party.x, party.y-1):
                    party.px = party.x
                    party.py = party.y
                    party.y -= 1
                    meswin.print("north")
            elif c in 'jJ' and party.y < floor_obj.y_size-1:
                if (c == 'J' and config['debug']) or \
                   floor_obj.can_move(party.x, party.y+1):
                    party.px = party.x
                    party.py = party.y
                    party.y += 1
                    meswin.print("south")
            elif c in 'lL' and party.x < floor_obj.x_size-1:
                if (c == 'L' and config['debug']) or \
                   floor_obj.can_move(party.x+1, party.y):
                    party.px = party.x
                    party.py = party.y
                    party.x += 1
                    meswin.print("east")
            elif c == 'o':  # open or unlock door
                vscr.disp_scrwin(floor_obj)
                floor_obj.open_door(game, meswin)
            elif c == '.':
                meswin.print('.')
                vscr.disp_scrwin()
            elif c == '>' and config['debug']:
                party.floor += 1
                party.floor_move = 1  # go down
            elif c == '<' and config['debug']:
                party.floor = min(party.floor-1, 1)
                party.floor_move = 2  # go up
            elif c == 'S' and config['debug']:
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
    # vscr = Vscr(w, h)  # singleton
    vscr = Vscr(80, 25)  # +++++++++++++++
    game.vscr = vscr
    vscr.game = game
    vscr.meswins.append(Meswin(vscr, 42, 18, 40, 7))  # meswin for scrollwin
    # meswin for castle/edge of town
    vscr.meswins.append(Meswin(vscr, 10, 1, 64, 17, frame=True))
    game.spell = Spell(game)  # singleton
    game.dungeon = Dungeon(game)  # singleton
    game.battle = Battle(game)  # singleton
    game.chest = Chest(game)  # singleton

    """
    m = Member("Alex", Align.GOOD, Race.DWARF, 32)
    m.job = Job.FIGHTER
    m.stat = [18, 10, 5, 11, 13, 11]
    m.maxhp = m.hp = 13
    m.gold = 50000
    m.exp = 25000
    m.items.append(['long sword +3', True, False, True])
    m.items.append(['plate mail', True, False, False])
    m.items.append(['potion of curing', False, False, False])
    m.items.append(['scroll of pain', False, False, True])
    m.ac = 2
    m.mspells = []
    for n, s in game.spelldef.items():
        if s.categ == 'mage':
            m.mspells.append(n)
    m.mspell_cnt = [9, 9, 9, 9, 9, 9, 9]
    m.mspell_max = [9, 9, 9, 9, 9, 9, 9]
    m.pspells = []
    for n, s in game.spelldef.items():
        if s.categ == 'priest':
            m.pspells.append(n)
    m.pspell_cnt = [9, 9, 9, 9, 9, 9, 9]
    m.pspell_max = [9, 9, 9, 9, 9, 9, 9]
    game.characters.append(m)
    m = Member("Betty", Align.GOOD, Race.HUMAN, 28)
    m.job = Job.FIGHTER
    m.stat = [16, 9, 5, 15, 12, 11]
    m.exp = 25000
    m.maxhp = m.hp = 15
    m.hp = 8
    m.ac = 3
    m.items.append(['long sword', True, False, False])
    m.items.append(['plate mail', True, False, False])
    game.characters.append(m)
    m = Member("Cal", Align.GOOD, Race.HUMAN, 48)
    m.job = Job.SAMURAI
    m.stat = [16, 10, 5, 16, 13, 13]
    m.maxhp = m.hp = 16
    m.exp = 25000
    m.ac = 4
    m.items.append(['long sword', True, False, False])
    m.items.append(['plate mail', True, False, False])
    game.characters.append(m)
    m = Member("Debora", Align.NEUTRAL, Race.HOBBIT, 36)
    m.job = Job.THIEF
    m.stat = [12, 10, 5, 18, 13, 18]
    m.maxhp = m.hp = 11
    m.exp = 25000
    game.characters.append(m)
    m = Member("Emily", Align.GOOD, Race.ELF, 29)
    m.job = Job.PRIEST
    m.stat = [12, 15, 18, 15, 12, 9]
    m.maxhp = m.hp = 12
    m.exp = 60000
    m.pspells = ['jiai', 'iyashi']
    m.pspell_cnt = [9, 9, 9, 9, 9, 9, 9]
    m.pspell_max = [9, 9, 9, 9, 9, 9, 9]

    game.characters.append(m)
    m = Member("Fast", Align.GOOD, Race.ELF, 36)
    m.job = Job.MAGE
    m.stat = [8, 18, 10, 14, 16, 14]
    m.maxhp = m.hp = 7
    m.exp = 30000
    m.mspells = []
    for n, s in game.spelldef.items():
        if s.categ == 'mage':
            m.mspells.append(n)
    m.mspell_cnt = [9, 9, 9, 9, 9, 9, 9]
    m.mspell_max = [9, 9, 9, 9, 9, 9, 9]
    game.characters.append(m)
    """

    dispatch(game)


if __name__ == "__main__":
    main()
