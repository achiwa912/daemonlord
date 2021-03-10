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

    def __repr__(self):
        return f"<{self.name}, {self.align.name[:1]}-{self.race.name[:3]}-{self.job.name[:3]} {self.stat[0]}/{self.stat[1]}/{self.stat[2]}/{self.stat[3]}/{self.stat[4]}>"

    def __str__(self):
        return f"{self.name[:16].ljust(16)} Lv{self.level:3d} {self.race.name[:3].lower()}-{self.align.name[:1].lower()}-{self.job.name[:3].lower()}"


class Game:
    def __init__(self):
        self.characters = []  # registerd characters


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
            for y in range(mw.height):
                if len(mw.mes_lines) <= y:
                    line = ' '*(mw.width-2)
                else:
                    line = mw.mes_lines[y].ljust(mw.width-2)
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

    def __init__(self, vscr, x, y, width, height):
        self.vscr = vscr
        self.width = min(width, vscr.width)
        self.height = min(height, vscr.height)
        self.x = x
        self.y = y
        self.cur_x = 0  # cursor position in message area
        self.cur_y = 0
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
        sublines = re.split('\n', msg)
        for idx, sl in enumerate(sublines):  # subline
            header = '  '
            if idx == 0:
                header = start + ' '
            ssls = textwrap.wrap(sl, width=self.width-2)
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
        while rs:
            idx_near = 0
            len_rs = len(rs)
            for i in range(len_rs):  # look for the nearest room
                if r_src.distsq_rooms(rs[i]) < r_src.distsq_rooms(rs[idx_near]):
                    idx_near = i
            r_near = rs.pop(idx_near)
            self.connect_rooms(r_src, r_near)
            r_src = r_near

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


def job_applicable(sp, ch, jobnum):
    """
    Utility function to check if the character is applicable for the job
    """
    for i in range(6):
        if sp[i]+ch.stat[i] < job_requirements[Job(jobnum)][i]:
            return False
    if job_requirements[Job(jobnum)][6][ch.align.value]:
        return True
    else:
        return False


def bonus_disp(game, ch, bonus, y, sp):
    """
    Display bonus assignment screen
    """
    vscr = game.vscr
    mw = vscr.meswins[-1]
    mw.cls()
    mw.print("Distribute bonus points")
    mw.print("  h)minus j)down k)up l)plus .)change bonus x)done\n", start=' ')
    mw.print(f"strength  {sp[0]+ch.stat[0]:2d}", start=' ')
    mw.print(f"iq        {sp[1]+ch.stat[1]:2d}", start=' ')
    mw.print(f"piety     {sp[2]+ch.stat[2]:2d}", start=' ')
    mw.print(f"vitality  {sp[3]+ch.stat[3]:2d}", start=' ')
    mw.print(f"agility   {sp[4]+ch.stat[4]:2d}", start=' ')
    mw.print(f"luck      {sp[5]+ch.stat[5]:2d}", start=' ')
    mw.print(f"\nbonus     {bonus:2d}", start=' ')
    mw.print
    mw.mes_lines[y+3] = mw.mes_lines[y+3][:11] + '>' + mw.mes_lines[y+3][12:]
    line = ''
    job = False
    for jobnum in range(5):
        if job_applicable(sp, ch, jobnum):
            job = True
            line = ''.join([line, Job(jobnum).name[:].lower(), ' '])
    mw.print(line)
    vscr.disp_scrwin(game.party)
    return job


def calc_bonus():
    """
    Calculate bonus points
    """
    bonus = random.randrange(5, 9)
    for _ in range(3):
        if random.randrange(6) == 0:
            bonus += 10
    return bonus


def distribute_bonus(game, ch):
    """
    Bonus assignment and deciding class main routine
    """
    bonus = calc_bonus()
    y = 0
    statplus = [0, 0, 0, 0, 0, 0]
    while True:
        job = bonus_disp(game, ch, bonus, y, statplus)
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
        elif c == 'l' and statplus[y]+ch.stat[y] < 18 and bonus > 0:
            statplus[y] += 1
            bonus -= 1
        elif c == '.':
            statplus = [0, 0, 0, 0, 0, 0]
            bonus = calc_bonus()
    jobs = []
    line = "Choose class ("
    for jobnum in range(8):
        if job_applicable(statplus, ch, jobnum):
            line = ''.join([line, Job(jobnum).name[:1].lower(), '/'])
            jobs.append(Job(jobnum).name[:1].lower())
    line = ''.join([line[:-1], ')'])
    mw = game.vscr.meswins[-1]
    c = mw.input_char(line, values=jobs)
    for jobnum in range(8):
        if c == Job(jobnum).name[:1].lower():
            break
    ch.job = Job(jobnum)
    if ch.job == Job.FIGHTER:
        ch.maxhp = ch.hp = random.randint(8, 15)
    elif ch.job == Job.MAGE:
        ch.maxhp = ch.hp = random.randint(2, 7)
        ch.mspells = ['onibi', 'shunmin']
        ch.mspell_cnt = [2, 0, 0, 0, 0, 0, 0]
    elif ch.job == Job.PRIEST:
        ch.maxhp = ch.hp = random.randint(6, 13)
        ch.pspells = ['jiai', 'ikari']
        ch.pspell_cnt = [2, 0, 0, 0, 0, 0, 0]
    elif ch.job == Job.THIEF or Job.BISHOP:
        ch.maxhp = ch.hp = random.randint(4, 9)
    elif ch.job == Job.SAMURAI:
        ch.maxhp = ch.hp = random.randint(12, 19)
    elif ch.job == Job.LORD:
        ch.maxhp = ch.hp = random.randint(12, 19)
    else:  # ninja
        ch.maxhp = ch.jp = random.randint(8, 17)

    for i in range(6):
        ch.stat[i] += statplus[i]
    game.characters.append(ch)
    mw.print("Character created")
    game.vscr.disp_scrwin(game.party)


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
    distribute_bonus(game, ch)


def disp_character(game, ch):
    """
    Display a character information in the message window
    """
    vscr = game.vscr
    mw = vscr.meswins[-1]
    mw.mes_lines = []
    mw.print(
        f"{ch.name.ljust(16)} L{ch.level:3d} {ch.align.name[:1].lower()}-{ch.job.name[:3].lower()} {ch.race.name.lower()}", start=' ')
    mw.print(f"", start=' ')
    mw.print(
        f"strength {ch.stat[0]:2d}  gold {ch.gold:16d} lvl {ch.level:5d}", start=' ')
    mw.print(
        f"    i.q. {ch.stat[1]:2d}  e.p. {ch.exp:16d} age {ch.age:5d}", start=' ')
    mw.print(
        f"   piety {ch.stat[2]:2d}  h.p.  {ch.hp:7d}/{ch.maxhp:7d} a.c.{ch.ac:5d}", start=' ')
    mw.print(
        f"vitality {ch.stat[3]:2d}  rip  {ch.rip:7d}     marks {ch.marks:8d}", start=' ')
    mw.print(f" agility {ch.stat[4]:2d}", start=' ')
    mw.print(f"    luck {ch.stat[5]:2d}  status {ch.state.name}", start=' ')
    mw.print(f"", start=' ')
    mw.print(f"mage  {ch.mspell_cnt[0]}/{ch.mspell_cnt[1]}/{ch.mspell_cnt[2]}/{ch.mspell_cnt[3]}/{ch.mspell_cnt[4]}/{ch.mspell_cnt[5]}/{ch.mspell_cnt[6]}   priest  {ch.pspell_cnt[0]}/{ch.pspell_cnt[1]}/{ch.pspell_cnt[2]}/{ch.pspell_cnt[3]}/{ch.pspell_cnt[4]}/{ch.pspell_cnt[5]}/{ch.pspell_cnt[6]}/", start=' ')
    mw.print(f"", start=' ')
    mw.print(
        f"1) {'*long sword'.ljust(16)}  2) {'*plate mail'.ljust(16)}", start=' ')
    vscr.disp_scrwin(game.party)
    getch(wait=True)


def inspect_characters(game):
    """
    Inspect characters (a training grounds menu item)
    """
    vscr = game.vscr
    mw = vscr.meswins[-1]
    mw.mes_lines = []
    vscr.disp_scrwin(game.party)
    cnum = 0
    while True:
        mw.mes_lines = []
        mw.print("Inspect characters -  j)down k)up i)nspect l)eave]")
        for i, mem in enumerate(game.characters):
            if i == cnum:
                cur = ' >'
            else:
                cur = '  '
            mw.print(''.join([cur, str(i+1), ' ', str(mem)]), start=' ')
        vscr.disp_scrwin(game.party)
        c = getch()
        if c == 'l':
            break
        elif c == 'j' and cnum < len(game.characters)-1:
            cnum += 1
        elif c == 'k' and cnum > 0:
            cnum -= 1
        elif c == 'i' and len(game.characters) > 0:
            disp_character(game, game.characters[cnum])


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


def load_spelldef():
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
        return spell_def


def load_itemdef():
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
            line = (row[1], unident, row[6], row[7], row[8], ac,
                    st, at, row[12], shop, price,
                    curse, hp, brk, row[19])
            item_def[name] = line
        return item_def


def tavern_add(game):
    vscr = game.vscr
    mw = vscr.meswins[-1]
    if len(game.party.members) >= 6:
        mw.print("Party full.")
        vscr.disp_scrwin(game.party)
        return

    vscr.disp_scrwin(game.party)
    chwin = Meswin(vscr, 10, 2, 40, 16)
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


def trader_buy(game, mem):
    vscr = game.vscr
    iw = Meswin(vscr, 10, 1, 41, 12)
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
                bought = [game.itemdef[items[idx]], False, False]
                mem.items.append(bought)
                vscr.disp_scrwin(game.party)
                getch()
    vscr.meswins.pop()


def trader(game):
    game.party.place = Place.TRADER_JAYS
    vscr = game.vscr
    mw = vscr.meswins[-1]
    while True:
        mw.print("*** Trader Jay's ***")
        vscr.disp_scrwin(game.party)
        while True:
            ch = mw.input_char(f"Who will enter? - # or l)eave")
            if ch == 'l':
                break
            try:
                if 0 <= (chid := int(ch)-1) < len(game.party.members):
                    break
            except:
                pass
        if ch == 'l':
            break
        mem = game.party.members[chid]
        while True:
            mw.print(f"Welcome, {mem.name}.")
            mw.print(f"  You have {mem.gold} gold.")
            ch = mw.input_char(f"b)uy s)ell u)ncurse i)dentify p)ool gold l)eave",
                               values=['b', 'p', 'l'])
            if ch == 'l':
                break
            elif ch == 'b':
                trader_buy(game, mem)
            elif ch == 'p':
                gold = 0
                for c in game.party.members:
                    gold += c.gold
                    c.gold = 0
                mem.gold = gold


def castle(game):
    game.party.place = Place.CASTLE
    vscr = game.vscr
    mw = vscr.meswins[-1]
    vscr.cls()
    vscr.disp_scrwin(game.party)
    ch = ''
    while True:
        mw.cls()
        mw.print("*** Castle ***")
        mw.print("h)awthorne tavern\ne)dge of town", start=' ')
        mw.print("t)rader jay's", start=' ')
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
                party.x -= 1
                meswin.print("west")
            elif c == 'k' and party.y > 0:
                party.y -= 1
                meswin.print("north")
            elif c == 'j' and party.y < floor_obj.y_size-1:
                party.y += 1
                meswin.print("south")
            elif c == 'l' and party.x < floor_obj.x_size-1:
                party.x += 1
                meswin.print("east")
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
    while game.party.place != Place.LEAVE_GAME:
        pl = game.party.place
        if pl == Place.EDGE_OF_TOWN:
            edge_town(game)
        elif pl == Place.TRAINING_GROUNDS:
            training(game)
        elif pl == Place.CASTLE:
            castle(game)
        elif pl == Place.MAZE:
            maze(game)


def main():
    game = Game()
    party = Party(0, 0, 1)
    game.party = party
    game.spelldef = load_spelldef()
    game.itemdef = load_itemdef()
    game.shopitems = {}
    for name in game.itemdef:
        game.shopitems[name] = game.itemdef[name][9]
    party.place = Place.CASTLE
    # floor_obj = generate_floor(1)
    w, h = terminal_size()
    # vscr = Vscr(w, h)
    vscr = Vscr(80, 25)  # +++++++++++++++
    game.vscr = vscr
    vscr.meswins.append(Meswin(vscr, 42, 18, 40, 7))  # meswin for scrollwin
    # meswin for castle/edge of town
    vscr.meswins.append(Meswin(vscr, 10, 1, 60, 17))
    dispatch(game)


if __name__ == "__main__":
    main()
