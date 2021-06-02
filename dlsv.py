import os
import random
import uuid
from datetime import datetime
from enum import Enum
import yaml
import socketio
from aiohttp import web
import aiofiles

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


class Eventid(Enum):
    RNDMSG, KEY, BOSS = range(3)


class Evloctype(Enum):
    RANDOM, DOWNSTAIRS = range(2)


class Place(Enum):
    MAZE, EDGE_OF_TOWN, TRAINING_GROUNDS, CASTLE, HAWTHORNE_TAVERN, TRADER_JAYS, LAKEHOUSE_INN, MGH, CAMP, BATTLE, LEAVE_GAME = range(
        11)


login_teams = {}  # key=team: value=Team object
login_users = {}  # key=user: value=sid
registered_users = {}
userfile_path = "users.yaml"


@sio.on('connect')
async def connect(sid, environ):
    # print(environ)  # for debug
    user = environ['HTTP_USER']
    room = environ['HTTP_TEAM']
    phash = environ['HTTP_PHASH']
    if not user or not room or not phash:
        return
    if user not in registered_users.keys():
        # register user
        registered_users[user] = {}
        registered_users[user]['phash'] = phash
        print(f"New user rigstered: {user}")
    else:
        if phash != registered_users[user]['phash']:
            print(F"Login failed for {user}")
            # incorrect password
            return
    registered_users[user]['last_login'] = datetime.now()
    yf = yaml.dump(registered_users)
    async with aiofiles.open(userfile_path, 'w') as f:
        # for l in yf:
        await f.write(yf)
    if room not in login_teams:
        login_teams[room] = Team(room)
    team = login_teams[room]
    team.logins[user] = datetime.now()
    login_users[user] = sid
    sio.enter_room(sid, room)
    async with sio.session(sid) as session:
        session['user'] = user
        session['team'] = room
    await sio.emit('dungeon', {'uuid': team.dungeon.uuid,
                               'events': team.dungeon.events}, room=sid)
    print(
        f"connect user: {user}, sid: {sid}, team: {room}, uuid: {team.dungeon.uuid}")


@sio.on('message')
async def message(sid, data):
    async with sio.session(sid) as session:
        user = session['user']
        team = session['team']
    print(f"Message from {user}: {data}")
    mesdic = {'user': user, 'message': data}
    await sio.emit('message', mesdic, room=team)


@sio.event
async def get_plocs(sid):
    """
    Send back party locations that are logged in
    """
    async with sio.session(sid) as session:
        team = session['team']
    dungeon = login_teams[team].dungeon
    await sio.emit('send_plocs', dungeon.team_locs, room=sid)


@sio.event
async def get_party(sid, ulist):
    """
    Request party info to users in ulist
    """
    async with sio.session(sid) as session:
        requester = session['user']
    if requester in ulist:
        print(f"{requester} wants its own party.  Igoring.")
        ulist.remove(requester)
    for user in ulist:
        await sio.emit('get_party', requester, sid=login_users[user])
        print(f"{requester} requests party update to {user}")


@sio.event
async def update_party(sid, data):
    """
    Update sender's party_s to requester
    If requester is None, emit to all users who are in the same location
    as the sender and camping (ie, in the joined camp as the sender)
    """
    async with sio.session(sid) as session:
        sender = session['user']
        team = session['team']
    dungeon = login_teams[team].dungeon
    sloc = dungeon.team_locs[sender]
    if data['requester']:
        users = [data['requester']]
        if data['requester'] == sender:
            print(f"{data['requester']} wants {sender} party.  Aborting.")
            return
    else:
        users = [k for k, v in dungeon.team_locs.items() if v[0] == sloc[0] and
                 v[1] == sloc[1] and v[2] == sloc[2] and v[3] == Place.CAMP.name
                 and k != sender]
    updata = {'sender': sender, 'party_s': data['party_s']}
    for user in users:
        await sio.emit('update_party', updata, room=login_users[user])
        print(f"Update {sender} party_s to {users}")
        # print(f"{data['party_s']['members']}")


@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)


@sio.on('get_monp')
async def get_monp(sid, sender):
    """
    Request monster party info to sender (of the info)
    Used for joined battles
    """
    async with sio.session(sid) as session:
        requester = session['user']
    await sio.emit('get_monp', requester, room=login_users[sender])
    print(
        f"get_monp request from {requester}({sid}) to {sender}({login_users[sender]})")


@sio.on('send_monp')
async def send_monp(sid, data):
    """
    Send back monster party info to requester
    Used for joined battles
    """
    await sio.emit('send_monp', data['monp_s'], room=login_users[data['requester']])
    print(f"sent monp_s to {data['requester']}")


@sio.event
async def update_monp(sid, monp_s):
    async with sio.session(sid) as session:
        team = session['team']
        user = session['user']
    tm = login_teams[team]  # Team object
    loc = tm.dungeon.team_locs[user]  # (x, y, floor, place)
    users = []  # user list to update monp
    for k, v in tm.dungeon.team_locs.items():
        if loc == v:
            users.append(k)
    for u in users:
        if u != user:
            await sio.emit('send_monp', monp_s, room=login_users[u])
            print(f"update_monp from {user} to {login_users[u]}")


@sio.event
async def battle_msg(sid, data):
    async with sio.session(sid) as session:
        team = session['team']
        user = session['user']
    tm = login_teams[team]  # Team object
    loc = tm.dungeon.team_locs[user]  # (x, y, floor, place)
    users = []  # user list to update monp
    for k, v in tm.dungeon.team_locs.items():
        if loc == v:
            users.append(k)
    for u in users:
        if u != user:
            await sio.emit('battle_msg', data, room=login_users[u])
            # print(f"battle_msg: {data['msg']}, {data['start']}")


@sio.on('party_move')
async def party_move(sid, data):
    async with sio.session(sid) as session:
        team = session['team']
        user = session['user']
    dungeon = login_teams[team].dungeon
    dungeon.team_locs[user] = (
        data['x'], data['y'], data['floor'], data['place'])
    locdic = {}
    locdic['user'] = user
    locdic['x'] = data['x']
    locdic['y'] = data['y']
    locdic['floor'] = data['floor']
    locdic['place'] = data['place']
    # print(
    #    f"{user} - ({locdic['x']},{locdic['y']})@{locdic['floor']}%{locdic['place']}")
    await sio.emit('party_loc', locdic, room=team, skip_sid=sid)


@ sio.on('exit_dungeon')
async def exit_dungeon(sid):
    async with sio.session(sid) as session:
        team = session['team']
        user = session['user']
    del login_teams[team].logins[user]
    print(f"{user} exited from dungeon")
    if not login_teams[team].logins:  # empty->everyone logged out?
        del login_teams[team]
        print(f"Team {team} removed.")


@sio.on('load_floor')
async def load_floor(sid, floor):
    async with sio.session(sid) as session:
        team = session['team']
    dungeon = login_teams[team].dungeon
    if floor in dungeon.floors:
        f = dungeon.floors[floor]
    else:
        f = dungeon.generate_floor(floor)
        dungeon.floors[floor] = f
    rooms = tuple([(r.x, r.y, r.x_size, r.y_size) for r in f.rooms])
    # convert tuple keys to string (as it can't be serialized)
    events = {','.join([str(k[0]), str(
        k[1])]): v for k, v in f.events.items()}
    floor_dic = {'x_size': f.x_size, 'y_size': f.y_size, 'floor': f.floor,
                 'up_x': f.up_x, 'up_y': f.up_y,
                 'down_x': f.down_x, 'down_y': f.down_y,
                 'floor_orig': bytes(f.floor_orig), 'floor_data': bytes(f.floor_data),
                 'rooms': rooms, 'events': events, 'battled': f.battled}
    await sio.emit('floor_dic', floor_dic, room=sid)
    print(f"Sent floor {floor} data to {sid}")


@sio.event
async def cast_spell(sid, sdata):
    """
    Cast spell for other party member.
    """
    async with sio.session(sid) as session:
        user = session['user']
    data = {'user': user, 'spell': sdata['spell'], 'caster': sdata['caster'],
            'target': sdata['target']}
    await sio.emit('cast_spell', data, room=login_users[sdata['user']])
    print(f"Cast {sdata['spell']} for {sdata['target']}({sdata['user']})")


class Team:
    """
    Represents a team
    """

    def __init__(self, team):
        self.team = team
        self.logins = {}  # key: user, value: sid
        self.dungeon = Dungeon()

    def __repr__(self):
        return f"Team<{self.team} - {self.logins}, {self.dungeon}>"


class Dungeon:
    """
    Represents a dungeon
    """

    def __init__(self):
        self.floors = {}  # dict of floor objects (server)
        self.events = []  # list of events (floor, eventid)
        self.generate_events()
        self.uuid = uuid.uuid1().hex
        # user: (x, y, floor, place)  # Place.MAZE, .CAMP or .BATTLE in text
        self.team_locs = {}

    def __repr__(self):
        return f"Dungeon<{self.uuid} - {self.floors}, {self.events}>"

    def generate_events(self):
        """
        Generate important events when creating a dungeon.
        Later, events need to be placed on creating floors
        """
        # generate keys
        self.events.append((Evloctype.RANDOM.name, 3, Eventid.KEY.name))
        self.events.append((Evloctype.RANDOM.name, 6, Eventid.KEY.name))
        self.events.append((Evloctype.RANDOM.name, 9, Eventid.KEY.name))
        self.events.append((Evloctype.RANDOM.name, 10, Eventid.KEY.name))

        # generate bosses
        self.events.append((Evloctype.DOWNSTAIRS.name, 3, Eventid.BOSS.name))
        self.events.append((Evloctype.DOWNSTAIRS.name, 6, Eventid.BOSS.name))
        self.events.append((Evloctype.DOWNSTAIRS.name, 9, Eventid.BOSS.name))
        self.events.append((Evloctype.DOWNSTAIRS.name, 10, Eventid.BOSS.name))

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
        floor_obj.place_doors(rooms)
        floor_obj.rooms = rooms
        floor_obj.floor_orig = floor_obj.floor_data
        floor_obj.place_events(self)
        floor_obj.floor_data = bytearray(b'^' * floor_x_size * floor_y_size)
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
        self.events = {}  # event list. key is (x, y), value is [eventID, done]

    def __repr__(self):
        s = self.floor_data.decode()
        return f"Floor(size: {self.x_size}x{self.y_size}, floor: {self.floor} - {s})"

    def place_events(self, dungeon):
        """
        Place events on random or specific type location
        """
        for ev in dungeon.events:
            if ev[1] != self.floor:  # event[1] is floor
                continue
            if ev[0] == Evloctype.RANDOM.name:
                while True:
                    x = random.randrange(self.x_size)
                    y = random.randrange(self.y_size)
                    if self.get_tile(x, y) == b'.':  # floor tile
                        break
                self.put_tile(x, y, b',')
                self.events[(x, y)] = [ev[2], False]  # event[2] is eventid
            elif ev[0] == Evloctype.DOWNSTAIRS.name:
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
            self.events[(x, y)] = [Eventid.KEY.name, False]

        # place random messages
        for _ in range(2 + random.randrange(3)):  # 2 to 4 messages
            while True:
                x = random.randrange(self.x_size)
                y = random.randrange(self.y_size)
                if self.get_tile(x, y) == b'.':  # floor tile
                    break
            self.put_tile(x, y, b',')
            self.events[(x, y)] = [Eventid.RNDMSG.name, False]

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


if __name__ == '__main__':
    # read user file once before async starts
    if os.path.exists(userfile_path):
        with open(userfile_path, 'r') as f:
            registered_users = yaml.safe_load(f)
    web.run_app(app)
