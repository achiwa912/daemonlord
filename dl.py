import re
import textwrap
import time
import random
import os
import sys
import struct
import tty
from enum import Enum
import termios
import fcntl

config = {
    'floor_xmin': 76,  # 40,
    'floor_ymin': 32,  # 16,
    'max_depth': 16,
}


class Job(Enum):
    UNEMPLOYED, FIGHTER, MAGE, PRIEST, THIEF, BISHOP, SAMURAI, NINJA, LORD = range(
        9)


class Race(Enum):
    HUMAN, ELF, DWARF, GNOME, HOBBIT = range(5)


class State(Enum):
    OK, ASLEEP, PARALYZED, POISONED, STONED, DEAD, ASHED, LOST = range(8)


class Align(Enum):
    GOOD, NEUTRAL, EVIL = range(3)


race_status = {
    Race.HUMAN: (8, 8, 5, 8, 8, 9),
    Race.ELF: (7, 10, 10, 6, 9, 6),
    Race.DWARF: (10, 7, 10, 10, 5, 6),
    Race.GNOME: (7, 7, 10, 8, 19, 7),
    Race.HOBBIT: (5, 7, 7, 6, 10, 15),
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
        self.items = []
        self.strength, self.iq, self.piety, self.vitality, self.agility, \
            self.luck = race_status[race]
        self.maxhp = 0
        self.hp = self.maxhp


class Vscr:
    """
    Manage and control scroll window and virtual scroll windows
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.vscr0 = bytearray(b'M'*width*height)
        self.vscr1 = bytearray(b'N'*width*height)
        self.prev_vscr_view = memoryview(self.vscr0)
        self.cur_vscr_view = memoryview(self.vscr1)
        self.meswin = None

    def draw_map(self, party, floor_obj):
        """
        Copy map data to a virtual scroll window
        """
        floor_view = memoryview(floor_obj.floor_data)
        cv = self.cur_vscr_view
        w = self.width
        for cy in range(self.height):
            cv[cy*w:(cy+1)*w] = b'^'*w  # fill with rocks
            my = party.y - self.height//2 + cy  # convert cy to floor_y
            if 0 <= my < floor_obj.y_size:
                l_left = min(0, party.x-w//2) * -1
                l_right = min(w, floor_obj.x_size - party.x + w//2)
                map_left = my*floor_obj.x_size + party.x - w//2 + l_left
                map_right = map_left + l_right - l_left
                cv[cy*w+l_left:cy*w+l_right] = floor_view[map_left:map_right]
            if cy == self.height//2:
                cv[cy*w+w//2:cy*w+w//2+1] = b'@'

    def display(self):
        """
        Actually print scroll window on the terminal
        """
        cv = self.cur_vscr_view
        w = self.width
        for y in range(self.height):
            slc = slice(y*w, (y+1)*w)
            if cv[slc] != self.prev_vscr_view[slc]:
                print(f"\033[{y};0H", end='')
                print(cv[slc].tobytes().decode(), end='')

    def show_meswin(self):
        mw = self.meswin
        for y in range(mw.height):
            if y == 0 or y == mw.height-1:
                line = '-'*mw.width
            elif len(mw.mes_lines) <= y-1:
                line = ''.join(['| ', ' '*(mw.mes_width+2), '|'])
            else:
                line = ''.join(
                    ['| ', mw.mes_lines[y-1].ljust(mw.mes_width+2), '|'])
            line = line.encode()
            vscr_left = (mw.y+y)*self.width + mw.x
            self.cur_vscr_view[vscr_left:vscr_left+len(line)] = line

    def show_partywin(self, party):
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

    def disp_scrwin(self, party, floor_obj):
        """
        Display scroll window main
        """
        start = time.time()
        self.draw_map(party, floor_obj)
        self.show_partywin(party)
        self.show_meswin()
        self.display()
        self.cur_vscr_view, self.prev_vscr_view \
            = self.prev_vscr_view, self.cur_vscr_view
        delta = time.time() - start
        try:
            print(f"\033[{self.height-1};0H", end='')
            print(f"\n{party.x:03d}/{party.y:03d}, {delta:.5f}",
                  end='', flush=True)
        except:
            pass


class Meswin:
    """
    Message window.  Max 40x8 at the upper center of the scroll window.
    The message area is max 36x6 and a message starts with " * ".
    """

    def __init__(self, vscr):
        self.vscr = vscr
        self.width = min(40, vscr.width)
        self.height = min(8, vscr.height)
        self.x = max(0, (vscr.width-self.width)//2)  # center
        self.y = max(0, (vscr.height-self.height)//10)  # uppper
        self.mes_width = self.width - 4  # Message area width
        self.mes_height = self.height - 2  # Message area height
        self.cur_x = 0  # cursor position in message area
        self.cur_y = 0
        self.show = False
        self.mes_lines = []
        self.cls()

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
            ssls = textwrap.wrap(sl, width=self.mes_width)
            if len(ssls) == 0:
                self.mes_lines.append(header)
            else:
                for ssl in ssls:
                    self.mes_lines.append(''.join([header, ssl]))
                    header = '  '
        if len(self.mes_lines) > self.mes_height:
            self.mes_lines = self.mes_lines[len(
                self.mes_lines)-self.mes_height:]
        self.cur_y = len(self.mes_lines)-1
        self.show = True

    def input(self, msg):
        """
        Input a string in the message window.
        """
        self.print(msg)
        self.print('', start='>')
        self.vscr.show_meswin()
        self.vscr.display()
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
            self.print(msg+' >')
            self.vscr.show_meswin()
            self.vscr.display()
            print(f"\033[{self.y+self.cur_y+1};{self.x+len(msg)+8}H",
                  end='', flush=True)
            ch = getch()
            l = self.mes_lines.pop()
            self.print(''.join([l, ' ', ch])[2:])
            self.vscr.show_meswin()
            self.vscr.display()
            if not values:
                break
        return ch


class Party:
    def __init__(self, x, y, floor):
        self.x = x
        self.y = y
        self.floor = floor
        self.members = []


class Floor:
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


def getch():
    fd = sys.stdin.fileno()
    oattr = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, oattr)
    return ch


def main():
    floor_obj = generate_floor(1)
    party = Party(0, 0, 1)
    mem = Member("Alex", Align.GOOD, Race.HUMAN, 24)
    party.members.append(mem)
    mem = Member("Sean", Align.GOOD, Race.ELF, 136)
    party.members.append(mem)
    mem = Member("Son Goku", Align.NEUTRAL, Race.HOBBIT, 36)
    party.members.append(mem)
    w, h = terminal_size()
    # vscr = Vscr(w, h)
    vscr = Vscr(80, 25)  # +++++++++++++++
    meswin = Meswin(vscr)
    vscr.meswin = meswin
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
                vscr.show_meswin()
                vscr.display()
            else:
                pass  # draw = False
        else:
            draw = False
        if draw:
            vscr.disp_scrwin(party, floor_obj)


if __name__ == "__main__":
    main()
