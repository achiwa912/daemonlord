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
    OK, ASLEEP, PARALYZED, POISONED, STONED, DEAD, ASHED, LOST = range(8)


class Align(Enum):
    GOOD, NEUTRAL, EVIL = range(3)


class Place(Enum):
    MAZE, EDGE_OF_TOWN, TRAINING_GROUNDS, CASTLE, HAWTHORNE_TAVERN, TRADER_JAYS, LAKEHOUSE_INN, LEAVE_GAME = range(
        8)


race_status = {
    Race.HUMAN: (8, 8, 5, 8, 8, 9),
    Race.ELF: (7, 10, 10, 6, 9, 6),
    Race.DWARF: (10, 7, 10, 10, 5, 6),
    Race.GNOME: (7, 7, 10, 8, 19, 7),
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


class Member:
    def __init__(self, name, align, race, age):
        self.name = name
        self.align = align
        self.race = race
        self.age = age
        self.level = 1
        self.ac = 10
        self.job = Job.UNEMPLOYED
        self.state = State.OK
        self.gold = random.randrange(100, 200)
        self.exp = 0
        self.marks = 0
        self.rip = 0
        self.items = []
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
                if self.job.name[:1].lower() not in game.itemdef[item[0]][4].lower():
                    m = '#'  # can't equip
                if item[1]:
                    m = '*'  # equipped
                if item[2]:
                    m = '&'  # cursed
                if self.items[idx][3]:  # unidentified
                    l = f"{m}?{game.itemdef[item[0]][1]}"
                else:
                    l = f"{m}{item[0]}"
            except:
                l = ''
            if idx % 2:
                mw.print(f"{idx}) {ol.ljust(18)} {idx+1}) {l.ljust(18)}",
                         start=' ')
            ol = l

    def inspect_character(self, game):
        mw = game.vscr.meswins[-1]
        while True:
            self.disp_character(game)
            mw.print(f"", start=' ')
            c1 = mw.input_char("i)tems s)pells l)eave",
                               values=['i', 's', 'l'])
            if c1 == 'l':
                mw.cls()
                break
            elif c1 == 'i':
                self.item_menu(game)
            elif c1 == 's':
                self.spell_menu(game)

    def item_menu(self, game):
        vscr = game.vscr
        iw = Meswin(vscr, 14, 2, 44, 8, frame=True)
        vscr.meswins.append(iw)
        while True:
            iw.print("which item?  # or l)leave")
            vscr.disp_scrwin(game.party)
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
                dispname = ''.join(['?', game.itemdef[dispname][1]])
            iw.print(f"{inum+1}) {dispname}", start=' ')
            c = iw.input_char("u)se e)quip t)rade d)rop l)eave",
                              values=['u', 'e', 't', 'd', 'l'])
            if c == 'l':
                continue
            elif c == 'e':
                if self.job.name[:1] not in game.itemdef[self.items[inum][0]][4]:
                    iw.print("Can't equip the item.")
                    continue
                for item in self.items:
                    if game.itemdef[self.items[inum][0]][2] \
                       == game.itemdef[item[0]][2]:
                        if item[2]:  # already cursed
                            iw.print("Already equipped a cursed item.")
                            break
                        elif item[1]:  # equipped
                            item[1] = False
                if game.itemdef[self.items[inum][0]][11]:
                    self.items[inum][2] = True  # cursed
                    iw.print("Cursed!")
                    vscr.disp_scrwin(game.party)
                    getch()
                self.items[inum][1] = True  # equipped
                self.calc_ac(game)
                vscr.meswins.pop()
                vscr.disp_scrwin(game.party)
                vscr.disp_scrwin(game.party)
                return

    def calc_ac(self, game):
        self.ac = 10
        for item in self.items:
            if item[1] or item[2]:
                self.ac += game.itemdef[item[0]][5]

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
        Calculate bonus points
        """
        bonus = random.randrange(5, 9)
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
        for jobnum in range(5):
            if self.job_applicable(sp, jobnum):
                job = True
                line = ''.join([line, Job(jobnum).name[:].lower(), ' '])
        mw.print(line)
        vscr.disp_scrwin(game.party)
        return job

    def distribute_bonus(self, game):
        """
        Bonus assignment and deciding class main routine
        """
        bonus = self.calc_bonus()
        y = 0
        statplus = [0, 0, 0, 0, 0, 0]
        while True:
            job = bonus_disp(game, self, bonus, y, statplus)
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
        elif ch.job == Job.MAGE:
            self.maxhp = self.hp = random.randint(2, 7)
            self.mspells = ['onibi', 'shunmin']
            self.mspell_max = [2, 0, 0, 0, 0, 0, 0]
            self.mspell_cnt = [2, 0, 0, 0, 0, 0, 0]
        elif ch.job == Job.PRIEST:
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
        game.vscr.disp_scrwin(game.party)


class Game:
    def __init__(self):
        self.characters = []  # registerd characters

    def load_spelldef(self):
        """
        load spell definition file and return spell_def dictionary
        """
        with open('spells.csv') as csvfile:
            rdr = csv.reader(csvfile)
            spell_def = {}
            for i, row in enumerate(rdr):
                if i == 0:
                    continue
                line = (row[1], int(row[2]), json.loads(row[5].lower()),
                        json.loads(row[6].lower()), row[7], row[8], row[9], row[10])
                spell_def[row[3]] = line
            self.spelldef = spell_def

    def load_itemdef(self):
        """
        load item definition file and return item_def dictionary
        """
        with open('items.csv') as csvfile:
            rdr = csv.reader(csvfile)
            item_def = {}
            for i, row in enumerate(rdr):
                if i == 0 or not row:
                    continue
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
                # (0lvl, 1unident, 2type, 3range, 4jobs, 5ac, 6st, 7at,
                #  8dice, 9shop, 10price, 11curse, 12hp, 13brk, 14regist)
                line = (row[1], unident, row[6], row[7], row[8], ac,
                        st, at, row[12], shop, price,
                        curse, hp, brk, row[19])
                item_def[name] = line
            self.itemdef = item_def
            self.shopitems = {}
            for name in self.itemdef:
                self.shopitems[name] = self.itemdef[name][9]


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
        Actually print scroll window on the terminal
        """
        cv = self.cur_vscr_view
        w = self.width
        for y in range(self.height):
            slc = slice(y*w, (y+1)*w)
            if force == True or cv[slc] != self.prev_vscr_view[slc]:
                print(f"\033[{y+1};0H", end='')
                print(cv[slc].tobytes().decode(), end='')
        self.cur_vscr_view, self.prev_vscr_view \
            = self.prev_vscr_view, self.cur_vscr_view

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
                    line = f" {y} {m.name[:10].ljust(10)} {alcls} {m.ac:3d} {m.hp:4d} {m.state.name[:13].ljust(13)}"
                else:
                    line = f" {y}" + ' '*(width-2)
            line = line.encode()
            vscr_left = (self.height-7+y)*self.width
            self.cur_vscr_view[vscr_left:vscr_left+len(line)] = line

    def draw_header(self, party):
        """
        Display the header info
        """
        line = f" daemon lord - dl - [{party.place.name.lower()}] floor:{party.floor:2d} ({party.x}/{party.y}) "
        self.cur_vscr_view[:len(line)] = line.encode()

    def disp_scrwin(self, party, floor_obj=None):
        """
        Display scroll window main
        """
        start = time.time()
        if party.place == Place.MAZE:
            for y in range(party.y-1, party.y+2):
                for x in range(party.x-1, party.x+2):
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
            print(f"\n{party.x:03d}/{party.y:03d}, {delta:.5f}",
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
            ssls = textwrap.wrap(sl, width=meswidth)
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
        self.vscr.draw_meswins()
        self.vscr.display()
        print(f"\033[{self.y+self.cur_y+1};{self.x+3}H", end='', flush=True)
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
            self.vscr.draw_meswins()
            self.vscr.display()
            print(f"\033[{self.y+self.cur_y+1};{self.x+len(msg)+6}H",
                  end='', flush=True)
            ch = getch()
            l = self.mes_lines.pop()
            self.print(''.join([l, ' ', ch])[2:], start=' ')
            self.vscr.draw_meswins()
            self.vscr.display()
            if not values:
                break
        return ch


class Party:
    # Represents a party
    def __init__(self, x, y, floor):
        self.x = x
        self.y = y
        self.floor = floor
        self.members = []

    def can_open(self, game):
        return True  # ++++++++++++++++++++++++++++++

    def choose_character(self, game):
        """
        Choose and return a party member
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
                    game.vscr.disp_scrwin(self)
                    game.vscr.disp_scrwin(self)
            except:
                pass


class Floor:
    # Represents a floor in the dungeon
    def __init__(self, x_size, y_size, floor, floor_data):
        self.x_size = x_size
        self.y_size = y_size
        self.floor = floor
        self.floor_data = floor_data
        self.floor_view = memoryview(floor_data)

    def __repr__(self):
        s = self.floor_data.decode()
        return f"Floor(size: {self.x_size}x{self.y_size}, floor: {self.floor} - {s})"

    def get_tile(self, x, y):
        if x >= self.x_size or x < 0:
            return b'^'
        if y >= self.y_size or y < 0:
            return b'^'
        pos = y * self.x_size + x
        return self.floor_orig[pos:pos+1]

    def put_tile(self, x, y, bc, orig=True):
        if 0 <= x < self.x_size and 0 <= y < self.y_size:
            pos = y * self.x_size + x
            if orig:
                self.floor_orig[pos:pos+1] = bc
            else:
                self.floor_data[pos:pos+1] = bc

    def can_move(self, x, y):
        bc = self.get_tile(x, y)
        if bc in b"*+#^":
            return False
        return True

    def open_door(self, game, mw):
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
            # game.vscr.disp_scrwin(game.party)

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
        if random.randrange(1) == 0:  # 1/2
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


def terminal_size():
    """
    Get terminal size
    Will return width and height
    """
    h, w, hp, wp = struct.unpack('HHHH',
                                 fcntl.ioctl(0, termios.TIOCGWINSZ,
                                             struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h


def generate_floor(floor):
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
    floor_obj.floor_orig = floor_obj.floor_data
    floor_obj.floor_data = bytearray(b'^' * floor_x_size * floor_y_size)
    return floor_obj


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
                vscr.disp_scrwin(game.party)
            else:
                break
    vscr.disp_scrwin(game.party)

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
    vscr.disp_scrwin(game.party)

    c = mw.input_char(
        "Choose alignment - g)ood n)eutral e)vil", values=['g', 'n', 'e'])
    if c == 'g':
        align = Align.GOOD
    elif c == 'n':
        align = Align.NEUTRAL
    else:
        align = Align.EVIL
    mw.print(f"Alignment: {align.name.lower()}")
    vscr.disp_scrwin(game.party)

    while True:
        age = mw.input("How old is he/she? (13-199)")
        try:
            age = int(age)
            if 12 < age < 200:
                break
        except:
            pass
        vscr.disp_scrwin(game.party)
    mw.print(f"{age} years old.")
    vscr.disp_scrwin(game.party)

    ch = Member(name, align, race, age)
    ch.distribute_bonus(game)


def inspect_characters(game):
    """
    Inspect characters (a training grounds menu item)
    """
    vscr = game.vscr
    mw = vscr.meswins[-1]
    mw.mes_lines = []
    vscr.disp_scrwin(game.party)
    cnum = 0
    chlist = game.party.members
    if game.party.place == Place.TRAINING_GROUNDS:
        chlist = game.characters
    while True:
        mw.mes_lines = []
        mw.print("Inspect characters -  j)down k)up i)nspect l)eave]")
        for i, mem in enumerate(chlist):
            if i == cnum:
                cur = ' >'
            else:
                cur = '  '
            mw.print(''.join([cur, str(i+1), ' ', str(mem)]), start=' ')
        vscr.disp_scrwin(game.party)
        c = getch()
        if c == 'l':
            break
        elif c == 'j' and cnum < len(chlist)-1:
            cnum += 1
        elif c == 'k' and cnum > 0:
            cnum -= 1
        elif c == 'i' and len(chlist) > 0:
            chlist[cnum].inspect_character(game)


def training(game):
    """
    Training grounds main (an edge of town menu item)
    """
    vscr = game.vscr
    game.party.place = Place.TRAINING_GROUNDS
    mw = vscr.meswins[-1]
    vscr.cls()
    vscr.disp_scrwin(game.party)
    while True:
        mw.print(
            "*** training grounds ***\nc)reate a character\ni)nspect a character\nl)eave")
        vscr.disp_scrwin(game.party)
        c = mw.input_char("Command?")
        if c == 'l':
            break
        elif c == 'c':
            create_character(game)
        elif c == 'i':
            inspect_characters(game)


def tavern_add(game):
    """
    add members to the party
    """
    vscr = game.vscr
    mw = vscr.meswins[-1]
    if len(game.party.members) >= 6:
        mw.print("Party full.")
        vscr.disp_scrwin(game.party)
        return

    vscr.disp_scrwin(game.party)
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
        vscr.disp_scrwin(game.party)
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
    vscr.disp_scrwin(game.party)


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
        vscr.disp_scrwin(game.party)
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
            if (mem := game.party.choose_character(game)):
                mem.inspect_character(game)
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
                 and game.itemdef[item][2] == pages[page]]
        ilines = []
        for i, item in enumerate(items):
            cur = ' '
            if i == idx:
                cur = '>'
                cur_item = i
            afford = canequip = ' '
            if mem.job.name[:1].lower() not in game.itemdef[item][4].lower():
                canequip = '#'
            if mem.gold >= game.itemdef[item][10]:
                afford = '$'
            iline = f"| {cur}{i+1:2} {item.ljust(21)[:21]} {game.itemdef[item][10]:10d}{canequip}{afford}|"
            ilines.append(iline)
        iw.mes_lines = []
        iw.mes_lines.append(
            f"| {mem.name} has {mem.gold} gold".ljust(40)+'|')
        iw.mes_lines.append("|  jk)cursor x)choose hl)page ;)leave   |")
        for il in ilines[top:top+iw.height-2]:
            iw.mes_lines.append(il.ljust(iw.width-1))
        for _ in range(iw.width - len(iw.mes_lines)):
            iw.mes_lines.append(''.join(['|', ' '*(iw.width-2), '|']))
        vscr.disp_scrwin(game.party)
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
                vscr.disp_scrwin(game.party)
                getch()
            elif mem.gold < game.itemdef[items[idx]][10]:
                iw.mes_lines[0] = "| Sorry, you can't afford it.".ljust(
                    iw.width-1)+'|'
                #iw.mes_lines[1] = f"{mem.gold} < {game.itemdef[items[idx]][10]}"
                vscr.disp_scrwin(game.party)
                getch()
            else:
                iw.mes_lines[0] = "| Anything else, noble sir?".ljust(
                    iw.width-1)+'|'
                mem.gold -= game.itemdef[items[idx]][10]
                bought = [items[idx], False, False, False]
                mem.items.append(bought)
                game.shopitems[items[idx]] -= 1
                vscr.disp_scrwin(game.party)
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
                dispname = ''.join(['?', game.itemdef[item[0]][1]])
        elif op == 'i':  # identify
            if (not item[3]) or item[2]:
                continue
            dispname = ''.join(['?', game.itemdef[item[0]][1]])
        else:  # sell
            if item[2] or item[3]:
                continue
            if item[1]:  # equipped
                mark = '*'
        price = game.itemdef[item[0]][10]//2
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

    game.vscr.disp_scrwin(game.party)
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
        vscr.disp_scrwin(game.party)
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


def castle(game):
    """
    castle main
    dispatch to tavern, shop, inn or temple
    """
    vscr = game.vscr
    mw = vscr.meswins[-1]
    vscr.cls()
    vscr.disp_scrwin(game.party)
    ch = ''
    while True:
        mw.cls()
        game.party.place = Place.CASTLE
        mw.print("*** Castle ***")
        mw.print("h)awthorne tavern\nt)rader jay's\nl)akehouse inn", start=' ')
        mw.print("k)makura shrine\ne)dge of town", start=' ')
        vscr.disp_scrwin(game.party)
        ch = mw.input_char("Command?", values=['h', 'e', 't'])
        if ch == 'h':
            tavern(game)
        elif ch == 'e':
            game.party.place = Place.EDGE_OF_TOWN
            break
        elif ch == 't':
            trader(game)


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
        mw.print("m)aze\nt)raining grounds\nl)eave game\nc)astle", start=' ')
        vscr.disp_scrwin(game.party)
        ch = mw.input_char("Command? ", values=['t', 'm', 'c', 'l'])
        if ch == 't':
            training(game)
        elif ch == 'c':
            game.party.place = Place.CASTLE
            break
        elif ch == 'm':
            game.party.place = Place.MAZE
            break
        elif ch == 'l':
            mw.print("type Q to quit for now...")
            vscr.disp_scrwin(game.party)
            getch()


def maze(game):
    party = game.party
    party.place = Place.MAZE
    vscr = game.vscr

    floor_obj = generate_floor(1)
    party.x = floor_obj.up_x
    party.y = floor_obj.up_y

    meswin = vscr.meswins[0]
    vscr.meswins = [meswin]
    vscr.disp_scrwin(party, floor_obj)

    while True:
        c = getch()
        draw = True
        if c:
            if c == 'Q':
                sys.exit()
            if c == 'h' and party.x > 0:
                if floor_obj.can_move(party.x-1, party.y):
                    party.x -= 1
                    meswin.print("west")
            elif c == 'k' and party.y > 0:
                if floor_obj.can_move(party.x, party.y-1):
                    party.y -= 1
                    meswin.print("north")
            elif c == 'j' and party.y < floor_obj.y_size-1:
                if floor_obj.can_move(party.x, party.y+1):
                    party.y += 1
                    meswin.print("south")
            elif c == 'l' and party.x < floor_obj.x_size-1:
                if floor_obj.can_move(party.x+1, party.y):
                    party.x += 1
                    meswin.print("east")
            elif c == 'o':
                vscr.display()
                floor_obj.open_door(game, meswin)
            elif c == '.':
                ch = meswin.input_char("Do you? (y/n)", values=['n', 'y'])
                meswin.print("Input char: "+ch)
                vscr.draw_meswins()
                vscr.display()
            else:
                pass  # draw = False
        else:
            draw = False
        if draw:
            vscr.disp_scrwin(party, floor_obj)


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
    game = Game()
    party = Party(0, 0, 1)
    game.party = party
    game.load_spelldef()
    game.load_itemdef()
    party.place = Place.CASTLE
    # floor_obj = generate_floor(1)
    w, h = terminal_size()
    # vscr = Vscr(w, h)
    vscr = Vscr(80, 25)  # +++++++++++++++
    game.vscr = vscr
    vscr.meswins.append(Meswin(vscr, 42, 18, 40, 7))  # meswin for scrollwin
    # meswin for castle/edge of town
    vscr.meswins.append(Meswin(vscr, 10, 1, 64, 17, frame=True))

    m = Member("Alex", Align.GOOD, Race.DWARF, 32)
    m.job = Job.FIGHTER
    m.stat = (18, 10, 5, 11, 13, 11)
    m.maxhp = m.hp = 13
    m.gold = 50000
    m.items.append(['shield -3', False, False, True])
    game.characters.append(m)
    m = Member("Betty", Align.GOOD, Race.HUMAN, 28)
    m.job = Job.FIGHTER
    m.stat = (16, 9, 5, 15, 12, 11)
    m.maxhp = m.hp = 15
    game.characters.append(m)
    m = Member("Cal", Align.GOOD, Race.HUMAN, 48)
    m.job = Job.SAMURAI
    m.stat = (16, 10, 5, 16, 13, 13)
    m.maxhp = m.hp = 16
    game.characters.append(m)
    m = Member("Debora", Align.NEUTRAL, Race.HOBBIT, 36)
    m.job = Job.THIEF
    m.stat = (12, 10, 5, 18, 13, 18)
    m.maxhp = m.hp = 11
    game.characters.append(m)
    m = Member("Emily", Align.GOOD, Race.ELF, 29)
    m.job = Job.PRIEST
    m.stat = (12, 15, 18, 15, 12, 9)
    m.maxhp = m.hp = 12
    game.characters.append(m)
    m = Member("Fast", Align.GOOD, Race.ELF, 36)
    m.job = Job.MAGE
    m.stat = (8, 18, 10, 14, 16, 14)
    m.maxhp = m.hp = 7
    game.characters.append(m)
    dispatch(game)


if __name__ == "__main__":
    main()
