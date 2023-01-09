import collections
import itertools
from operator import itemgetter, attrgetter
from dataclasses import dataclass
import csv
import json
from enum import Enum
import select
import struct
import sys
import os
import random
import time
import textwrap
import re
import pickle
import uuid
from threading import Thread
import yaml
import hashlib
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, LargeBinary
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
if os.name == 'nt':
    import msvcrt  # Windows
    os_windows = True
    os.system("")
else:
    import termios  # Mac & Linux
    import fcntl
    import tty
    os_windows = False

config = {
    'debug': False,
    'client': True,
    'newdb': True,
}

if config['client']:
    import socketio
    sio = socketio.Client()


class Job(Enum):
    FIGHTER, MAGE, PRIEST, THIEF, BISHOP, SAMURAI, LORD, NINJA, UNEMPLOYED = range(
        9)


class Race(Enum):
    HUMAN, ELF, DWARF, GNOME, HOBBIT = range(5)


class State(Enum):
    OK, ASLEEP, PARALYZED, STONED, DEAD, ASHED, LOST, RAN = range(8)


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


Monsterdef = collections.namedtuple(
    'Monsterdef', ['names', 'unident', 'unidents', 'type',
                   'level', 'hp', 'ac', 'attack', 'count', 'act',
                   'poison', 'paraly',
                   'stone', 'critical', 'drain', 'breathsp', 'heal',
                   'regdeathp', 'regfire', 'regcold', 'regpoison',
                   'regspellp', 'weakmaka', 'weaksleep', 'friendly',
                   'exp', 'number', 'floors', 'fellow', 'fellowp',
                   'agi', 'treasure'])

Spelldef = collections.namedtuple(
    'Spelldef', ['categ', 'level', 'battle', 'camp', 'type',
                 'target', 'value', 'attr', 'desc'])

Itemdef = collections.namedtuple(
    'Itemdef', ['level', 'unident', 'type', 'range', 'jobs', 'ac',
                'st', 'at', 'dice', 'shop', 'price', 'curse',
                'hp', 'use', 'brk', 'regist', 'twice', 'align',
                'sp', 'target'])


@dataclass
class Memitem:
    """
    Member.items will have list of Memitem()
    """
    name: str
    equipped: bool = False
    cursed: bool = False
    unidentified: bool = False
    onsale: bool = False


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
        self.messages = []  # list of tuple(user, message)
        self.battle_messages = []  # list of (start, message)
        self.refresh = False  # someone moved
        # party owner to show in party window (for group camp)
        self.show_puser = config['server']['auth']['user']

    def draw_map(self, party, floor_obj):
        """
        Copy map data to a virtual scroll window
        """
        floor_view = memoryview(floor_obj.floor_data)
        cv = self.cur_vscr_view
        w = self.width
        plocs = [(k[:1].upper(), v[0], v[1])
                 for k, v in game.dungeon.party_locs.items()
                 if v[2] == party.floor and k != config['server']['auth']['user']]
        for cy in range(self.height):
            cv[cy*w:(cy+1)*w] = b'^'*w  # fill with rocks
            my = party.y - (self.height-7)//2 + cy  # convert cy to floor_y
            if 0 <= my < floor_obj.y_size:
                l_left = min(0, party.x-w//2) * -1
                l_right = min(w, floor_obj.x_size - party.x + w//2)
                map_left = my*floor_obj.x_size + party.x - w//2 + l_left
                map_right = map_left + l_right - l_left
                cv[cy*w+l_left:cy*w+l_right] = floor_view[map_left:map_right]
                for ch, x, y in plocs:
                    if my != y:
                        continue
                    if party.x-w//2+l_left < x < party.x-w//2+l_right:
                        cv[cy*w+l_left+x] = ch.encode('utf-8')[0]
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
        if game.dungeon.expedition and game.dungeon.parties \
           and game.party.place == Place.CAMP and \
           game.vscr.show_puser != config['server']['auth']['user']:
            p = game.dungeon.parties[game.vscr.show_puser]
        else:
            p = party
        if p.gps:
            line = f" daemon lord - dl - [{party.place.name.lower()}] floor:{party.floor:2d} ({party.x:3d}/{party.y:3d}) "
        else:
            line = f" daemon lord - dl - [{party.place.name.lower()}] floor:?? (???/???) "
        if game.dungeon.expedition:
            line = line.replace("- dl -", "<server>")
        if game.dungeon.expedition and game.dungeon.parties \
           and game.party.place == Place.CAMP:
            line = line.replace("camp", "group camp")
            if game.vscr.show_puser != config['server']['auth']['user']:
                line = line.replace("daemon lord ", "[VIEW MODE] ")
        if p.identify:
            line = line + "<identify> "
        if p.light_cnt:
            line = line + "<light> "
        self.cur_vscr_view[:len(line)] = line.encode()

    def disp_scrwin(self, floor_obj=None):
        """
        Display scroll window main
        """
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
        if game.dungeon.expedition and party.place == Place.CAMP and \
           game.vscr.show_puser != config['server']['auth']['user']:
            p = game.dungeon.parties[game.vscr.show_puser]
            self.draw_partywin(p)
        else:
            self.draw_partywin(party)
        self.draw_header(party)
        self.draw_meswins()
        self.display()
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

    def print(self, msg, start='*', bcast=False):
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
        if bcast and game.dungeon.expedition and \
           game.party.place == Place.BATTLE and game.battle.joined_battle():
            data = {'msg': msg, 'start': start}
            sio.emit('battle_msg', data)

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
        self.print(msg+' >', start=' ')
        self.vscr.disp_scrwin()
        l = self.mes_lines.pop()
        while ch not in values:
            print(f"\033[{self.y+self.cur_y+1};{self.x+len(msg)+8}H",
                  end='', flush=True)
            ch = getch()
            self.print(''.join([l, ' ', ch])[2:], start=' ')
            self.vscr.disp_scrwin()
            if ch in values:
                break
            if not values:
                break
            self.mes_lines.pop()
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
        self.saving = 0  # 0: not saving, 1: saving, 2: save completed

    def save(self):
        """
        Save game status to the database (sqlte3: dl.db via SQLAlchemy).
        Skip saving floor and event data if saved from Edge of Town.
        Called from a separate thread as it is slow.  Not really thread
        safe but it wouldn't do major harm either.
        """
        session = Session()

        # Save party
        party_db = session.query(Party_db).first()
        if not party_db:
            party_db = Party_db()
            session.add(party_db)

        party_db.x = self.party.x
        party_db.y = self.party.y
        party_db.px = self.party.px
        party_db.py = self.party.py
        party_db.floor = self.party.floor
        party_db.pfloor = self.party.pfloor
        party_db.tsubasa_floor = self.party.tsubasa_floor
        party_db.floor_move = self.party.floor_move
        party_db.resumed = self.party.resumed
        party_db.place = self.party.place
        party_db.light_cnt = self.party.light_cnt
        party_db.ac = self.party.ac
        # temporary measure until we have an independent table
        # Note: currently, we don't use "silenced" flag for party
        party_db.silenced = self.dungeon.expedition
        party_db.identify = self.party.identify
        party_db.gps = self.party.gps
        party_db.dungeon_uuid = self.dungeon.uuid

        # session.commit()  # commit party_db.id

        party_db = session.query(Party_db).first()

        # save members
        session.query(Memitems_db).delete()

        for mem in self.characters:
            mem_db = session.query(
                Member_db).filter_by(name=mem.name).first()
            if not mem_db:
                mem_db = Member_db(name=mem.name)
                session.add(mem_db)

            mem_db.name = mem.name
            mem_db.align = mem.align
            mem_db.race = mem.race
            mem_db.level = mem.level
            mem_db.ac = mem.ac
            mem_db.acplus = mem.acplus
            mem_db.job = mem.job
            mem_db.state = mem.state
            mem_db.silenced = mem.silenced
            mem_db.poisoned = mem.poisoned
            mem_db.inspected = mem.inspected
            mem_db.deepest = mem.deepest
            mem_db.floor = mem.floor
            mem_db.in_maze = mem.in_maze
            mem_db.gold = mem.gold
            mem_db.exp = mem.exp
            mem_db.nextexp = mem.nextexp
            mem_db.marks = mem.marks
            mem_db.rip = mem.rip
            mem_db.stat_strength = mem.stat_strength
            mem_db.stat_iq = mem.stat_iq
            mem_db.stat_piety = mem.stat_piety
            mem_db.stat_vitality = mem.stat_vitality
            mem_db.stat_agility = mem.stat_agility
            mem_db.stat_luck = mem.stat_luck
            mem_db.hp = mem.hp
            mem_db.maxhp = mem.maxhp
            mem_db.hpplus = mem.hpplus
            mem_db.mspells = ','.join(mem.mspells)
            mem_db.pspells = ','.join(mem.pspells)
            mem_db.mspell_cnt = ','.join(map(str, mem.mspell_cnt))
            mem_db.pspell_cnt = ','.join(map(str, mem.pspell_cnt))
            mem_db.mspell_max = ','.join(map(str, mem.mspell_max))
            mem_db.pspell_max = ','.join(map(str, mem.pspell_max))
            mem_db.hospitalized = False
            if mem in self.hospitalized:
                mem_db.hospitalized = True
            # session.commit()  # to assign member.id

            # Save member items
            for i in mem.items:
                # We can't save "on sale" status as added later
                mi_db = Memitems_db(name=i.name, equipped=i.equipped,
                                    cursed=i.cursed,
                                    unidentified=i.unidentified,
                                    member_id=mem_db.id)
                session.add(mi_db)

        # Save party members to members table
        for i, mem in enumerate(self.party.members, 1):
            mem_db = session.query(
                Member_db).filter_by(name=mem.name).first()
            mem_db.party_id = party_db.id
            mem_db.party_order = i

        # Save shop inventory
        session.query(Inventory_db).delete()
        for item in self.shopitems.keys():
            if not self.shopitems[item]:
                continue
            inv_db = Inventory_db(name=item, value=self.shopitems[item])
            session.add(inv_db)

        # if in Dungeon
        if self.party.place in [Place.MAZE, Place.CAMP, Place.BATTLE]:
            # Different dungeon
            if not self.dungeon.uuid or \
               party_db.dungeon_uuid != self.dungeon.uuid:
                session.query(Floor_db).delete()
                session.query(Room_db).delete()
                session.query(Fevent_db).delete()
                session.query(Devent_db).delete()

            # Always recreate dungeon events as this is small
            session.query(Devent_db).delete()
            for ev in self.dungeon.events:
                devent_db = Devent_db(loc_type=ev[0], floor=ev[1],
                                      ev_type=ev[2])
                session.add(devent_db)

            # Save floors
            for f in self.dungeon.floors:
                if f is None:
                    continue
                floor_db = session.query(
                    Floor_db).filter_by(floor=f.floor).first()
                if not floor_db:
                    floor_db = Floor_db(
                        x_size=f.x_size, y_size=f.y_size,
                        floor=f.floor, up_x=f.up_x, up_y=f.up_y,
                        down_x=f.down_x, down_y=f.down_y
                    )
                    session.add(floor_db)
                floor_db.floor_orig = f.floor_orig
                floor_db.floor_data = f.floor_data
                # session.commit()  # to define floor.id

                # Save rooms of the floor
                for i, r in enumerate(f.rooms):
                    room_db = session.query(
                        Room_db).filter_by(
                            x=r.x, y=r.y, floor_id=floor_db.id).first()
                    if not room_db:
                        room_db = Room_db(
                            x=r.x, y=r.y, x_size=r.x_size,
                            y_size=r.y_size, center_x=r.center_x,
                            center_y=r.center_y, floor_id=floor_db.id
                        )
                        session.add(room_db)
                    room_db.battled = f.battled[i]

                # Save floor events
                for fek in f.events.keys():
                    fev_db = session.query(
                        Fevent_db).filter_by(
                            x=fek[0], y=fek[1],
                            floor_id=floor_db.id).first()
                    if not fev_db:
                        fev_db = Fevent_db(
                            x=fek[0], y=fek[1],
                            ev_type=f.events[fek][0],
                            floor_id=floor_db.id
                        )
                        session.add(fev_db)
                    fev_db.done = f.events[fek][1]
        else:
            session.query(Floor_db).delete()
            session.query(Room_db).delete()
            session.query(Fevent_db).delete()
            session.query(Devent_db).delete()

        session.commit()  # final commit
        session.close()
        config['newdb'] = False  # can load from database
        self.saving = 2  # saved

    def save_file(self):
        """
        Obsolete.  It is not used anymore.
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
        Load save data from the database.
        If database doesn't exist, load from file for backward
        compatibility.
        Return True if loaded.
        """
        self.vscr.meswins[-1].print("loading..")
        self.vscr.disp_scrwin()
        if config['newdb']:
            return self.load_file()

        session = Session()

        party_db = session.query(Party_db).first()
        if not party_db:
            self.vscr.meswins[-1].print("..oops, no save data.")
            self.vscr.disp_scrwin()
            return False

        # load party
        self.party.x = party_db.x
        self.party.y = party_db.y
        self.party.px = party_db.px
        self.party.py = party_db.py
        self.party.floor = party_db.floor
        self.party.pfloor = party_db.pfloor
        self.party.tsubasa_floor = party_db.tsubasa_floor
        self.party.floor_move = party_db.floor_move
        self.party.place = party_db.place
        self.party.light_cnt = party_db.light_cnt
        self.party.ac = party_db.ac
        # temporary measure until we have an independent table
        # Note: currently, we don't use "silenced" flag for party
        self.dungeon.expedition = party_db.silenced
        self.party.silenced = False
        self.party.identify = party_db.identify
        self.party.gps = party_db.gps
        self.dungeon.uuid = party_db.dungeon_uuid

        # load members
        self.hospitalized = []
        self.characters = []
        for mem_db in session.query(
                Member_db).order_by(Member_db.id):
            mem = Member(mem_db.name, mem_db.align, mem_db.race)
            mem.level = mem_db.level
            mem.ac = mem_db.ac
            mem.acplus = mem_db.acplus
            mem.job = mem_db.job
            mem.state = mem_db.state
            mem.silenced = mem_db.silenced
            mem.poisoned = mem_db.poisoned
            mem.inspected = mem_db.inspected
            mem.deepest = mem_db.deepest
            mem.floor = mem_db.floor
            mem.in_maze = mem_db.in_maze
            mem.gold = mem_db.gold
            mem.exp = mem_db.exp
            mem.nextexp = mem_db.nextexp
            mem.marks = mem_db.marks
            mem.rip = mem_db.rip
            mem.stat_strength = mem_db.stat_strength
            mem.stat_iq = mem_db.stat_iq
            mem.stat_piety = mem_db.stat_piety
            mem.stat_vitality = mem_db.stat_vitality
            mem.stat_agility = mem_db.stat_agility
            mem.stat_luck = mem_db.stat_luck
            mem.hp = mem_db.hp
            mem.maxhp = mem_db.maxhp
            mem.hpplus = mem_db.hpplus
            mem.mspells = mem_db.mspells.split(',')
            if '' in mem.mspells:
                mem.mspells.remove('')
            mem.pspells = mem_db.pspells.split(',')
            if '' in mem.pspells:
                mem.pspells.remove('')
            mem.mspell_cnt = list(map(int, mem_db.mspell_cnt.split(',')))
            mem.pspell_cnt = list(map(int, mem_db.pspell_cnt.split(',')))
            mem.mspell_max = list(map(int, mem_db.mspell_max.split(',')))
            mem.pspell_max = list(map(int, mem_db.pspell_max.split(',')))
            self.characters.append(mem)
            if mem_db.hospitalized:
                self.hospitalized.append(mem)

            # load member items
            mem.items = []
            for mi_db in session.query(
                    Memitems_db).filter_by(member_id=mem_db.id).order_by(
                        Memitems_db.id):
                mem.items.append(Memitem(mi_db.name, mi_db.equipped,
                                         mi_db.cursed,
                                         mi_db.unidentified, False))

        # load party members
        self.party.members = []
        for pmem_db in session.query(
                Member_db).filter_by(party_id=party_db.id).order_by(
                    Member_db.party_order):
            mem = [m for m in self.characters if m.name == pmem_db.name][0]
            self.party.members.append(mem)

        # load shop inventories
        for item_db in session.query(
                Inventory_db).all():
            self.shopitems[item_db.name] = item_db.value

        # if not in Dungeon
        if not self.party.place in [Place.MAZE, Place.CAMP, Place.BATTLE]:
            session.close()
            self.vscr.meswins[-1].print("loaded.")
            self.vscr.disp_scrwin()
            self.party.resumed = False
            return True

        self.party.resumed = True  # party_db.resumed

        # load dungeon events
        self.dungeon.events = []
        for dev_db in session.query(
                Devent_db).all():
            self.dungeon.events.append((dev_db.loc_type,
                                        dev_db.floor,
                                        dev_db.ev_type))

        # load floors
        self.dungeon_floors = []
        for floor_db in session.query(
                Floor_db).order_by(Floor_db.floor):
            f = Floor(floor_db.x_size, floor_db.y_size,
                      floor_db.floor, bytearray(floor_db.floor_data))
            f.floor_orig = bytearray(floor_db.floor_orig)
            f.up_x = floor_db.up_x
            f.up_y = floor_db.up_y
            f.down_x = floor_db.down_x
            f.down_y = floor_db.down_y

            # load rooms on the floor
            f.rooms = []
            for room_db in session.query(
                    Room_db).filter_by(
                        floor_id=floor_db.id).order_by(Room_db.id):
                r = Room(room_db.x, room_db.y, room_db.x_size,
                         room_db.y_size)
                f.rooms.append(r)
                f.battled.append(room_db.battled)

            # load floor events
            for i, fev_db in enumerate(session.query(
                    Fevent_db).filter_by(floor_id=floor_db.id)):
                f.events[(fev_db.x, fev_db.y)] = \
                    [fev_db.ev_type, fev_db.done]

            while True:
                if len(self.dungeon.floors) < f.floor-1:
                    self.dungeon.floors.append(None)
                else:
                    break
            self.dungeon.floors.append(f)

        self.party.floor_obj = self.dungeon.floors[self.party.floor-1]

        session.close()
        self.vscr.meswins[-1].print("loaded.")
        self.vscr.disp_scrwin()
        return True

    def load_file(self):
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


class Member_db(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    align = Column(sqlalchemy.Enum(Align))
    race = Column(sqlalchemy.Enum(Race))
    level = Column(Integer)
    ac = Column(Integer)
    acplus = Column(Integer)
    job = Column(sqlalchemy.Enum(Job))
    state = Column(sqlalchemy.Enum(State))
    silenced = Column(Boolean)
    poisoned = Column(Boolean)
    inspected = Column(Boolean)
    deepest = Column(Integer)
    floor = Column(Integer)
    in_maze = Column(Boolean)
    gold = Column(Integer)
    exp = Column(Integer)
    nextexp = Column(Integer)
    marks = Column(Integer)
    rip = Column(Integer)
    stat_strength = Column(Integer)
    stat_iq = Column(Integer)
    stat_piety = Column(Integer)
    stat_vitality = Column(Integer)
    stat_agility = Column(Integer)
    stat_luck = Column(Integer)
    hp = Column(Integer)
    maxhp = Column(Integer)
    hpplus = Column(Integer)
    mspells = Column(String)
    pspells = Column(String)
    mspell_cnt = Column(String)
    pspell_cnt = Column(String)
    mspell_max = Column(String)
    pspell_max = Column(String)
    party_id = Column(Integer, ForeignKey('party.id'))
    party_order = Column(Integer)
    hospitalized = Column(Boolean)


class Memitems_db(Base):
    __tablename__ = 'member_items'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    equipped = Column(Boolean)
    cursed = Column(Boolean)
    unidentified = Column(Boolean)
    member_id = Column(Integer, ForeignKey('members.id'))


class Party_db(Base):
    __tablename__ = 'party'

    id = Column(Integer, primary_key=True)
    x = Column(Integer)
    y = Column(Integer)
    px = Column(Integer)
    py = Column(Integer)
    floor = Column(Integer)
    pfloor = Column(Integer)
    tsubasa_floor = Column(Integer)
    floor_move = Column(Integer)
    resumed = Column(Boolean)
    place = Column(sqlalchemy.Enum(Place))
    # floor_obj = Column(LargeBinary)
    light_cnt = Column(Integer)
    ac = Column(Integer)
    silenced = Column(Boolean)
    identify = Column(Boolean)
    gps = Column(Boolean)
    dungeon_uuid = Column(String)

    members = relationship("Member_db")


class Floor_db(Base):
    __tablename__ = 'floor'

    id = Column(Integer, primary_key=True)
    x_size = Column(Integer)
    y_size = Column(Integer)
    floor = Column(Integer)
    floor_data = Column(LargeBinary)
    floor_orig = Column(LargeBinary)
    up_x = Column(Integer)
    up_y = Column(Integer)
    down_x = Column(Integer)
    down_y = Column(Integer)
    rooms = relationship("Room_db", back_populates="floor")
    events = relationship("Fevent_db", back_populates="floor")


class Room_db(Base):
    __tablename__ = 'room'

    id = Column(Integer, primary_key=True)
    x = Column(Integer)
    y = Column(Integer)
    x_size = Column(Integer)
    y_size = Column(Integer)
    center_x = Column(Integer)
    center_y = Column(Integer)
    battled = Column(Boolean)
    floor_id = Column(Integer, ForeignKey('floor.id'))
    floor = relationship("Floor_db", back_populates="rooms")


class Fevent_db(Base):
    __tablename__ = 'floor_events'

    id = Column(Integer, primary_key=True)
    x = Column(Integer)
    y = Column(Integer)
    ev_type = Column(sqlalchemy.Enum(Eventid))
    done = Column(Boolean)
    floor_id = Column(Integer, ForeignKey('floor.id'))
    floor = relationship("Floor_db", back_populates="events")


class Devent_db(Base):
    __tablename__ = 'dungeon_events'

    id = Column(Integer, primary_key=True)
    loc_type = Column(sqlalchemy.Enum(Evloctype))
    ev_type = Column(sqlalchemy.Enum(Eventid))
    floor = Column(Integer)


class Inventory_db(Base):
    __tablename__ = 'shop_inventory'

    name = Column(String, primary_key=True)
    value = Column(Integer)


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

    def todic(self):
        """
        Return dict of the party (for serialization).  Member objects 
        are also converted to dict.  Doesn't include floor_obj.
        """
        pdic = {
            'x': self.x, 'y': self.y, 'px': self.px, 'py': self.py,
            'floor': self.floor, 'pfloor': self.pfloor,
            'tsubasa_floor': self.tsubasa_floor,
            'place': self.place.name, 'members': [],
            'light_cnt': self.light_cnt, 'ac': self.ac,
            'silenced': self.silenced, 'identify': self.identify,
            'gps': self.gps,
        }
        for m in self.members:
            pdic['members'].append(m.todic())
        return pdic

    def fromdic(self, p_s):
        """
        Update self with p_s (serialized party dict)
        """
        self.x = p_s['x']
        self.y = p_s['y']
        self.px = p_s['px']
        self.py = p_s['py']
        self.floor = p_s['floor']
        self.pfloor = p_s['pfloor']
        self.tsubasa_floor = p_s['tsubasa_floor']
        self.place = Place[p_s['place']]
        self.members = []
        self.light_cnt = p_s['light_cnt']
        self.ac = p_s['ac']
        self.silenced = p_s['silenced']
        self.identify = p_s['identify']
        self.gps = p_s['gps']
        for m_s in p_s['members']:
            m = Member('dummy', Align.GOOD, Race.HUMAN)
            m.fromdic(m_s)
            self.members.append(m)

    def injured(self):
        """
        Check if someone (in group camp) is injured and return True/False
        dead, ashed, lost members are not counted
        """
        for mem in self.members:
            if mem.state in [State.DEAD, State.ASHED, State.LOST]:
                continue
            if mem.hp < mem.maxhp:
                return True

        ulist = game.dungeon.get_gcamp_users()
        for user in ulist:
            p = game.dungeon.parties[user]
            for mem in p.members:
                if mem.state in [State.DEAD, State.ASHED, State.LOST]:
                    continue
                if mem.hp < mem.maxhp:
                    return True
        return False

    def cast_spell(self, spell, target='party'):
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
                p = game.party
                ulist = [user for user, loc in game.dungeon.party_locs.items()
                         if loc[3] == Place.CAMP.name and loc[0] == p.x and
                         loc[1] == p.y and loc[2] == p.floor
                         and user != config['server']['auth']['user']]
                if ulist:
                    for owner in ulist:
                        data = {'user': owner, 'spell': spell,
                                'caster': mem.name, 'target': target}
                        sio.emit('cast_spell', data)
                getch(wait=True)
                return True
        return False

    def prep(self):
        """
        Cast hogo, shikibetsu, gps and lomilwa
        """
        if self.ac == 0:
            self.cast_spell('hogo')
        if not self.identify:
            self.cast_spell('shikibetsu')
        if not self.gps:
            self.cast_spell('gps')
        if self.light_cnt < 1000:
            self.cast_spell('hikarinotama')

    def heal(self):
        """
        Heal all members in the party
        """
        while self.injured():
            if not self.cast_spell('zenkai'):
                if not self.cast_spell('zenjiai'):
                    break
        for mem in self.members:
            if mem.state in [State.DEAD, State.ASHED, State.LOST]:
                continue
            if mem.hp == mem.maxhp:
                continue
            if not self.cast_spell('kanzen', mem):
                if not self.cast_spell('daikaifuku', mem):
                    if not self.cast_spell('iyashi', mem):
                        if not self.cast_spell('jiai', mem):
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
        self.push_loc()

    def push_loc(self):
        """
        Push location and place (MAZE, BATTLE, CAMP) to server
        if in a server dungeon
        """
        if game.dungeon.expedition:
            locdict = {}
            locdict['x'] = self.x
            locdict['y'] = self.y
            locdict['floor'] = self.floor
            locdict['place'] = self.place.name
            sio.emit('party_move', locdict)

    def calc_hpplus(self):
        """
        Calc poison and healing item effects for the party members
        """
        for mem in self.members:
            mem.hpplus = sum(game.itemdef[item.name].hp
                             for item in mem.items)
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
            if it in [item.name for mem in self.members
                      for item in mem.items]:
                return True
        return False

    def reorder(self):
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

    def can_open(self, ch=b'*'):
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

    def choose_character(self):
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

    def remove_character(self):
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
        # list of Memitem(name, equipped, cursed, unidentified, onsale)
        # on sale status is only used in group camps and not saved/loaded
        self.items = []
        self.stat_strength, self.stat_iq, self.stat_piety, \
            self.stat_vitality, self.stat_agility, self.stat_luck \
            = race_status[race]
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
        return f"<{self.name}, {self.align.name[:1]}-{self.race.name[:3]}-{self.job.name[:3]} {self.stat_strength}/{self.stat_iq}/{self.stat_piety}/{self.stat_vitality}/{self.stat_agility}>"

    def __str__(self):
        return f"{self.name[:16].ljust(16)} Lv{self.level:3d} {self.race.name[:3].lower()}-{self.align.name[:1].lower()}-{self.job.name[:3].lower()}"

    def todic(self):
        """
        Return the member as a dictionary (for serialization)
        """
        mdic = {'name': self.name, 'align': self.align.name,
                'race': self.race.name, 'level': self.level,
                'ac': self.ac, 'job': self.job.name,
                'state': self.state.name, 'poisoned': self.poisoned,
                'deepest': self.deepest, 'gold': self.gold,
                'exp': self.exp, 'nextexp': self.nextexp,
                'marks': self.marks, 'rip': self.rip,
                # Convert dataclass Memietm to dict
                'items': [item.__dict__ for item in self.items],
                'stat_strength': self.stat_strength,
                'stat_iq': self.stat_iq,
                'stat_piety': self.stat_piety,
                'stat_vitality': self.stat_vitality,
                'stat_agility': self.stat_agility,
                'stat_luck': self.stat_luck,
                'maxhp': self.maxhp, 'hp': self.hp,
                'hpplus': self.hpplus,
                'mspells': self.mspells[:],
                'pspells': self.pspells[:],
                'mspell_cnt': self.mspell_cnt[:],
                'pspell_cnt': self.pspell_cnt[:],
                'mspell_max': self.mspell_max[:],
                'pspell_max': self.pspell_max[:],
                }
        return mdic

    def fromdic(self, m_s):
        """
        Update self with m_s (serialized Member dict)
        """
        self.name = m_s['name']
        self.align = Align[m_s['align']]
        self.race = Race[m_s['race']]
        self.level = m_s['level']
        self.ac = m_s['ac']
        self.job = Job[m_s['job']]
        self.state = State[m_s['state']]
        self.poisoned = m_s['poisoned']
        self.deepest = m_s['deepest']
        self.gold = m_s['gold']
        self.exp = m_s['exp']
        self.nextexp = m_s['nextexp']
        self.marks = m_s['marks']
        self.rip = m_s['rip']
        self.items = [Memitem(**idic) for idic in m_s['items']]
        self.stat_strength = m_s['stat_strength']
        self.stat_iq = m_s['stat_iq']
        self.stat_piety = m_s['stat_piety']
        self.stat_vitality = m_s['stat_vitality']
        self.stat_agility = m_s['stat_agility']
        self.stat_luck = m_s['stat_luck']
        self.maxhp = m_s['maxhp']
        self.hp = m_s['hp']
        self.hpplus = m_s['hpplus']
        self.mspells = m_s['mspells'][:]
        self.pspells = m_s['pspells'][:]
        self.mspells = m_s['mspells'][:]
        self.pspells = m_s['pspells'][:]
        self.mspell_cnt = m_s['mspell_cnt'][:]
        self.pspell_cnt = m_s['pspell_cnt'][:]
        self.mspell_max = m_s['mspell_max'][:]
        self.pspell_max = m_s['pspell_max'][:]

    def disp_character(self):
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
            f"strength {self.stat_strength:2d}  gold {self.gold:16d}   lvl {self.level:5d}", start=' ')
        mw.print(
            f"    i.q. {self.stat_iq:2d}  e.p. {self.exp:16d}   rip {self.rip:5d}", start=' ')
        mw.print(
            f"   piety {self.stat_piety:2d}  next {self.nextexp:16d}   a.c.{self.ac:5d}", start=' ')
        mw.print(
            f"vitality {self.stat_vitality:2d}  marks {self.marks:15d}   depth{self.deepest:4d}", start=' ')
        mw.print(
            f" agility {self.stat_agility:2d}  h.p.  {self.hp:7d}/{self.maxhp:7d}", start=' ')
        if self.state == State.OK and self.poisoned:
            mw.print(
                f"    luck {self.stat_luck:2d}  status   POISONED", start=' ')
        else:
            mw.print(
                f"    luck {self.stat_luck:2d}  status   {self.state.name}", start=' ')
        mw.print(f"", start=' ')
        mw.print(f"mage  {self.mspell_cnt[0]}/{self.mspell_cnt[1]}/{self.mspell_cnt[2]}/{self.mspell_cnt[3]}/{self.mspell_cnt[4]}/{self.mspell_cnt[5]}/{self.mspell_cnt[6]}   priest  {self.pspell_cnt[0]}/{self.pspell_cnt[1]}/{self.pspell_cnt[2]}/{self.pspell_cnt[3]}/{self.pspell_cnt[4]}/{self.pspell_cnt[5]}/{self.pspell_cnt[6]}/", start=' ')
        for idx in range(8):
            try:
                item = self.items[idx]
                m = ' '
                if self.job.name[:1].lower() not in \
                   game.itemdef[item.name].jobs.lower():
                    m = '#'  # can't equip
                if item.onsale:
                    m = '$'  # on sale
                if item.equipped:
                    m = '*'  # equipped
                if item.cursed:
                    m = '&'  # cursed
                if item.unidentified:  # unidentified
                    l = f"{m}?{game.itemdef[item.name].unident}"
                else:
                    l = f"{m}{item.name}"
            except:
                l = ''
            if idx % 2:
                mw.print(f"{idx}) {ol.ljust(18)} {idx+1}) {l.ljust(18)}",
                         start=' ')
            ol = l

    def inspect_character(self):
        """
        Inspect a character
        Show the character info and dispatch item or spell menus
        """
        mw = game.vscr.meswins[-1]
        while game.party.members:
            if game.party.floor_move and game.party.place == Place.CAMP:
                break
            self.disp_character()
            mw.print(f"", start=' ')
            if game.party.place == Place.CAMP and game.dungeon.expedition\
               and game.vscr.show_puser != config['server']['auth']['user']:
                c1 = mw.input_char("jk)change member l)leave",
                                   values=['j', 'k', 'l', 'm'])
            elif game.party.place == Place.CAMP and \
                    (ulist := game.dungeon.get_gcamp_users()):
                c1 = mw.input_char(
                    "i)tems s)pells c)lass b)uy jk)change member l)leave",
                    values=['i', 's', 'c', 'b', 'j', 'k', 'l', 'm'])
            else:
                c1 = mw.input_char(
                    "i)tems s)pells c)lass jk)change member l)leave",
                    values=['i', 's', 'c', 'j', 'k', 'l', 'm'])
            if c1 == 'l':
                mw.cls()
                return 0  # leave
            elif c1 == 'i':
                self.item_menu()
            elif c1 == 's':
                self.spell_menu()
            elif c1 == 'c' and game.party.place == Place.TRAINING_GROUNDS:
                self.change_classes()
            elif c1 == 'j':
                return 1  # next member
            elif c1 == 'k':
                return -1  # previous member
            elif c1 == 'm':
                send_message()
            elif c1 == 'b':  # see on sale items
                self.buy_onsale(ulist)
        return 0

    def buy_onsale(self, ulist):
        """
        See on sale items in the group camp users
        sio.emit('buy', buy_item_dict) if you chose to buy one
        """
        if not ulist:
            return
        mw = Meswin(game.vscr, 14, 4, 52, 12, frame=True)
        game.vscr.meswins.append(mw)
        mw.print("These items are on sale:")
        items = []  # (idx, user, mem, item, price)
        idx = 1
        for user in ulist:
            for mem in game.dungeon.parties[user].members:
                for item_idx, item in enumerate(mem.items):
                    if game.itemdef[item.name].level < 10 and \
                       not item.equipped and not item.cursed and \
                       not item.unidentified and item.onsale:
                        idct = {'idx': idx, 'seller': user,
                                'buyer': config['server']['auth']['user'],
                                'member': mem.name, 'item': item.name,
                                'item_idx': item_idx,
                                'price': game.itemdef[item.name].price*7//10,
                                'buyer_member': self.name}
                        items.append(idct)
                        idx += 1
        for i in items:
            mw.print(
                f"{i['idx']:2d} {i['item'].ljust(16)} {i['price']:6d} ({i['seller'].ljust(10)})", start=' ')
        while True:
            num = mw.input("Which item to buy? (# or l)eave)")
            try:
                num = int(num)
                idct = next(idct for idct in items if idct['idx'] == num)
                break
            except:
                if num == 'l':
                    game.vscr.meswins.pop()
                    return
        if idct['price'] > sum(mem.gold for mem in game.party.members):
            mw.print("You can't afford it.")
            game.vscr.disp_scrwin()
            getch()
        else:
            sio.emit('buy', idct)
            mw.print("Processing.")
            game.vscr.disp_scrwin()
            getch()
            game.vscr.meswins.pop()
            game.vscr.disp_scrwin()
        return

    def view_spells(self):
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

    def spell_menu(self):
        """
        Spell menu.  Cast, read spells.
        """
        v = game.vscr
        mw = Meswin(v, 12, 4, 52, 12, frame=True)
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
                self.view_spells()
        # mw.cls()
        v.disp_scrwin()
        v.meswins.pop()
        v.cls()

    def item_menu(self):
        """
        Item menu.  Use, equip, trade, drop an item.
        """
        vscr = game.vscr
        iw = Meswin(vscr, 14, 2, 56, 8, frame=True)
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
            dispname = self.items[inum].name
            if self.items[inum].unidentified:  # unidentified
                dispname = ''.join(['?', game.itemdef[dispname].unident])
            iw.print(f"{inum+1}) {dispname}", start=' ')
            if not game.dungeon.expedition or\
               self.items[inum].equipped or self.items[inum].cursed or\
               self.items[inum].unidentified:
                c = iw.input_char("u)se e)quip t)rade d)rop l)eave",
                                  values=['u', 'e', 't', 'd', 'l'])
            else:
                c = iw.input_char("u)se e)quip t)rade d)rop o)n sale l)eave",
                                  values=['u', 'e', 't', 'd', 'o', 'l'])

            if c == 'l':
                continue
            elif c == 'u':
                if self.items[inum].unidentified:  # unidentified:
                    iw.print(f"Tried to use {dispname}.")
                    iw.print(
                        ".. but don't know how to use it.", start=' ')
                    vscr.disp_scrwin()
                    continue
                itemdef = game.itemdef[self.items[inum].name]
                if not itemdef.use:
                    iw.print(f"Tried to use {dispname}.")
                    iw.print(".. but wasn't able to.", start=' ')
                    vscr.disp_scrwin()
                elif itemdef.use == 'etc':
                    iw.print(f"Used {dispname}.")
                    vscr.disp_scrwin()
                    if self.items[inum].name == 'murasama blade':
                        self.stat_strength += 1  # str+1
                    elif self.items[inum].name == 'kaiser knuckles':
                        self.maxhp += 1  # hp+1
                    elif self.items[inum].name == 'armor of lords':
                        for m in game.party.members:
                            m.hp = m.maxhp
                    elif self.items[inum].name == 'ninja dagger':
                        self.job = Job.NINJA
                        for i in self.items:
                            i.equipped = False
                    if itemdef.brk > random.randrange(100):
                        self.items[inum].name = 'broken item'
                        self.items[inum].equipped = False
                    getch(wait=True)
                    vscr.meswins.pop()
                    vscr.cls()
                    return
                else:  # magic spell
                    sdef = game.spelldef[itemdef.use]
                    if not sdef.camp:
                        iw.print("Can't use it now.")
                    if sdef.target == 'member':
                        if not game.dungeon.get_gcamp_users():
                            target = game.party.choose_character()
                            if not target:
                                iw.print("Aborted.", start=' ')
                                continue
                        else:
                            owner, uidx = choose_party_character()
                            if not owner:
                                iw.print("Aborted.", start=' ')
                                continue
                            if owner == config['server']['auth']['user']:
                                target = game.party.members[uidx]
                            else:
                                # Use item to other party member
                                tname = game.dungeon.parties[owner].members[uidx].name
                                data = {'user': owner,
                                        'spell': itemdef.use,
                                        'caster': self.name,
                                        'target': tname}
                                sio.emit('cast_spell', data)
                                iw.print(f"Used {dispname}.")
                                vscr.disp_scrwin()
                                if itemdef.brk > random.randrange(100):
                                    self.items[inum].name = 'broken item'
                                vscr.meswins.pop()
                                vscr.cls()
                                return
                    else:
                        target = sdef.target
                    iw.print(f"Used {dispname}.")
                    vscr.disp_scrwin()
                    game.spell.cast_spell_dispatch(
                        self, itemdef.use, target)
                    if itemdef.brk > random.randrange(100):
                        self.items[inum].name = 'broken item'
                    vscr.meswins.pop()
                    vscr.cls()
                    return
            elif c == 't':
                if self.items[inum].cursed:
                    iw.print(f"Cursed.")
                    vscr.disp_scrwin()
                    continue
                elif self.items[inum].equipped:
                    iw.print(f"Equipped.")
                    vscr.disp_scrwin()
                    continue
                target = game.party.choose_character()
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
                if self.items[inum].cursed:
                    iw.print(f"Cursed.")
                    vscr.disp_scrwin()
                    continue
                elif self.items[inum].equipped:
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
                if self.job.name[:1] not in game.itemdef[self.items[inum].name].jobs:
                    iw.print("Can't equip the item.")
                    continue
                for item in self.items:
                    if game.itemdef[self.items[inum].name].type \
                       == game.itemdef[item.name].type:
                        if item.cursed:  # already cursed
                            iw.print("Already equipped a cursed item.")
                            break
                        elif item.equipped:  # equipped
                            item.equipped = False
                            if item is self.items[inum]:
                                self.calc_ac()
                                vscr.meswins.pop()
                                vscr.cls()
                                return
                if game.itemdef[self.items[inum].name].curse:
                    self.items[inum].cursed = True  # cursed
                    iw.print("Cursed!")
                    vscr.disp_scrwin()
                    getch()
                self.items[inum].equipped = True  # equipped
                self.calc_ac()
                vscr.meswins.pop()
                vscr.cls()
                # vscr.disp_scrwin()
                return
            elif c == 'o':
                self.items[inum].onsale = not self.items[inum].onsale
                if game.dungeon.expedition:
                    if self.items[inum].onsale:
                        sio.emit(
                            'message', f"Just put <{self.items[inum].name}> on sale")
                        data = {'requester': None,
                                'party_s': game.party.todic()}
                        sio.emit('update_party', data)
                vscr.meswins.pop()
                vscr.cls()
                return

    def calc_ac(self):
        """
        Utility method to calculate AC
        """
        self.ac = 10
        for item in self.items:
            if item.equipped or item.cursed:
                self.ac += game.itemdef[item.name].ac

    def job_applicable(self, sp, jobnum):
        """
        Utility function to check if the character is applicable for the job
        """
        for i in range(6):
            if sp[i]+[self.stat_strength, self.stat_iq, self.stat_piety,
                      self.stat_vitality, self.stat_agility,
                      self.stat_luck][i] < job_requirements[Job(jobnum)][i]:
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

    def bonus_disp(self, bonus, y, sp):
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
        mw.print(f"  strength  {sp[0]+self.stat_strength:2d}", start=' ')
        mw.print(f"  iq        {sp[1]+self.stat_iq:2d}", start=' ')
        mw.print(f"  piety     {sp[2]+self.stat_piety:2d}", start=' ')
        mw.print(f"  vitality  {sp[3]+self.stat_vitality:2d}", start=' ')
        mw.print(f"  agility   {sp[4]+self.stat_agility:2d}", start=' ')
        mw.print(f"  luck      {sp[5]+self.stat_luck:2d}", start=' ')
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

    def change_classes(self):
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
            item.equipped = item.cursed = False
        self.calc_ac()
        self.stat_strength = race_status[self.race][0]
        self.stat_iq = race_status[self.race][1]
        self.stat_piety = race_status[self.race][2]
        self.stat_vitality = race_status[self.race][3]
        self.stat_agility = race_status[self.race][4]
        self.stat_luck = race_status[self.race][5]
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

    def distribute_bonus(self):
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
            job = self.bonus_disp(bonus, y, statplus)
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
            elif c == 'l' \
                and (statplus[y] +
                      [self.stat_strength, self.stat_iq,
                       self.stat_piety, self.stat_vitality,
                       self.stat_agility, self.stat_luck][y])\
                < race_status[self.race][y]+10 \
                    and bonus > 0:
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

        self.stat_strength += statplus[0]
        self.stat_iq += statplus[1]
        self.stat_piety += statplus[2]
        self.stat_vitality += statplus[3]
        self.stat_agility += statplus[4]
        self.stat_luck += statplus[5]
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

    def __init__(self):
        pass

    def cancast(self, mem, spell, consume=False):
        """
        Check if mem has mastered the spell and has MP
        Return True if can (and consumed if concume=True)
        Return False if can not
        """
        if mem.state not in [State.OK]:
            return False
        spelldef = game.spelldef[spell]
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
            if not game.dungeon.expedition or not game.dungeon.parties:
                target = game.party.choose_character()
                if not target:
                    mw = game.vscr.meswins[-1]
                    mw.print("Aborted.", start=' ')
                    return
            else:
                owner, uidx = choose_party_character()
                if not owner:
                    mw = game.vscr.meswins[-1]
                    mw.print("Aborted.", start=' ')
                    return
                if owner == config['server']['auth']['user']:
                    target = game.party.members[uidx]
                else:
                    # cast spell to other party member
                    tname = game.dungeon.parties[owner].members[uidx].name
                    data = {'user': owner, 'spell': s, 'caster': mem.name,
                            'target': tname}
                    sio.emit('cast_spell', data)
                    mw.print(f"{mem.name} started casting {s}", start=' ')
                    sdef = game.spelldef[s]
                    if sdef.categ == 'mage':
                        splcntlst = mem.mspell_cnt
                    else:
                        splcntlst = mem.pspell_cnt
                    splcntlst[sdef.level-1] -= 1
                    v.disp_scrwin()
                    return
        elif sdef.target in ['enemy', 'group']:
            target = game.battle.choose_group()
            if not target:
                mw = game.vscr.meswins[-1]
                mw.print("Aborted.", start=' ')
                return
        else:
            target = sdef.target
            p = game.party
            ulist = [user for user, loc in game.dungeon.party_locs.items()
                     if loc[3] == Place.CAMP.name and loc[0] == p.x and
                     loc[1] == p.y and loc[2] == p.floor
                     and user != config['server']['auth']['user']]
            if ulist and s not in ['tsubasa']:
                for owner in ulist:
                    data = {'user': owner, 'spell': s, 'caster': mem.name,
                            'target': target}
                    sio.emit('cast_spell', data)

        splcntlst[sdef.level-1] -= 1

        mw.print(f"{mem.name} started casting {s}", start=' ')
        v.disp_scrwin()
        self.cast_spell_dispatch(mem, s, target)

    def cast_spell_dispatch(self, invoker, spell, target):
        sdef = game.spelldef[spell]
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
        if game.dungeon.expedition and game.dungeon.parties:
            data = {'requester': None,
                    'party_s': game.party.todic()}
            sio.emit('update_party', data)  # send my party info

    def cure(self, invoker, spell, target):
        """
        Spell to cure bad status
        """
        v = game.vscr
        mw = v.meswins[-1]
        spelldef = game.spelldef[spell]
        if spell == 'okiro':
            if target.state in [State.ASLEEP, State.PARALYZED]:
                target.state = State.OK
                mw.print(f"{target.name} is awaken.", start=' ', bcast=True)
                v.disp_scrwin()
        elif spell == 'gedoku':
            if target.poisoned:
                target.poisoned = False
                target.hpplus += 1
                mw.print(f"{target.name} is cured.", start=' ', bcast=True)
                v.disp_scrwin()

    def etc(self, invoker, spell, target):
        """
        Misc spell
        """
        v = game.vscr
        mw = v.meswins[-1]
        spelldef = game.spelldef[spell]
        update = False  # update monp flag (joined battle in a server dungeon)
        if spell == 'gps':
            game.party.gps = True
        elif spell == 'tsubasa':
            party = game.party
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
            game.party.identify = True
        elif spell == 'hogo':
            game.party.ac = int(spelldef.value)
        elif spell == 'akari':
            game.party.light_cnt += random.randrange(15) + 30
        elif spell == 'hikarinotama':
            game.party.light_cnt += 9999
        elif spell == 'kanzen':
            if target.state not in [State.DEAD, State.ASHED, State.LOST]:
                target.hp = target.maxhp
                target.state = State.OK
                if target.poisoned:
                    target.poisoned = False
                game.party.calc_hpplus()
                mw.print(f"{target.name} is completely healed.",
                         start=' ', bcast=True)
        elif spell == 'senmetsu':
            monptmp = game.battle.monp[:]
            for mong in monptmp:
                mondef = game.mondef[mong.name]
                if mong.identified:
                    dispname = mondef.names
                else:
                    dispname = mondef.unidents
                if mondef.weakmaka:
                    game.battle.exp += mong.num_valid() * \
                        mondef.exp
                    monsterg = mong.monsters
                    for mon in monsterg:
                        mon.state = State.DEAD
                    mw.print(f"{dispname} are perished.",
                             start=' ', bcast=True)
                    v.disp_scrwin()
                    update = True
        elif spell == 'hinshi':
            if isinstance(invoker, Member):
                mondef = game.mondef[target.name]
                if target.identified:
                    disptarget = target.name
                else:
                    disptarget = mondef.unident
                if random.randrange(100) >= mondef.regspellp:

                    damage = max(
                        target.top_valid().hp - random.randrange(7) - 1, 0)
                    target.top_valid().hp -= damage
                    mw.print(
                        f"{disptarget} incurred {damage} damage.", start=' ', bcast=True)
                    update = True
                else:
                    mw.print(f"{disptarget} registed the spell.",
                             start=' ', bcast=True)
            else:
                target = random.choice([mem for mem in game.party.members
                                        if mem.state in [State.OK, State.ASLEEP]])
                regspellp = target.stat_luck * 100/20  # luck
                if random.randrange(100) >= regspellp:
                    damage = max(target.hp - random.randrange(7) - 1, 0)
                    target.hp -= damage
                    mw.print(
                        f"{target.name} incurred {damage} damage.", start=' ', bcast=True)
                    update = True
                else:
                    mw.print(f"{target.name} registed the spell.",
                             start=' ', bcast=True)
        elif spell == 'sosei':  # party member only
            if target.state != State.DEAD:
                mw.print(f"{target.name} is not dead.", start=' ')
            else:
                chance = (target.stat_vitality+target.stat_luck) * 100//45
                if random.randrange(100) < chance:
                    mw.print(f"{target.name} is resurrected.",
                             start=' ', bcast=True)
                    target.stat_vitality -= 1
                    target.state = State.OK
                    target.hp = min(target.maxhp, random.randrange(7)+1)
                else:
                    mw.print(
                        f"Failed to resurrect {target.name}.", start=' ', bcast=True)
                    target.state = State.ASHED
        elif spell == 'fukkatsu':
            if target.state not in [State.DEAD, State.ASHED]:
                mw.print(f"{target.name} is not dead or ashed.",
                         start=' ', bcast=True)
            else:
                chance = (target.stat_vitality+target.stat_luck) * 100//40
                if random.randrange(100) < chance:
                    mw.print(f"{target.name} is resurrected.",
                             start=' ', bcast=True)
                    target.stat_vitality -= 1
                    target.state = State.OK
                    target.hp = target.maxhp
                else:
                    mw.print(
                        f"Failed to resurrect {target.name}.", start=' ', bcast=True)
                    if target.state == State.DEAD:
                        target.state = State.ASHED
                    else:  # was ashed
                        target.state = State.LOST
        if update:
            game.battle.update_monp()

    def ac(self, invoker, spell, target):
        """
        Decrease peer(s)' or increase opponent(s)' AC
        """
        v = game.vscr
        mw = v.meswins[-1]
        spelldef = game.spelldef[spell]
        update = False
        if spelldef.target == 'self':
            if isinstance(invoker, Member):
                invoker.acplus += int(spelldef.value)
            else:
                invoker.ac += int(spelldef.value)
                update = True
        elif spelldef.target == 'party':
            if isinstance(invoker, Member):
                for m in game.party.members:
                    m.acplus += int(spelldef.value)
            else:
                mong = next((mong for mong in game.battle.monp
                             if mong.top_valid()), game.battle.monp[0])
                for m in mong.monsters:
                    m.ac += int(spelldef.value)
                update = True
        elif spelldef.target == 'enemy':
            if isinstance(invoker, Member):
                target.top_valid().ac += int(spelldef.value)
                update = True
            else:
                mem = random.choice(game.party.members)
                mem.acplus += int(spelldef.value)
        elif spelldef.target == 'group':
            if isinstance(invoker, Member):
                for mon in target.monsters:
                    mon.ac += int(spelldef.value)
                update = True
            else:
                for mem in game.party.members:
                    mem.acplus += int(spelldef.value)
        else:  # 'all'
            if isinstance(invoker, Member):
                for mong in game.battle.monp:
                    for mon in mong:
                        mon.ac += int(spelldef.value)
                update = True
            else:
                for mem in game.party.members:
                    mem.acplus += int(spelldef.value)
        if update:
            game.battle.update_monp()

    def status(self, invoker, spell, target):
        """
        Spells that could put to sleep and silence the target group.
        """
        v = game.vscr
        mw = v.meswins[-1]
        spelldef = game.spelldef[spell]
        update = False
        if isinstance(invoker, Member):
            if target.identified:
                disptarget = target.name
            else:  # unidentified
                disptarget = game.mondef[target.name].unident
            for mon in target.monsters:
                if 'sleep' in spelldef.attr and mon.state == State.OK:
                    if mon.mdef.weaksleep:
                        chance = 80
                    else:
                        chance = 35
                    if random.randrange(100) < chance and \
                       random.randrange(100) >= mon.mdef.regspellp:
                        mon.state = State.ASLEEP
                        update = True
                    if mon.state == State.ASLEEP:
                        mw.print(f"{disptarget} is slept.",
                                 start=' ', bcast=True)
                    else:
                        mw.print(f"{disptarget} is not slept.",
                                 start=' ', bcast=True)
                if 'silence' in spelldef.attr:
                    chance = 50 * mon.mdef.regspellp // 100
                    if random.randrange(100) < chance or mon.silenced:
                        mon.silenced = True
                        update = True
                        mw.print(f"{disptarget} is silenced.",
                                 start=' ', bcast=True)
                    else:
                        mw.print(f"{disptarget} is not silenced.",
                                 start=' ', bcast=True)
        else:
            for mem in game.party.members:
                if 'sleep' in spelldef.attr and mem.state == State.OK:
                    if random.randrange(100) < 35:
                        mem.state = State.ASLEEP
                    if mem.state == State.ASLEEP:
                        mw.print(f"{mem.name} is slept.",
                                 start=' ', bcast=True)
                    else:
                        mw.print(f"{mem.name} is not slept.",
                                 start=' ', bcast=True)
                if 'slience' in spelldef.attr and \
                   (mem.mspells or mem.pspells):
                    if random.randrange(100) < 50:
                        mem.silenced = True
                    if mem.silenced:
                        mw.print(f"{mem.name} is slept.",
                                 start=' ', bcast=True)
                    else:
                        mw.print(f"{mem.name} is not slept.",
                                 start=' ', bcast=True)
        if update:
            game.battle.update_monp()

    def death_single(self, target, disptarget):
        """
        Spells that cause instant death to a single enemy
        """
        mw = game.vscr.meswins[-1]
        update = False
        if isinstance(target, Monster):
            regdeathp = game.mondef[target.name].regdeathp
        else:
            # vitality + luck
            regdeathp = (target.stat_vitality + target.stat_luck) * 100//40
        if random.randrange(100) >= regdeathp:
            mw.print(f"{disptarget} is killed.", start=' ', bcast=True)
            target.hp = 0
            target.state = State.DEAD
            if isinstance(target, Member):
                target.rip += 1
            else:
                update = True
        else:
            mw.print(f"{disptarget} is alive.", start=' ', bcast=True)

    def attack(self, invoker, spell, target):
        """
        Attack spells to decrease HP
        """
        v = game.vscr
        mw = v.meswins[-1]
        spelldef = game.spelldef[spell]
        if not isinstance(invoker, Member):
            if spelldef.target == 'enemy':
                if spell == 'butsumetsu':
                    return
                targets = [mem for mem in game.party.members
                           if mem.state in [State.OK, State.ASLEEP]]
                mem = random.choice(targets)
                if spelldef.type == 'death':
                    self.death_single(mem, mem.name)
                else:
                    damage = dice(spelldef.value)
                    mw.print(
                        f"{mem.name} incurred {damage} damage.", start=' ', bcast=True)
                    v.disp_scrwin()
                    mem.hp = max(0, mem.hp - dice(spelldef.value))
                    if mem.hp <= 0 and \
                       mem.state not in [State.DEAD, State.ASHED, State.LOST]:
                        mem.state = State.DEAD
                        mem.rip += 1
                        mw.print(f"{mem.name} is killed.",
                                 start=' ', bcast=True)
            else:  # 'group' or 'all
                for mem in game.party.members:
                    if mem.state in [State.DEAD, State.ASHED, State.LOST]:
                        continue
                    if spelldef.type == 'death':
                        self.death_single(mem, mem.name)
                    else:
                        damage = dice(spelldef.value)
                        mw.print(
                            f"{mem.name} incurred {damage} damage.", start=' ', bcast=True)
                        mem.hp = max(0, mem.hp - dice(spelldef.value))
                        if mem.hp <= 0 and \
                           mem.state not in [State.DEAD, State.ASHED, State.LOST]:
                            mem.state = State.DEAD
                            mem.rip += 1
                            mw.print(f"{mem.name} is killed.",
                                     start=' ', bcast=True)
            return
        if spelldef.target == 'group':
            if target.identified:
                disptarget = target.name
            else:  # unidentified
                disptarget = game.mondef[target.name].unident
            if spell == 'shinoroi':  # lakanito
                for mon in target.monsters:
                    self.death_single(mon, disptarget)
                    game.battle.draw_ew()
            else:
                for mon in target.monsters:
                    self.attack_single(
                        mon, disptarget,
                        spelldef.value, spelldef.attr, target, invoker)
                    game.battle.draw_ew()
        elif spelldef.target == 'all':
            for mong in game.battle.monp:
                if mong.identified:
                    disptarget = mong.name
                else:
                    disptarget = game.mondef[mong.name].unident
                for mon in mong.monsters:
                    self.attack_single(mon, disptarget,
                                       spelldef.value, spelldef.attr, mong, invoker)
                    game.battle.draw_ew()
        elif spelldef.target == 'enemy':
            if target.identified:
                disptarget = target.name
            else:
                disptarget = game.mondef[target.name].unident
            if spelldef.type == 'death':
                self.death_single(target.top_valid(), disptarget)
                game.battle.draw_ew()
            elif spell != 'butsumetsu' or \
                    game.mondef[target.name].type != 'undead':
                self.attack_single(target.top_valid(), disptarget,
                                   spelldef.value, spelldef.attr, target, invoker)
                game.battle.draw_ew()

    def attack_single(self, mon, dispname, value, attr, mong, invoker):
        """
        Attack spells for a single enemy
        """
        if mon.state in [State.DEAD, State.RAN]:
            return
        v = game.vscr
        mw = v.meswins[-1]
        damage = dice(value)
        mondef = game.mondef[mon.name]
        if mondef.regspellp > random.randrange(100):
            mw.print(f"{dispname} registed.", bcast=True)
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
                mw.print(f"{dispname} was poisoned.", start=' ', bcast=True)
        mon.hp = max(mon.hp-damage, 0)
        mw.print(f"{dispname} incurred {damage} damage.",
                 start=' ', bcast=True)
        if mon.hp <= 0:
            mw.print(f"{dispname} is killed.", start=' ', bcast=True)
            mon.state = State.DEAD
            game.battle.exp += mondef.exp
            invoker.marks += 1
        game.battle.update_monp()

    def heal(self, invoker, spell, target):
        """
        Heal spells to recover HP
        """
        sdef = game.spelldef[spell]
        if not isinstance(invoker, Member):
            if sdef.target == 'party':
                for mon in game.battle.monp[0].monsters:
                    self.heal_single(spell, sdef, mon)
                    game.battle.update_monp()
            else:
                self.heal_single(spell, sdef, invoker)
                game.battle.update_monp()
            return
        if sdef.target == 'party':
            for target in game.party.members:
                self.heal_single(spell, sdef, target)
        else:
            self.heal_single(spell, sdef, target)

    def heal_single(self, sname, sdef, target):
        """
        Heal spells to recover HP for a signle fellow
        """
        plus = dice(sdef.value)
        target.hp = min(target.hp+plus, target.maxhp)
        mw = game.vscr.meswins[-1]
        if target.hp == target.maxhp:
            mw.print(f"{target.name}'s HP was fully restored.",
                     start=' ', bcast=True)
        else:
            mw.print(f"{plus} HP was restored to {target.name}.",
                     start=' ', bcast=True)


class Dungeon:
    """
    Represents the dungeon
    """

    def __init__(self):
        self.floors = []  # list of floor objects
        self.events = []  # list of events (floor, eventid)
        self.generate_events()
        self.uuid = None
        self.expedition = False  # logging in to an external server
        self.sio = None
        self.loaded = False  # load flag
        self.party_locs = {}  # {user: (x, y, floor, place.name)}
        self.parties = {}  # {user: party object}
        self.spells_casted = []  # (user, spell, caster, target)

    def get_gcamp_users(self):
        """
        Get group camp user list with the party
        Return [] if not in a group camp
        """
        if self.expedition and self.party_locs and \
           game.party.place == Place.CAMP:
            p = game.party
            ulist = [user for user, loc in self.party_locs.items()
                     if loc[3] == Place.CAMP.name and loc[0] == p.x
                     and loc[1] == p.y and loc[2] == p.floor and
                     user != config['server']['auth']['user']]
            return ulist
        else:
            return []

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
        party = game.party
        if not party.floor_move:
            return

        floor = party.floor
        if party.floor_move == 1:
            floor += 1
        elif party.floor_move == 3:
            floor = party.tsubasa_floor
        for idx in range(floor):
            if len(self.floors) < idx+1:
                if party.floor == idx + 1:
                    floor_obj = self.generate_floor(idx+1)
                else:
                    floor_obj = None
                self.floors.append(floor_obj)

        if party.floor_move == 1:  # down; on the upstairs
            party.floor += 1
            if self.floors[party.floor-1] == None:
                self.floors[party.floor-1] = self.generate_floor(party.floor)
            floor_obj = self.floors[party.floor-1]
            party.floor_obj = floor_obj
            party.move(floor_obj.rooms[0].center_x,
                       floor_obj.rooms[0].center_y,
                       floor=party.floor)
            if floor == 1:
                party.move(floor_obj.rooms[0].center_x,
                           floor_obj.rooms[0].center_y,
                           floor=party.floor)
        elif party.floor_move == 2:  # 2: up; on the downstairs
            party.floor -= 1
            if self.floors[party.floor-1] == None:
                self.floors[party.floor-1] = self.generate_floor(party.floor)
            floor_obj = self.floors[party.floor-1]
            party.floor_obj = floor_obj
            party.move(floor_obj.rooms[-1].center_x,
                       floor_obj.rooms[-1].center_y,
                       floor=party.floor)
        else:  # tsubasa; on the upstairs
            if self.floors[party.tsubasa_floor-1] == None:
                self.floors[party.tsubasa_floor -
                            1] = self.generate_floor(party.tsubasa_floor)
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
        Generate (or load from server) a dungeon floor.
        Create rooms, connect among them and place doors
        """
        if self.expedition:
            self.floor_obj = None
            sio.emit('load_floor', floor)
            while not self.floor_obj:
                pass
            return self.floor_obj

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
        floor_obj.place_doors(rooms)
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
                if game.dungeon.expedition:
                    game.dungeon.expedition = False
                    sio.emit('exit_dungeon')
                    sio.disconnect()
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

    def ending(self):
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

    def boss(self):
        """
        Events before fighting with boss mosters
        """
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
            self.ending()
        else:
            mw.print("You won the battle, but it was no ordinary monster.")
        mw.print("You see downstairs appearing in front of you.")
        v.disp_scrwin()
        getch(wait=True)
        v.meswins.pop()

    def key(self):
        """
        Events to find keys
        """
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
                if key == 'one time password':
                    game.chest.get_item(key)
                else:
                    game.chest.get_item(key+' key')
            v.meswins.pop()
            v.disp_scrwin()

    def random_message(self):
        """
        Random message events
        """
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

    def check_event(self):
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
            self.random_message()
            self.events[(x, y)][1] = True  # processed
            return True
        elif evid == Eventid.KEY:
            self.key()
        elif evid == Eventid.BOSS:
            self.boss()
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

    def open_door(self, mw):
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
            if game.party.can_open():
                mw.print("Unlocked.")
                self.put_tile(x, y, b'.')
            else:
                mw.print("No luck.")
        elif tile == b'%':
            if game.party.can_open(ch=b'%'):
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

    def place_doors(self, rooms):
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

    def __init__(self, name):
        self.name = name
        self.mdef = game.mondef[name]
        self.hp = self.maxhp = dice(self.mdef.hp)
        self.hpplus = 0
        self.ac = self.mdef.ac
        self.state = State.OK
        self.silenced = False
        self.poisoned = False

    def is_active(self):
        """
        Check if it can act in a battle
        """
        return self.state in [State.OK]

    def is_valid(self):
        """
        Check if it is valid in a battle
        """
        return self.state in [State.OK, State.ASLEEP, State.PARALYZED,
                              State.STONED]


class Monstergrp:
    """
    Represents a monster group
    """

    def __init__(self, name):
        self.name = name
        self.mdef = game.mondef[name]
        self.monsters = []
        self.identified = False

    def is_valid(self):
        """
        Check if there's at least one valid monster
        """
        return next((True for m in self.monsters if m.is_valid()), False)

    def num_valid(self):
        """
        Return number of valid mosters
        """
        return sum(1 for m in self.monsters if m.is_valid())

    def top_valid(self):
        """
        Rturn the 1st valid moster in the group
        """
        return next((m for m in self.monsters if m.is_valid()), False)

    def top_active(self):
        """
        Rturn the 1st valid moster in the group
        """
        return next((m for m in self.monsters if m.is_active()), False)


class Battle:
    """
    Represents battles
    """

    def __init__(self):
        self.boss = False
        self.ran = False  # ran from the battle flag
        v = game.vscr
        self.cw = Meswin(v, v.width//16, v.height//8+6,
                         v.width*7//16-1, 8, frame=True)
        self.mw = Meswin(v, v.width//2-3, v.height//8+6,
                         v.width*7//16+6, 8, frame=True)
        self.ew = Meswin(v, v.width//16, v.height//8-1,
                         v.width*14//16+4, 6, frame=True)

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
        game.party.alarm = False  # alarm flag
        if random.randrange(100) < 10:
            self.surprised = 1  # you surprised the monsters
        elif random.randrange(100) < 10:
            self.surprised = 2  # monsters surprised you
        else:
            self.surprised = 0
        self.ran = False  # ran flag
        for m in game.party.members:
            m.action = '????????????'
            m.drained = False
            m.acplus = 0
            m.silenced = False
        # Do not initialize here (init before check_event)
        # self.join_user = None  # joined battle for a server dungeon
        # monster party set flag (joined battle @ server dungeon)
        self.monp_set = False
        self.cw.cls()

    def draw_ew(self):
        """
        draw enemy window that lists the monster groups and number
        of monsters in them
        """
        self.ew.cls()
        i = 0
        for mg in self.monp:
            if not mg.is_valid():
                continue
            i += 1
            active = valid = 0
            if self.friendly or game.party.identify:
                mg.identified = True
            if mg.identified:
                dispname = mg.name
                if mg.num_valid() > 1:
                    dispname = mg.mdef.names
            else:
                dispname = mg.mdef.unident
                if mg.num_valid() > 1:
                    dispname = mg.mdef.unidents
            for m in mg.monsters:
                if m.is_active():
                    active += 1
                if m.is_valid():
                    valid += 1
            self.ew.print(
                f"{i}) {valid} {dispname.ljust(24)} ({active})", start=' ')

    def create_monsterparty(self):
        """
        Create a monster party and save it to self.monp
        """
        if game.dungeon.expedition and game.battle.join_user:
            self.monp_set = False
            sio.emit('get_monp', self.join_user)
            while not self.monp_set:
                pass
            game.chest.items = list(self.monp[0].mdef.treasure)
            for mong in self.monp:
                mdef = game.mondef[mong.name]
                self.gold = sum((mdef.level*(random.randrange(15)+10))
                                for _ in mong.monsters)
            return
        if self.boss:
            bosses = {
                3: 'daemon kid',
                6: 'the lady',
                9: 'atlas',
                10: 'daemon lord',
            }
            mname = bosses[game.party.floor]
        else:
            candidates = []
            for mname in game.mondef:
                if game.party.floor <= 10:
                    if game.party.floor in game.mondef[mname].floors:
                        candidates.append(mname)
                else:
                    if 0 in game.mondef[mname].floors:
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
        maxgrps = 4  # up to 4 groups
        if game.dungeon.expedition:
            maxgrps = 6  # up to 6 groups in a server dungeon
        while len(self.monp) < maxgrps:
            mdef = game.mondef[mname]
            if len(self.monp) == 0:  # 1st group
                if mdef.friendly and random.randrange(100) < 10:  # 1/10
                    self.friendly = True

            mong = Monstergrp(mname)
            self.monp.append(mong)
            for _ in range(dice(mdef.number)):
                mon = Monster(mname)
                mong.monsters.append(mon)
                self.gold += mdef.level * (random.randrange(15) + 10)
            fellowp = mdef.fellowp
            if game.dungeon.expedition and fellowp != 0:
                fellowp += 20  # +20% more likely in a server dungeon
            if fellowp <= random.randrange(100):
                break
            mname = mdef.fellow
        # top monster defines treasure levels
        game.chest.items = list(self.monp[0].mdef.treasure)
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
                    el += game.mondef[m.name].level
        for mem in game.party.members:
            if mem.state == State.OK:
                pl += mem.level
        if pl > el:
            success += 20

        if len(game.party.members) == 1:
            success += 15
        elif len(game.party.members) == 2:
            success += 10
        elif len(game.party.members) == 3:
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
        v = game.vscr
        if len(self.monp) > 1:
            dispname = 'monsters'
        else:
            mong = self.monp[0]
            if mong.identified:
                dispname = mong.name
                if mong.num_valid() > 1:
                    dispname = mong.mdef.names
            else:
                dispname = mong.mdef.unident
                if mong.num_valid() > 1:
                    dispname = mong.mdef.unidents
        if self.friendly:
            self.surprised = 0
            self.mw.print(f"You encountered friendly {dispname}.")
            c = self.mw.input_char("Leave? (y/n)", values=['y', 'n'])
            if c == 'y':
                idx = self.room_index
                if idx >= 0:  # room encounter
                    game.party.floor_obj.battled[idx] = True
                return True
        else:
            self.mw.print(f"You encountered {dispname}.")
            game.vscr.disp_scrwin()
        return False

    def enemy_action(self):
        """
        Decide enemy/monster actions
        """
        if self.surprised == 1:  # you surprised the monsters
            return
        mondef = game.mondef
        party = game.party
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
                    if action in game.spelldef:
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
        for mem in game.party.members:
            mem.action = '????????????'
        if self.surprised == 2:  # monsters surprised you
            return False
        while True:
            self.cw.print(f"Options - f)ight s)pell u)se")
            self.cw.print(f"d)ispell p)arry r)un t)ake back", start=' ')
            for idx, mem in enumerate(game.party.members, 1):
                if mem.state not in [State.OK]:
                    continue
                while True:
                    c = self.cw.input_char(f"{mem.name}'s action?")
                    monglst = [mong for mong in self.monp if mong.is_valid()]
                    if not monglst:
                        return False
                    agi = mem.stat_agility + random.randrange(5)
                    if c == 'r':
                        if self.canrun(mem):
                            return True
                        else:
                            return False  # failed
                    elif c == 't':
                        self.entities = []
                        for mem in game.party.members:
                            mem.action = '????????????'
                        self.cw.print("..taking back")
                        game.vscr.disp_scrwin()
                        break
                    elif c == 'p':
                        mem.action = 'parry'
                        self.entities.append(
                            Entity(mem, mem.name, None, agi, 'parry', None))
                        game.vscr.disp_scrwin()
                        break
                    elif c == 'f':
                        wrange = 'short'
                        for item in mem.items:
                            idef = game.itemdef[item.name]
                            if item.equipped and idef.type.lower() == 'weapon' \
                               and idef.range.lower() == 'long':
                                wrange = 'long'
                        if idx > 3 and wrange == 'short':
                            self.cw.print("Weapon range too short.")
                            game.vscr.disp_scrwin()
                            continue
                        mong = self.choose_group()
                        if not mong:
                            return
                        self.entities.append(
                            Entity(mem, mem.name, None, agi, 'fight', mong))
                        mem.action = 'fight'
                        game.vscr.disp_scrwin()
                        break
                    elif c == 'd':
                        if mem.job not in [Job.PRIEST, Job.BISHOP, Job.LORD]:
                            continue
                        mong = self.choose_group()
                        if not mong:
                            return
                        self.entities.append(
                            Entity(mem, mem.name, None, agi, 'dispell', mong))
                        mem.action = 'dispell'
                        game.vscr.disp_scrwin()
                        break
                    elif c == 's':
                        if self.surprised == 1:  # you surprised the monsters
                            continue
                        s, target = self.choose_spell(mem)
                        self.entities.append(
                            Entity(mem, mem.name, None, agi, s, target))
                        mem.action = s
                        game.vscr.disp_scrwin()
                        break
                    elif c == 'u':
                        item, target = self.choose_item(mem)
                        if not item:
                            continue
                        self.entities.append(
                            Entity(mem, mem.name, None, agi, item, target))
                        mem.action = item
                        game.vscr.disp_scrwin()
                        break
                    elif c == 'm' and game.dungeon.expedition:
                        send_message()
                if c == 't':
                    break
            if c != 't':
                self.cw.print("Press any key or t)ake back >")
                game.vscr.disp_scrwin()
                c = getch(wait=True)
                if c == 't':
                    self.entities = []
                    for mem in game.party.members:
                        mem.action = '????????????'
                    continue
                break

    def choose_group(self):
        """
        choose monster group and return monster group object
        """
        if sum(1 for mong in self.monp if mong.is_valid()) == 1:
            return next((mong for mong in self.monp if mong.is_valid()), self.monp[0])
        while True:
            msg = f"Which group? (#)"
            self.cw.print(msg)
            game.vscr.disp_scrwin()
            print(f"\033[{self.cw.y+self.cw.cur_y+1};{self.cw.x+len(msg)+6}H",
                  end='', flush=True)
            n = getch(wait=True)
            l = self.cw.mes_lines.pop()
            self.cw.print(''.join([l, ' ', n])[2:], start=' ')
            game.vscr.disp_scrwin()
            try:
                n = int(n)
            except:
                continue
            if n < 1 or n > 4:
                continue
            monglst = [mong for mong in self.monp if mong.is_valid()]
            if not monglst:
                return None
            try:
                mong = monglst[n-1]
            except:
                continue
            return mong

    def choose_spell(self, mem):
        """
        Choose spell to cast and the target monster group or the party member
        """
        mw = self.cw
        s = mw.input("What spell to cast?")
        s = s.lower()
        if s not in game.spelldef:  # No such spell
            return s, None
        elif s not in list(itertools.chain(mem.mspells, mem.pspells)):
            return s, None  # not mastered yet
        sdef = game.spelldef[s]
        if sdef.target == 'enemy' or sdef.target == 'group':
            target = self.choose_group()
            if not target:
                return None, None
        elif sdef.target == 'member':
            while True:
                ch = mw.input_char(f"To who? (#)")
                try:
                    if 0 <= (chid := int(ch)-1) < len(game.party.members):
                        break
                except:
                    pass
            target = game.party.members[chid]
        else:
            target = None
        return s, target

    def choose_item(self, mem):
        """
        Choose item to use.  If the item has spell power and the
        spell needs target to choose, have player specify target.
        """
        mw = self.cw
        mw.print("Which item to use?")
        for i, item in enumerate(mem.items, 1):
            if item.unidentified:
                dispitem = ''.join(['?', game.itemdef[item.name].unident])
            else:
                dispitem = item.name
            mw.print(f"{i}) {dispitem}")
        idx = mw.input_char("Item # or l)eave",
                            values=['1', '2', '3', '4', '5', '6', '7', '8', 'l'])
        if idx == 'l':
            return False, None
        idef = mem.items[int(idx)-1]
        if idef[3]:
            iname = ''.join(['?', game.itemdef[idef.name].unident])
        else:
            iname = idef.name
        spell = game.itemdef[idef.name].use
        if spell != '' and spell in game.spelldef and \
           iname == idef.name:
            target = game.spelldef[spell].target
            if target == 'member':
                m = game.party.choose_character()
                if not m:
                    return False, None
                return iname, m
            elif target in ['group', 'enemy']:
                mong = self.choose_group()
                if not mong:
                    return None, None
                return iname, mong
        return iname, None

    def monster_attack(self, e):
        """
        Monster attacks a member
        """
        mdef = game.mondef[e.name]
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
            self.mw.print(f"{e.name} lost its target.", bcast=True)
            return

        apoint = 19
        if e.target.action == 'parry':
            apoint += 2
        apoint -= game.mondef[e.name].level + 2
        bpoint = apoint - e.target.ac - e.target.acplus - game.party.ac

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
        for _ in range(game.mondef[e.name].count):
            if hitp > random.randrange(100):
                hitcnt += 1
                damage += dice(game.mondef[e.name].attack)
        e.target.hp -= damage
        if e.target.state != State.OK:
            e.target.hp -= damage  # twice the damage if not status OK
        self.mw.print(f"{dispname} {verb} at {e.target.name}.", bcast=True)
        self.mw.print(
            f"{e.target.name} incurred {damage} damage.", start=' ', bcast=True)
        game.vscr.disp_scrwin()
        if e.target.hp <= 0:
            e.target.hp = 0
            e.target.state = State.DEAD
            e.target.rip += 1
            self.mw.print(f"{e.target.name} is killed.", start=' ', bcast=True)
            return
        if hitcnt == 0:
            return

        regist = set()
        for item in e.target.items:
            if item.equipped:  # equipped
                regist |= set(game.itemdef[item.name].regist)

        if game.mondef[e.name].poison:
            if (e.target.stat_luck+1)*100//20 < random.randrange(100):
                if 'poison' not in regist and not e.target.poisoned:
                    e.target.poisoned = True
                    e.target.hpplus -= 1
                    self.mw.print(f"{e.target.name} is poisoned.", bcast=True)

        if game.mondef[e.name].paraly:
            if (e.target.stat_luck+1)*100//20 < random.randrange(100):
                if 'paraly' not in regist:
                    e.target.state = State.PARALYZED
                    self.mw.print(f"{e.target.name} is paralyzed.", bcast=True)

        if game.mondef[e.name].stone:
            if (e.target.stat_luck+1)*100//20 < random.randrange(100):
                if 'stone' not in regist:
                    e.target.state = State.STONED
                    self.mw.print(f"{e.target.name} is petrified.", bcast=True)

        if not e.target.drained and game.mondef[e.name].drain > 0:
            if (e.target.stat_luck+1)*100//20 < random.randrange(100):
                if 'drain' not in regist:
                    prevlevel = e.target.level
                    e.target.level -= game.mondef[e.name].drain
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
                        f"{e.target.name} is drained by {game.mondef[e.name].drain} level.", bcast=True)
                    if e.target.level < 1:
                        e.target.hp = 0
                        e.target.state = State.LOST
                        self.mw.print(f"{e.target.name} is lost.", bcast=True)
                        return
                    e.target.maxhp = \
                        e.target.maxhp * \
                        (prevlevel - game.mondef[e.name].drain) \
                        // prevlevel
                    if e.target.hp > e.target.maxhp:
                        e.target.hp = e.target.maxhp
                    e.target.drained = True

        if game.mondef[e.name].critical:
            if (e.target.stat_lucl+1)*100//20 < random.randrange(100):
                if 'critical' not in regist:
                    if (49 - game.mondef[e.name].level) * 100 / 50 \
                       < random.randrange(100):
                        e.target.state = State.DEAD
                        e.target.hp = 0
                        e.target.rip += 1
                        self.mw.print(
                            f"{e.target.name} is decapitated.", bcast=True)

    def dispell(self, e):
        """
        Party member dispells a monster group
        """
        mondef = game.mondef[e.target.name]
        if e.target.identified:
            dispname = e.target.name
        else:
            dispname = mondef.unident
        self.mw.print(f"{e.name} tried to dispell.", bcast=True)
        if mondef.type != 'undead':
            self.mw.print("Not undead.", start=' ', bcast=True)
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
                self.mw.print(f"{dispname} is dispelled.",
                              start=' ', bcast=True)
            else:
                self.mw.print(f"{dispname} registed to dispell.",
                              start=' ', bcast=True)

    def member_attack(self, e):
        """
        Party member attacks a monster
        """
        update = False  # update flag in a server dungeon
        if e.entity.job in [Job.MAGE, Job.THIEF, Job.BISHOP]:
            lvbonus = e.entity.level // 5
        else:
            lvbonus = e.entity.level // 3 + 2
        strbonus = 0
        if e.entity.stat_strength >= 16:
            strbonus = e.entity.stat_strength - 15
        elif e.entity.stat_strength < 6:
            strbonus = e.entity.stat_strength - 6
        st_bonus = weapat = 0
        weapon = None
        for item in e.entity.items:
            if item.equipped:  # equpped?
                # (check align)
                itemdef = game.itemdef[item.name]
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
        hitpercent = (game.mondef[e.target.name].ac
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
                    if game.mondef[e.target.name].type in weapon.twice:
                        damage += dice(weapon.dice) * 2
                    else:
                        damage += dice(weapon.dice)
                hitcnt += 1
        if e.target.identified:
            dispname = e.target.name
        else:
            dispname = game.mondef[e.target.name].unident
        if e.target.top_valid().state != State.OK:
            damage *= 2
        verb = random.choice(['swings', 'thrusts', 'stabs', 'slashes'])
        self.mw.print(
            f"{e.name} {verb} violently at {dispname} and hits {hitcnt} times for {damage} damage.", bcast=True)
        e.target.top_valid().hp -= damage
        if damage:
            update = True

        if e.entity.job == Job.NINJA:
            crit = (e.entity.level -
                    game.mondef[e.target.name].level) + 20
            if crit > 80:
                crit = 80
            elif crit < 5:
                crit = 5
            if crit > random.randrange(100):
                e.target.monsters[0].hp = 0
                e.target.monsters[0].state = State.DEAD
                self.mw.print(f"{dispname} is decapitated!", bcast=True)
                update = True

        if e.target.top_valid().hp <= 0:
            e.target.top_valid().state = State.DEAD
            self.mw.print(f"{dispname} is killed.", start=' ', bcast=True)
            self.exp += game.mondef[e.target.name].exp
            e.entity.marks += 1
            self.draw_ew()
            update = True

        if update:
            self.update_monp()

    def reorder_party(self):
        """
        Members with bad status move back.
        """
        valid = []
        invalid = []
        for mem in game.party.members:
            if mem.state in [State.OK]:
                valid.append(mem)
            else:
                invalid.append(mem)
        game.party.members = valid + invalid

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
        place = game.party.place
        game.party.place = Place.BATTLE
        v = game.vscr
        v.meswins.append(self.ew)
        v.meswins.append(self.cw)
        v.meswins.append(self.mw)
        self.mw.cls()

        self.create_monsterparty()
        self.draw_ew()

        if self.handle_friendly(place):
            party = game.party
            self.treasure = False
            for idx, room in enumerate(party.floor_obj.rooms):
                if room.in_room(party.x, party.y):
                    party.floor_obj.battled[idx] = True
                    break
            v.meswins.pop()
            v.meswins.pop()
            v.meswins.pop()
            game.party.place = place
            return

        if self.surprised == 1:
            self.mw.print("You surprised the monsters.\n - press space bar")
            game.vscr.disp_scrwin()
            while getch(wait=True) != ' ':
                pass
        elif self.surprised == 2:
            self.mw.print("Monsters surprised you.\n - press space bar")
            game.vscr.disp_scrwin()
            while getch(wait=True) != ' ':
                pass

        game.party.push_loc()

        while True:
            for m in game.party.members:
                m.action = '????????????'
            self.recover_state()
            self.reorder_party()
            self.identify_check()
            self.draw_ew()
            v.disp_scrwin()
            if self.input_action():
                self.ran = True
                v.meswins[0].print("Ran away from the battle.", bcast=True)
                v.disp_scrwin()
                game.party.x, game.party.px =\
                    game.party.px, game.party.x
                game.party.y, game.party.py =\
                    game.party.py, game.party.y
                game.party.floor, game.party.pfloor =\
                    game.party.pfloor, game.party.floor
                game.party.floor_obj =\
                    game.dungeon.floors[game.party.floor-1]
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
                    if not next((True for mong in self.monp if mong.is_valid()), False):
                        break
                    if not e.target.is_valid():  # already the gorup is gone
                        e.target = next((mong for mong in self.monp
                                         if mong.is_valid()), self.monp[0])
                if isinstance(e.entity, Monster):
                    if not e.group.identified:
                        dispname = game.mondef[e.name].unident
                if e.entity.state is State.ASLEEP:
                    self.mw.print(f"{dispname} is asleep.", bcast=True)
                    continue
                if e.entity.state not in [State.OK]:
                    continue
                if not next((True for mong in self.monp if mong.is_valid()), False):
                    break

                if e.action == 'parry':
                    self.mw.print(f"{dispname} parried.", bcast=True)
                elif e.action == 'breath':  # monster only
                    self.mw.print(
                        f"{dispname} breathed on the party.", bcast=True)
                    for mem in game.party.members:
                        if mem.state in [State.DEAD, State.ASHED, State.LOST]:
                            continue
                        damage = e.entity.hp // 2
                        mem.hp = max(0, mem.hp - damage)
                        self.mw.print(f"{mem.name} incurred {damage} damage.",
                                      start=' ', bcast=True)
                        if mem.hp <= 0 and mem.state not in \
                           [State.DEAD, State.ASHED, State.LOST]:
                            mem.state = State.DEAD
                            mem.rip += 1
                            self.mw.print(f"{mem.name} is killed.",
                                          start=' ', bcast=True)
                elif e.action == 'fight':
                    if isinstance(e.entity, Member):
                        self.member_attack(e)
                    else:
                        self.monster_attack(e)
                elif e.action == 'dispell':
                    self.dispell(e)
                elif e.action == 'run':  # monster only
                    if self.canrun(e.entity):
                        e.group.top_active().state = State.RAN
                        self.mw.print(f"{dispname} ran away.", bcast=True)
                        self.draw_ew()
                    else:
                        self.mw.print(
                            f"{dispname} tried to run away", bcast=True)
                        self.mw.print(f".. but wasn't able to.",
                                      start=' ', bcast=True)
                elif e.action == 'help':  # monster only
                    self.mw.print(f"{dispname} called for help.")
                    if e.group.num_valid() < 9 and \
                       random.randrange(100) < 40:  # 40%
                        self.mw.print(
                            f".. and a fellow monster appeared.", start=' ', bcast=True)
                        mon = Monster(game, e.name)
                        e.group.monsters.append(mon)
                        self.gold += game.mondef[e.name].level * \
                            (random.randrange(15) + 10)
                    else:
                        self.mw.print(
                            f".. but no help came.", start=' ', bcast=True)
                elif '?' in e.action:  # tried to use unidentified item
                    self.mw.print(f"{dispname} tried to use {e.action}.")
                    self.mw.print(
                        f".. but doesn't know how to use it.", start=' ', bcast=True)
                elif e.action in game.itemdef:  # item
                    item = game.itemdef[e.action]
                    if item.use and (spell := game.spelldef[item.use].battle):
                        self.mw.print(
                            f"{dispname} used {e.action}.", bcast=True)
                        self.mw.print(
                            f".. and invoked {spell}.", start=' ', bcast=True)
                        v.disp_scrwin()
                        getch(wait=True)
                        game.spell.cast_spell_dispatch(
                            e.entity, spell, e.target)
                    else:
                        self.mw.print(
                            f"{dispname} tried to use {e.action}.", bcast=True)
                        self.mw.print(f".. but wasn't able to.",
                                      start=' ', bcast=True)
                elif e.action in game.spelldef:  # spell
                    spelldef = game.spelldef[e.action]
                    if isinstance(e.entity, Member):
                        if (not spelldef.battle) or \
                           e.action not in list(itertools.chain(
                               e.entity.mspells, e.entity.pspells)):
                            self.mw.print(
                                f"{dispname} tried to cast {e.action}", bcast=True)
                            self.mw.print(
                                f".. but nothing happend.", start=' ', bcast=True)
                            v.disp_scrwin()
                            getch(wait=True)
                            continue
                        else:
                            if e.action in e.entity.mspells:
                                if e.entity.mspell_cnt[spelldef.level-1] > 0:
                                    e.entity.mspell_cnt[spelldef.level-1] -= 1
                                else:
                                    self.mw.print(
                                        f"{dispname} tried to cast {e.action}", bcast=True)
                                    self.mw.print(
                                        f".. but MP is exhausted.", start=' ', bcast=True)
                                    v.disp_scrwin()
                                    getch(wait=True)
                                    continue
                            else:
                                if e.entity.pspell_cnt[spelldef.level-1] > 0:
                                    e.entity.pspell_cnt[spelldef.level-1] -= 1
                                else:
                                    self.mw.print(
                                        f"{dispname} tried to cast {e.action}", bcast=True)
                                    self.mw.print(
                                        f".. but MP is exhausted.", start=' ', bcast=True)
                                    v.disp_scrwin()
                                    getch(wait=True)
                                    continue
                    if e.entity.silenced:
                        self.mw.print(
                            f"{dispname} tried to cast {e.action} but silenced.", bcast=True)
                    else:
                        self.mw.print(
                            f"{dispname} casted {e.action}.", bcast=True)
                        game.spell.cast_spell_dispatch(
                            e.entity, e.action, e.target)
                # self.clean_dead()  # clean up dead monsters
                v.disp_scrwin()
                if not next((True for mong in self.monp if mong.is_valid()), False):
                    break
                getch(wait=True)

            # Battle end?
            party = game.party
            if not next((True for mong in self.monp if mong.is_valid()), False):
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
                self.mw.print(
                    "The party lost the battle and defeated.", bcast=True)
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
        v.meswins.pop()
        game.party.place = place
        game.party.push_loc()
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
        v = game.vscr
        mw = v.meswins[-1]
        for mem in game.party.members:
            if mem.state == State.ASLEEP and random.randrange(100) < 50:
                mem.state = State.OK
            if mem.state in [State.DEAD, State.ASHED, State.LOST]:
                continue
            mem.hp = min(max(0, mem.hp+mem.hpplus), mem.maxhp)
        for mong in self.monp:
            for mon in mong.monsters:
                mon.hp = min(max(0, mon.hp+mon.hpplus), mon.maxhp)
                if mon.state == State.ASLEEP:
                    if game.mondef[mon.name].weaksleep:
                        chance = 15
                    else:
                        chance = 40
                    if random.randrange(100) < chance:
                        mon.state = State.OK

    def check_battle(self):
        """
        Check if they'll have a battle
        Return 0 if False, 1 if random encounter, 2 if room battle.
        self.join_user is set if joined battle in a server dungeon
        """
        party = game.party
        if game.dungeon.expedition:
            user = next((k for k, v in game.dungeon.party_locs.items()
                         if v[0] == party.x and v[1] == party.y and v[2] == party.floor
                         and v[3] == Place.BATTLE.name), None)
            if user:
                self.join_user = user
        rooms = party.floor_obj.rooms
        for idx, room in enumerate(rooms):
            if idx == 0:
                continue
            if room.in_room(party.x, party.y) \
               and not party.floor_obj.battled[idx]:
                if random.randrange(100) < min(95, party.floor*10) or \
                   self.join_user:
                    self.room_index = idx
                    return 2  # with room guardian
                else:
                    party.floor_obj.battled[idx] = True
        if random.randrange(64) == 0 or self.join_user:
            self.room_index = -1  # random encounter
            return 1  # random encounter
        return 0

    def monp_todic(self):
        """
        Create a serializable copy of monp
        """
        monp_s = []
        for mong in self.monp:
            mong_s = {'name': mong.name, 'monsters': [],
                      'identified': mong.identified}
            for mon in mong.monsters:
                mon_s = {'name': mon.name, 'maxhp': mon.maxhp, 'hp': mon.hp,
                         'hpplus': mon.hpplus, 'ac': mon.ac, 'state': mon.state.name,
                         'silenced': mon.silenced, 'poisoned': mon.poisoned}
                mong_s['monsters'].append(mon_s)
            monp_s.append(mong_s)
        return monp_s

    def monp_fromdic(self, monp_s):
        """
        Deserialize monp_s and return a monp copy
        """
        monp = []
        for mong_s in monp_s:
            mong = Monstergrp(game, mong_s['name'])
            mong.monsters = []
            mong.identified = mong_s['identified']
            for mon_s in mong_s:
                mon = Monster(game, mon_s['name'])
                mon.hp = mon_s['hp']
                mon.hpplus = mon_s['hpplus']
                mon.ac = mon_s['ac']
                mon.state = State[mon_s['state']]
                mon.silenced = mon_s['silenced']
                mon.poisoned = mon_s['poisoned']
                mong.monsters.append(mon)
            monp.append(mong)
        return monp

    def update_monp(self):
        """
        Update monp to server.  The server decides which clents to update
        """
        if self.joined_battle():
            sio.emit('update_monp', self.monp_todic())

    def joined_battle(self):
        """
        Check if the party is in a joined battle (server dungeon only)
        """
        if not game.dungeon.expedition:
            return False
        p = game.party
        for x, y, floor, place in game.dungeon.party_locs.values():
            if x == p.x and y == p.y and floor == p.floor and Place[place] == p.place:
                return True
        return False


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

    def __init__(self):
        self.mw = Meswin(game.vscr, 14, 3, 44, 10, frame=True)
        self.trap = Trap.TRAPLESS_CHEST
        self.items = None

    def chest(self):
        """
        Chest main.  Determine the trap, inspect, disarm, activate
        the trap, find items, etc.
        """
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
                mem = game.party.choose_character()
                if not mem:
                    continue
                self.trap_activated(mem)
                self.treasure()
                v.meswins.pop()
                return
            elif c == 'd':  # disarm
                mem = game.party.choose_character()
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
                if random.randrange(20) < mem.stat_agility:  # agility
                    mw.print("Failed to disarm.", start=' ')
                    v.disp_scrwin()
                    continue
                self.trap_activated(mem)
                self.treasure()
                v.meswins.pop()
                return
            elif c == 'k':  # calfo
                mem = game.party.choose_character()
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
                mem = game.party.choose_character()
                if not mem:
                    continue
                if mem.inspected:
                    mw.print("Already inspected.", start=' ')
                    continue
                if mem.job == Job.THIEF:
                    chance = mem.stat_agility * 6  # agility
                elif mem.job == Job.NINJA:
                    chance = mem.stat_agility * 4
                else:
                    chance = mem.stat_agility
                chance = min(chance, 95)
                if random.randrange(100) >= chance:  # failed?
                    if random.randrange(20) > mem.stat_agility:
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
        mw = game.vscr.meswins[-1]
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
            game.vscr.disp_scrwin()
            getch(wait=True)

    def choose_item(self, item_lvl):
        """
        Randomly pick one item of the specified item level.
        """
        items = []
        for item in game.itemdef:
            if game.itemdef[item].level == item_lvl:
                items.append(item)
        item = random.choice(items)
        return item

    def get_item(self, item):
        """
        Someone in the party get the item found.
        """
        v = game.vscr
        mw = v.meswins[-1]
        if sum(len(mem.items) for mem in game.party.members) == \
           8 * len(game.party.members):
            mw.print("Item full.")
            v.disp_scrwin()
            getch(wait=True)
            return
        mem = random.choice(
            [mem for mem in game.party.members if len(mem.items) < 8])
        mem.items.append([item, False, False, True, False])  # unidentified
        mw.print(
            f"{mem.name} found {game.itemdef[item].unident}", start=' ')
        v.disp_scrwin()
        getch(wait=True)

    def trap_activated(self, mem):
        """
        Trap is activated and do harm to party member(s).
        """
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
                    if random.randrange(20) >= m.stat_luck:
                        if m.state in [State.OK]:
                            m.state = State.PARALYZED
                            mw.print(f"{m.name} is paralyzed.", start=' ')
                    else:
                        if m.state in [State.OK, State.PARALYZED]:
                            m.state = State.STONED
                            mw.print(f"{m.name} is petrified.", start=' ')
                elif m.job == Job.SAMURAI:
                    if random.randrange(20) >= m.stat_luck:
                        if m.state in [State.OK]:
                            m.state = State.PARALYZED
                            mw.print(f"{m.name} is paralyzed.", start=' ')
            v.disp_scrwin()
        elif self.trap == Trap.PRIEST_BLASTER:
            for m in game.party.members:
                if m.job == Job.PRIEST:
                    if random.randrange(20) >= m.stat_luck:
                        if m.state in [State.OK]:
                            m.state = State.PARALYZED
                            mw.print(f"{m.name} is paralyzed.", start=' ')
                    else:
                        if m.state in [State.OK, State.PARALYZED]:
                            m.state = State.STONED
                            mw.print(f"{m.name} is petrified.", start=' ')
                elif m.job == Job.LORD:
                    if random.randrange(20) >= m.stat_luck:
                        if m.state in [State.OK]:
                            m.state = State.PARALYZED
                            mw.print(f"{m.name} is paralyzed.", start=' ')
        v.disp_scrwin()
        getch(wait=True)

    def choose_trap(self):
        """
        Decide which trap the chest has.
        """
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
    if os_windows:
        w = 80
        h = 25
    else:
        h, w, hp, wp = struct.unpack(
            'HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ,
                                struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h


def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def getch_sub():
    if game.vscr.refresh:
        game.vscr.refresh = False
        game.vscr.disp_scrwin()
    if game.dungeon.expedition:
        if game.vscr.messages:  # one message at a time
            user, mes = game.vscr.messages.pop(0)
            game.vscr.meswins[0].print(f"Message from {user}:")
            game.vscr.meswins[0].print(mes, start=' ')
            game.vscr.disp_scrwin()
        if game.vscr.battle_messages:
            mes, st = game.vscr.battle_messages.pop(0)
            if st == '*':
                st = '-'
            game.vscr.meswins[-1].print(mes, start=st)
            game.vscr.disp_scrwin()
        if game.party.place == Place.CAMP and \
           game.dungeon.spells_casted and \
           game.dungeon.parties:
            user, spell, caster, target = \
                game.dungeon.spells_casted.pop(0)
            p = game.dungeon.parties[user]
            cas = next(mem for mem in p.members
                       if mem.name == caster)
            mw = game.vscr.meswins[-1]
            if target in ['party', 'all', '']:
                tgt = target
                mw.print(f"{caster}({user}) casted {spell}.",
                         start='-')
            else:
                tgt = next(mem for mem in game.party.members
                           if mem.name == target)
                mw.print(
                    f"{caster}({user}) casted {spell} for {target}.",
                    start='-')
                game.spell.cast_spell_dispatch(cas, spell, tgt)
                game.vscr.disp_scrwin()


def getch(wait=True):
    """
    realtime key scan
    wait - if it waits (blocks) for user input
    """
    if os_windows:
        while True:
            if msvcrt.kbhit() or wait:  # msvcrt.kbhit() is non-blocking
                c = msvcrt.getch()  # msvcrt.getch() is blocking
                c = c.decode("utf-8")
                if c == 'Q':
                    if game.dungeon.expedition:
                        sio.disconnect()
                    sys.exit()
                return c
            getch_sub()
            time.sleep(0.05)

    c = ''
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())

        c = ''
        while True:
            if isData():
                c = sys.stdin.read(1)
            if c != '' or not wait:
                break
            getch_sub()
            time.sleep(0.05)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    if c == 'Q':
        if game.dungeon.expedition:
            sio.disconnect()
        sys.exit()
    return c


def loaddef_all():
    """
    Load spell, item and monster definitions
    """
    with open("dldef.yaml", 'r') as stream:
        try:
            dldef = yaml.load(stream, Loader=yaml.Loader)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit()
    game.spelldef = {}
    game.itemdef = {}
    game.mondef = {}
    for k, v in dldef['spell'].items():
        game.spelldef[k] = Spelldef(**v)
    for k, v in dldef['item'].items():
        game.itemdef[k] = Itemdef(**v)
    game.shopitems = {}
    for name in game.itemdef:
        game.shopitems[name] = game.itemdef[name].shop
    for k, v in dldef['monster'].items():
        game.mondef[k] = Monsterdef(**v)


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


def choose_party_character():
    """
    Return user of the party and character number.
    Used in group camp.
    """
    mw = game.vscr.meswins[-1]
    ulist = [config['server']['auth']['user']]
    ulist.extend(list(game.dungeon.parties.keys()))
    uidx = 0
    while True:
        game.vscr.show_puser = puser = ulist[uidx]
        ch = mw.input_char(f"Who? - # or p)switch parties l)eave")
        if ch == 'l':
            break
        elif ch == 'p':
            if (uidx := uidx+1) >= len(ulist):
                uidx = 0
        try:
            if 0 <= (chid := int(ch)-1) < \
               len(game.dungeon.parties[puser].members):
                break
        except:
            pass
    game.vscr.show_puser = config['server']['auth']['user']
    if ch == 'l':
        return None, None
    return puser, chid


def create_character():
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
    ch.distribute_bonus()


def inspect_characters():
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
                rtn = chlist[cnum].inspect_character()
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


def training():
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
            create_character()
        elif c == 'i':
            inspect_characters()


def tavern_add():
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


def tavern():
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
                tavern_add()
            else:
                mw.print("No characters to add")
        elif ch == 'i':
            if not game.party.members:
                continue
            idx = 0
            while True:
                mem = game.party.members[idx]
                rtn = mem.inspect_character()
                if rtn == 0:
                    break
                idx += rtn
                if idx < 0:
                    idx = len(game.party.members) - 1
                elif idx >= len(game.party.members):
                    idx = 0
        elif ch == 'r':
            game.party.remove_character()
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
                        bought = Memitem(items[idx])
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
                bought = Memitem(items[idx])
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
        dispname = item.name
        mark = ' '
        if op == 'u':  # uncurse
            if not item.cursed:
                continue
            mark = '&'
            if item.unidentified:
                dispname = ''.join(['?', game.itemdef[item.name].unident])
        elif op == 'i':  # identify
            if (not item.unidentified) or item.cursed:
                continue
            dispname = ''.join(['?', game.itemdef[item.name].unident])
        else:  # sell
            if item.equipped or item.cursed or item.unidentified:
                continue
        price = game.itemdef[item.name].price//div
        if op == 'i':
            price = min(1000, max(price, 20))
        mw.print(
            f"{i}){mark}{dispname.ljust(24)} {price}",
            start=' ')
        idic[i] = (item.name, dispname, price)

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
        mem.items[int(c)-1].unidentified = False  # identified
        mw.print(f"Identified as {mem.items[int(c)-1].name}.")
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
        mw.print(f"Uncursed {mem.items[int(c)-1].name}.")
        del mem.items[int(c)-1]

    game.vscr.disp_scrwin()
    getch()


def trader():
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
        mem = game.party.choose_character()
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

        if random.randrange(100) < 45:
            m.stat_strength += 1
        elif random.randrange(100) < 25:  # (100-45) * 25% = 13.75%
            m.stat_strength -= 1
        m.stat_strength = max(m.stat_strength, race_status[m.race][0])
        m.stat_strength = min(m.stat_strength, race_status[m.race][0]+10)
        if random.randrange(100) < 45:
            m.stat_iq += 1
        elif random.randrange(100) < 25:  # (100-45) * 25% = 13.75%
            m.stat_iq -= 1
        m.stat_iq = max(m.stat_iq, race_status[m.race][1])
        m.stat_iq = min(m.stat_iq, race_status[m.race][1]+10)
        if random.randrange(100) < 45:
            m.stat_piety += 1
        elif random.randrange(100) < 25:  # (100-45) * 25% = 13.75%
            m.stat_piety -= 1
        m.stat_piety = max(m.stat_piety, race_status[m.race][2])
        m.stat_piety = min(m.stat_piety, race_status[m.race][2]+10)
        if random.randrange(100) < 45:
            m.stat_vitality += 1
        elif random.randrange(100) < 25:  # (100-45) * 25% = 13.75%
            m.stat_vitality -= 1
        m.stat_vitality = max(m.stat_vitality, race_status[m.race][3])
        m.stat_vitality = min(m.stat_vitality, race_status[m.race][3]+10)
        if random.randrange(100) < 45:
            m.stat_agility += 1
        elif random.randrange(100) < 25:  # (100-45) * 25% = 13.75%
            m.stat_agility -= 1
        m.stat_agiilty = max(m.stat_agility, race_status[m.race][4])
        m.stat_agility = min(m.stat_agility, race_status[m.race][4]+10)
        if random.randrange(100) < 45:
            m.stat_luck += 1
        elif random.randrange(100) < 25:  # (100-45) * 25% = 13.75%
            m.stat_luck -= 1
        m.stat_luck = max(m.stat_luck, race_status[m.race][5])
        m.stat_luck = min(m.stat_luck, race_status[m.race][5]+10)

        m.level += 1
        newhp = 0
        if m.stat_vitality <= 3:
            plus = -2
        elif m.stat_vitality <= 5:
            plus = -1
        elif m.stat_vitality >= 20:
            plus = 4
        elif m.stat_vitality >= 18:
            plus = 3
        elif m.stat_vitality >= 16:
            plus = 2
        elif m.stat_vitality >= 15:
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
                if m.stat_iq > random.randrange(30):  # iq
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
                if m.stat_piety > random.randrange(30):  # piety
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

    oldstate = [m.stat_strength, m.stat_iq, m.stat_piety,
                m.stat_vitality, m.stat_agility, m.stat_luck]
    oldhp = m.maxhp
    levels, learned = levelup(game, m)

    m.hp += healhp
    if m.hp > m.maxhp:
        m.hp = m.maxhp

    m.mspell_cnt = m.mspell_max[:]
    m.pspell_cnt = m.pspell_max[:]

    if levels > 0:
        mw.print(f"Level up!")
        if m.stat_strength > oldstate[0]:
            mw.print(
                f"Gained strength by {m.stat_strength-oldstate[0]} points.")
        elif m.stat_strength < oldstate[0]:
            mw.print(f"Lost strength by {oldstate[0]-m.stat_strength} points.")
        if m.stat_iq > oldstate[1]:
            mw.print(
                f"Gained i.q. by {m.stat_iq-oldstate[1]} points.", start=' ')
        elif m.stat_iq < oldstate[1]:
            mw.print(
                f"Lost i.q. by {oldstate[1]-m.stat_iq} points.", start=' ')
        if m.stat_piety > oldstate[2]:
            mw.print(
                f"Gained piety by {m.stat_piety-oldstate[2]} points.", start=' ')
        elif m.stat_piety < oldstate[2]:
            mw.print(
                f"Lost piety by {oldstate[2]-m.stat_piety} points.", start=' ')
        if m.stat_vitality > oldstate[3]:
            mw.print(
                f"Gained vitality by {m.stat_vitality-oldstate[3]} points.", start=' ')
        elif m.stat_vitality < oldstate[3]:
            mw.print(
                f"Lost vitality by {oldstate[3]-m.stat_vitality} points.", start=' ')
        if m.stat_agility > oldstate[4]:
            mw.print(
                f"Gained agility by {m.stat_agility-oldstate[4]} points.", start=' ')
        elif m.stat_agility < oldstate[4]:
            mw.print(
                f"Lost agility by {oldstate[4]-m.stat_agility} points.", start=' ')
        if m.stat_luck > oldstate[5]:
            mw.print(
                f"Gained luck by {m.stat_luck-oldstate[5]} points.", start=' ')
        elif m.stat_luck < oldstate[5]:
            mw.print(
                f"Lost luck by {oldstate[5]-m.stat_luck} points.", start=' ')
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


def inn():
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


def hospital():
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
               random.randrange(100) > 50 + (3*p.stat_vitality):
                mw.print("Oops..")
                v.disp_scrwin()
                p.state = State.ASHED
            elif p.state == State.ASHED and \
                    random.randrange(100) > 40 + (3*p.stat_vitality):
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


def castle():
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
            tavern()
        elif ch == 'e':
            game.party.place = Place.EDGE_OF_TOWN
            break
        elif ch == 't':
            trader()
        elif ch == 'i':
            inn()
        elif ch == 'm':
            hospital()


def edge_town():
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
        if config['client']:
            mw.print("m)aze\nx)expedition to external dungeon", start=' ')
        else:
            mw.print("m)aze", start=' ')
        mw.print(
            "t)raining grounds\nc)astle\nS)ave and quit game\nR)esume from saved data", start=' ')
        vscr.disp_scrwin()
        ch = mw.input_char("Command? ", values=['t', 'S', 'm', 'c', 'R', 'x'])
        if ch == 't':
            training()
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
            save()
            mw.print("Thank you for playing.")
            mw.print("See you soon.")
            vscr.disp_scrwin()
            sys.exit()
        elif ch == 'R':
            if game.load():
                pass
                # mw.print("loaded.")
            vscr.disp_scrwin()
            if game.dungeon.expedition:
                url = f"http://{config['server']['host']}:{config['server']['port']}"
                auth = config['server']['auth'].copy()
                auth['phash'] = hashlib.sha256(
                    bytes(auth['password'], 'utf-8')).hexdigest()
                auth.pop('password')
                game.dungeon.loaded = False
                uuid = game.dungeon.uuid
                try:
                    sio.connect(url, auth)
                except:
                    vscr.cls()
                    game.dungeon.expedition = False
                    game.dungeon.floors = []
                    game.party.place = Place.EDGE_OF_TOWN
                    game.party.floor_obj = None
                    game.party.resumed = False
                    mw.print("Connection error occurred.")
                    mw.print("Falling back to Edge of Town")
                    vscr.disp_scrwin()
                    getch(wait=True)
                    continue
                #mw.print("receiving dungeon data")
                # vscr.disp_scrwin()
                while True:
                    if game.dungeon.loaded:
                        #mw.print("dugeon data received")
                        # vscr.disp_scrwin()
                        break

                game.dungeon.sio = sio
                game.party.place = Place.MAZE
                game.party.resumed = True
                game.dungeon.expedition = True
                if game.dungeon.uuid != uuid:
                    mw.print("Dungeon data removed from the server")
                    mw.print("Entering a new dungeon")
                    vscr.disp_scrwin()
                    game.dungeon.floors = []
                    game.party.floor_obj = None
                    game.party.resumed = False
                    # sio.disconnect()
                    getch(wait=True)
            break
        elif ch == 'x' and game.party.members:
            url = f"http://{config['server']['host']}:{config['server']['port']}"
            auth = config['server']['auth'].copy()
            auth['phash'] = hashlib.sha256(
                bytes(auth['password'], 'utf-8')).hexdigest()
            auth.pop('password')
            game.dungeon.loaded = False
            try:
                sio.connect(url, auth)
            except:
                mw.print("Connection error occurred.")
                vscr.disp_scrwin()
                getch(wait=True)
                continue

            mw.print(
                f"Traveling to {config['server']['host']} as {config['server']['auth']['user']}@{config['server']['auth']['team']} ({sio.sid})")
            vscr.disp_scrwin()
            game.dungeon.expedition = True
            game.dungeon.sio = sio
            game.party.place = Place.MAZE
            while True:
                if game.dungeon.loaded:
                    break
            break


def camp(game, floor_obj):
    """
    Camp main
    """
    game.party.place = Place.CAMP
    game.party.push_loc()
    v = game.vscr
    mw = Meswin(v, 10, 1, 64, 17, frame=True)
    v.meswins.append(mw)
    dg = game.dungeon

    if dg.expedition and dg.party_locs:
        dg.parties = {}
        dg.spells_casted = []
        v.show_puser = config['server']['auth']['user']
        p = game.party
        ulist = dg.get_gcamp_users()
        if ulist:
            sio.emit('get_party', ulist)
            ustr = ', '.join(ulist)
            mw.print(f"group camp with {ustr}.")
            time.sleep(0.3)

    while not game.party.floor_move:  # tsubasa?
        mw.cls()
        if dg.get_gcamp_users():
            if game.vscr.show_puser == config['server']['auth']['user']:
                mw.print("*** group camp menu ***\ni)nspect\nr)eorder party")
                mw.print("h)eal all members\np)rep for adventure", start=' ')
                mw.print("P)switch parties\nS)ave and quit game\nl)eave",
                         start=' ')
                c = mw.input_char("Command?",
                                  values=['i', 'r', 'S', 'l',
                                          'h', 'p', 'P', 'm'])
            else:
                mw.print("*** group camp menu (view) ***\ni)nspect")
                mw.print("P)switch parties\nS)ave and quit game\nl)eave",
                         start=' ')
                c = mw.input_char("Command?", values=['i', 'S', 'l', 'P', 'm'])
        else:
            mw.print(
                "*** camp menu ***\ni)nspect\nr)eorder party\nh)eal all members\np)rep for adventure\nS)ave and quit game\nl)eave")
            c = mw.input_char("Command?", values=[
                              'i', 'r', 'S', 'l', 'h', 'p', 'm'])
        if c == 'l':
            break
        elif c == 'r':
            game.party.reorder()
        elif c == 'h':
            game.party.heal()
        elif c == 'p':
            game.party.prep()
        elif c == 'S':
            game.party.place = Place.MAZE
            save()
            mw.print("Thank you for playing.")
            mw.print("See you again soon.")
            v.disp_scrwin()
            if game.dungeon.expedition:
                sio.disconnect()
            sys.exit()
        elif c == 'i':
            idx = 1
            while not game.party.floor_move:  # tsubasa?
                if game.party.place == Place.CAMP and game.dungeon.expedition\
                   and game.vscr.show_puser != config['server']['auth']['user']:
                    p = dg.parties[game.vscr.show_puser]
                else:
                    p = game.party
                mem = p.members[idx-1]
                rtn = mem.inspect_character()
                if rtn == 0:
                    break
                idx += rtn
                if idx < 0:
                    idx = len(p.members) - 1
                elif idx >= len(p.members):
                    idx = 0
        elif c == 'P':
            ulist = [config['server']['auth']['user']]
            ulist.extend(dg.get_gcamp_users())
            u = game.vscr.show_puser
            uidx = ulist.index(u)
            if (uidx := uidx + 1) >= len(ulist):
                uidx = 0
            game.vscr.show_puser = ulist[uidx]
        elif c == 'm':
            send_message()
            continue

    v.disp_scrwin(floor_obj)
    v.meswins.pop()
    game.party.place = Place.MAZE
    game.party.push_loc()


def maze():
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
        if not dungeon.expedition:
            dungeon.uuid = uuid.uuid1().hex
        party.floor_obj = floor_obj = None
    party.resumed = False
    dungeon.party_locs = {}
    dungeon.parties = {}
    dungeon.spells_casted = []

    loop_cnt = 0
    checked = False
    while True:
        if not checked:
            checked = True
            dungeon.generate_move_floors()
            floor_obj = party.floor_obj

            if party.light_cnt > 0:  # milwa/lomilwa counter
                party.light_cnt -= 1

            party.calc_hpplus()
            for mem in party.members:
                if mem.state not in [State.DEAD, State.ASHED, State.LOST]:
                    mem.hp = min(max(1, mem.hp+mem.hpplus), mem.maxhp)

            if game.saving == 2:
                game.thread.join()
                vscr.meswins[0].print("...saved")
                vscr.disp_scrwin(floor_obj)
                game.saving = 0

            vscr.disp_scrwin()

            game.battle.join_user = None  # initialize
            rt = floor_obj.check_event()
            if party.defeated():  # Defeated by boss monster?
                break
            if not rt:  # event processed
                rtn = game.battle.check_battle()
                if rtn:  # 1: random or 2: room
                    meswin.print("*** encounter ***")
                    vscr.disp_scrwin(floor_obj)
                    if not game.dungeon.expedition or game.battle.join_user:
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
            checked = False
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
                floor_obj.open_door(meswin)
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
                save()
            elif c == '#' and config['debug']:
                for y in range(party.y-10, party.y+10+1):
                    for x in range(party.x-32, party.x+32+1):
                        floor_obj.put_tile(
                            x, y, floor_obj.get_tile(x, y), orig=False)
            elif c == 'm' and game.dungeon.expedition:
                send_message()
            else:
                pass

            draw = False
            if vscr.messages:  # one message at a time
                user, mes = vscr.messages.pop(0)
                meswin.print(f"Message from {user}:")
                meswin.print(mes, start=' ')
                draw = True
        else:
            draw = False
            if vscr.messages:  # one message at a time
                user, mes = vscr.messages.pop(0)
                meswin.print(f"Message from {user}:")
                meswin.print(mes, start=' ')
                draw = True
        if draw:
            vscr.disp_scrwin(floor_obj)
        loop_cnt += 1

    vscr.meswins = meswins_save
    vscr.cls()
    party.place = Place.EDGE_OF_TOWN
    vscr.disp_scrwin()


def dispatch():
    """
    dispatch either to edge of town, castle or maze
    """
    while game.party.place != Place.LEAVE_GAME:
        pl = game.party.place
        if pl == Place.EDGE_OF_TOWN:
            edge_town()
        elif pl == Place.CASTLE:
            castle()
        elif pl == Place.MAZE:
            maze()


def save():
    """
    Dispatch a game.save thread to start save
    """
    if game.saving != 0:
        return

    game.vscr.meswins[-1].print("saving..")
    game.vscr.disp_scrwin()
    game.saving = 1  # saving

    thread = Thread(target=game.save)
    thread.start()
    game.thread = thread


def send_message():
    """
    Enter and send message to fellow parties
    Valid only in a server dungeon
    """
    if game.dungeon.expedition:
        vscr = game.vscr
        mw = Meswin(vscr, 6, 2, 64, 2, frame=True)
        vscr.meswins.append(mw)
        mes = mw.input('Message to send?')
        sio.emit('message', mes)
        vscr.meswins.pop()


if config['client']:
    @sio.event
    def connect():
        sio.emit('get_plocs')
        # print("Connected")

    @sio.event
    def send_plocs(data):
        game.dungeon.party_locs = data
        user = config['server']['auth']['user']
        if user in game.dungeon.party_locs:
            game.dungeon.party_locs.pop(user)

    @sio.event
    def connect_error(data):
        print("Connection failed.")

    @sio.event
    def disconnect():
        print("Disconnected.")

    @sio.event
    def message(data):
        game.vscr.messages.append((data['user'], data['message']))

    @sio.event
    def battle_msg(data):
        # if game.party.place == Place.BATTLE and game.dungeon.joined_battle():
        if game.party.place == Place.BATTLE:
            game.vscr.battle_messages.append((data['msg'], data['start']))

    @sio.event
    def party_loc(data):
        game.dungeon.party_locs[data['user']] = (
            data['x'], data['y'], data['floor'], data['place'])
        game.vscr.refresh = True
        # print(f"{data['user']}-{game.dungeon.party_locs[data['user']]}")

    @sio.event
    def dungeon(data):
        if game.dungeon.uuid != data['uuid']:
            game.dungeon.floors = []
            game.dungeon.events = []
            game.dungeon.uuid = data['uuid']
            game.dungeon.events = [(Evloctype[event[0]], event[1], Eventid[event[2]])
                                   for event in data['events']]
        game.dungeon.loaded = True

    @sio.event
    def floor_dic(fdic):
        f = Floor(fdic['x_size'], fdic['y_size'],
                  fdic['floor'], bytearray(fdic['floor_data']))
        f.floor_orig = bytearray(fdic['floor_orig'])
        f.up_x = fdic['up_x']
        f.up_y = fdic['up_y']
        f.down_x = fdic['down_x']
        f.down_y = fdic['down_y']
        rooms = fdic['rooms']
        f.rooms = [Room(r[0], r[1], r[2], r[3]) for r in rooms]
        f.events = {tuple(k.split(',')): [Eventid[v[0]], v[1]]
                    for k, v in fdic['events'].items()}
        f.battled = fdic['battled']
        game.dungeon.floor_obj = f

    @sio.event
    def get_party(requester):
        """
        Requester requests my party so send it back and request
        its party as well
        """
        if requester == config['server']['auth']['user']:
            return
        data = {'requester': requester,
                'party_s': game.party.todic()}
        sio.emit('update_party', data)  # send my party info
        if requester not in game.dungeon.parties:
            sio.emit('get_party', [requester])  # request its party info

    @sio.event
    def update_party(data):
        """
        """
        user = data['sender']
        ul = game.dungeon.party_locs[user]
        p = game.party

        if p.place == Place.CAMP and p.x == ul[0] and p.y == ul[1] and \
           p.floor == ul[2] and p.place.name == ul[3] and \
           user != config['server']['auth']['user']:
            pt = Party(0, 0, 0)
            pt.fromdic(data['party_s'])
            game.dungeon.parties[user] = pt

    @sio.event
    def get_monp(requester):
        """
        Requester requests my monp so send it back
        """
        data = {'requester': requester,
                'monp_s': game.battle.monp_todic()}
        sio.emit('send_monp', data)

    @sio.event
    def send_monp(monp_s):
        """
        Received monp_s from joined client so update mine
        """
        refresh = False
        monp = game.battle.monp
        if game.party.place != Place.BATTLE or \
           (not monp and game.battle.monp_set):
            return
        if monp:
            if monp[0].name != monp_s[0]['name']:  # top monsters differ
                return
        for mong, mong_s in itertools.zip_longest(monp, monp_s,
                                                  fillvalue=None):
            if not mong_s:
                continue
            if not mong:
                mong = Monstergrp(game, mong_s['name'])
                monp.append(mong)
            mong.identified = mong_s['identified']
            for mon, mon_s in itertools.zip_longest(
                    mong.monsters, mong_s['monsters'], fillvalue=None):
                if not mon_s:
                    continue
                if not mon:
                    mon = Monster(game, mon_s['name'])
                    mon.hp = mon_s['hp']
                    mon.hpplus = mon_s['hpplus']
                    mon.ac = mon_s['ac']
                    mon.state = State[mon_s['state']]
                    mon.silenced = mon_s['silenced']
                    mon.poisoned = mon_s['poisoned']
                    mong.monsters.append(mon)
                else:
                    if mon.hp > mon_s['hp']:
                        mon.hp = mon_s['hp']
                        mon.hpplus = mon_s['hpplus']
                        mon.ac = mon_s['ac']
                    if mon.state.value < State[mon_s['state']].value:
                        mon.state = State[mon_s['state']]
                        if mon.state in [State.DEAD, State.ASHED, State.LOST]:
                            # Get a quarter exp if the other party killed a monster
                            game.battle.exp += game.mondef[mong.name].exp // 4
                            refresh = True
                    if mon_s['silenced']:
                        mon.silenced = True
                    if mon_s['poisoned']:
                        mon.poisoned = True
        if refresh:
            game.battle.draw_ew()
            game.vscr.disp_scrwin()
        game.battle.monp_set = True

    @sio.event
    def cast_spell(data):
        """
        Other party member casted a spell for you.
        Used only in a group camp.
        """
        t = (data['user'], data['spell'], data['caster'], data['target'])
        game.dungeon.spells_casted.append(t)

    @sio.event
    def buy(data):
        if data['buyer'] not in game.dungeon.parties:
            return
        mem = next(mem for mem in game.party.members
                   if mem.name == data['member'])
        try:
            item = mem.items[data['item_idx']]
        except:
            return
        if item.name == data['item'] and not item.equipped and \
           not item.cursed and not item.unidentified and \
           item.onsale:  # still on sale?
            mem.gold += data['price']
            del mem.items[data['item_idx']]
            game.vscr.messages.append(
                (data['buyer'], f"Bought <{data['item']}> from {data['seller']}."))
            sio.emit('sold', data)

    @sio.event
    def sold(data):
        try:
            mem = next(mem for mem in game.party.members
                       if mem.name == data['buyer_member'])
        except:
            return
        if mem.gold >= data['price']:
            mem.gold -= data['price']
        else:
            if not game.party.pay(data['price']):
                return
        bought = Memitem(data['item'])
        mem.items.append(bought)
        game.vscr.messages.append(
            (data['seller'], f"Sold <{data['item']}> to {data['buyer']}."))


game = Game()  # singleton

if os.path.exists("dl.db"):
    config['newdb'] = False
engine = create_engine('sqlite:///dl.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def main():
    with open('dlconf.yaml') as f:  # load cofig
        config.update(yaml.safe_load(f))
    party = Party(0, 0, 1)
    game.party = party
    loaddef_all()
    party.place = Place.CASTLE
    w, h = terminal_size()
    vscr = Vscr(w, h-1)  # singleton
    # vscr = Vscr(78, 24)  # +++++++++++++++
    game.vscr = vscr
    # meswin for scrollwin
    vscr.meswins.append(Meswin(vscr, 43, vscr.height-7, vscr.width-42, 7))
    # meswin for castle/edge of town
    vscr.meswins.append(Meswin(vscr, 10, vscr.height//5, vscr.width-20,
                               (vscr.height-8)*2//3, frame=True))
    game.spell = Spell()  # singleton
    game.dungeon = Dungeon()  # singleton
    game.battle = Battle()  # singleton
    game.chest = Chest()  # singleton

    dispatch()


if __name__ == "__main__":
    main()
