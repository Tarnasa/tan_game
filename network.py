import socket
import asynchat
import asyncore
import logging
from importlib import import_module
import struct

from physics import V
from chat import chat
from loader import images

host = '192.168.1.11'
host = '127.0.0.1'
port = 41369

clients = {}
character = None

server = None
client = None


def send_message(msg):
    if server:
        server.push_all(msg + '\n')
    if client:
        client.push(msg + '\n')


def send_create_message(obj, kwargs=''):
    if server or client:
        msg = "C{id}:{classname}:{x},{y},{xv},{yv},{dir}:{kwargs}"
        send_message(msg.format(id=obj.id, classname=obj.__class__.__name__,
                                x=int(obj.pos.x), y=int(obj.pos.y), xv=int(obj.speed.x),
                                yv=int(obj.speed.y), dir=int(obj.direction),
                                kwargs=kwargs))


def send_move_message(obj):
    if server or client:
        msg = "M{id},{x},{y},{xv},{yv},{dir}"
        send_message(msg.format(id=obj.id, x=obj.pos.x, y=obj.pos.y, xv=obj.speed.x, yv=obj.speed.y, dir=obj.direction))


class ChatHandler(asynchat.async_chat):
    def __init__(self, world, sock=None):
        if server is None:
            asynchat.async_chat.__init__(self)
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect((host, port))
        else:
            asynchat.async_chat.__init__(self, sock=sock, map=clients)
        self.set_terminator('\n')
        self.buffer = []
        self.world = world
        self.handlers = {
            'H': self.receive_hello,
            'M': self.receive_move,
            'C': self.receive_create,
            'D': self.receive_damage,  # Unused
            'T': self.receive_talk,
            'X': self.receive_kill,
            'F': self.receive_force,
            'L': self.receive_collide,
        }
        self.other_character = None
        # Tell the server which player we are
        self.push('H' + character + '\n')
        if server:
            self.send_all()

    def collect_incoming_data(self, data):
        self.buffer.append(data)

    def found_terminator(self):
        msg = ''.join(self.buffer)
        logging.info('Received: {0}'.format(msg))  # TODO
        if msg[0] in self.handlers:
            self.handlers[msg[0]](msg)
        else:
            logging.warning('No handler for message: {0}'.format(msg))
        self.buffer = []

    def forward(self, msg):
        """Send the given message to all other clients except the sending one"""
        if server is not None:
            for client in clients.values():
                if client is not server and client is not self:
                    client.push(msg + '\n')

    def send_all(self):
        template = "C{id}:{classname}:{x},{y},{xv},{yv},{dir}:{kwargs}"

        from gameobject import Static
        image_name = {id(v): k for k, v in images.items()}

        for obj in self.world.objs.values():
            if isinstance(obj, Static):
                send_create_message(obj, 'sprites=images[\'{0}\'],depth={1},wall={2}'.format(
                    image_name[id(obj.sprites[0][0])], obj.depth, obj.wall))
            else:
                send_create_message(obj)

    def receive_hello(self, msg):
        """
        Hello - H{character}
            Where {character} is one of w, e, c
        """
        self.other_character = msg[1]
        logging.info('Player {0} joined!'.format(self.other_character))

    def receive_move(self, msg):
        """Position - M{id},{x},{y},{xv},{yv},{dir}"""
        self.forward(msg)
        id, x, y, xv, yv, dir = msg[1:].split(',')
        obj = self.world.objs[id]
        obj.set_pos(V(float(x), float(y)))
        obj.speed = V(float(xv), float(yv))
        obj.direction = int(dir)

    def receive_create(self, msg):
        """
        Create - C{id}:{classname}:{x},{y},{xv},{yv},{dir}:{**kwargs}
            Where {classname} is the classname of the object to be created (such as Spider)
            and {**kwargs} is a comma-separated list of key=value pairs which will be passed to the constructor
        """
        self.forward(msg)
        id, classname, attrs, kwargstring = msg[1:].split(':')
        x, y, xv, yv, dir = map(int, attrs.split(','))
        if id in self.world.objs:
            # Just update position
            obj = self.world.objs[id]
            obj.set_pos(V(int(x), int(y)))
            obj.speed = V(int(xv), int(yv))
            obj.direction = int(dir)
            return
        kwargs = {w.split('=')[0]: eval(w.split('=')[1]) for w in kwargstring.split(',') if w}
        kwargs['id'] = id
        kwargs['pos'] = V(x, y)
        kwargs['speed'] = V(xv, yv)
        kwargs['direction'] = dir
        if classname == 'Witch':
            class_ = import_module('witch').Witch
        elif classname == 'WW':
            class_ = import_module('ww').WW
        elif classname == 'Cat':
            class_ = import_module('cat').Cat
        elif classname == 'Spider':
            class_ = import_module('spider').Spider
        elif classname == 'PlayerFireball':
            class_ = import_module('spell').PlayerFireball
        elif classname == 'Static':
            class_ = import_module('gameobject').Static
        new_obj = class_(**kwargs)
        self.world.add_object(new_obj)

    def receive_damage(self, msg):
        """Damage - D{id}:{amount}"""
        self.forward(msg)
        id, amount = msg[1:].split(':')
        self.world.objs[id].damage(int(amount))

    def receive_talk(self, msg):
        """Talk - T{character}:{message}"""
        self.forward(msg)
        chat.add(msg[1] + ': ' + msg[3:])

    def receive_kill(self, msg):
        """Kill - X{id}"""
        self.forward(msg)
        id = msg[1:]
        if id in self.world.objs:
            self.world.remove_object(self.world.objs[id])

    def receive_force(self, msg):
        """Force - F{id}:{xf}:{yf}"""
        self.forward(msg)
        id, xf, yf = msg[1:].split(':')
        if id in self.world.objs:
            self.world.objs[id].force = V(float(xf), float(yf))
        else:
            logging.warning('Force message received for dead object!')

    def receive_collide(self, msg):
        """Collide - L{id}:{other}"""
        self.forward(msg)
        call_id, other_id = msg[1:].split(':')
        if call_id in self.world.objs and other_id in self.world.objs:
            self.world.objs[call_id].collide(self.world.objs[other_id])
        else:
            logging.warning('L received for dead object')


class Server(asyncore.dispatcher):
    def __init__(self, world):
        asyncore.dispatcher.__init__(self, map=clients)
        self.world = world
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', port))
        self.listen(2)

    def handle_accept(self):
        pair = self.accept()
        if pair:
            sock, addr = pair
            logging.info('Connection from {0}'.format(addr))
            ChatHandler(world=self.world, sock=sock)

    def push_all(self, data):
        for c in clients.values():
            if c is not self:
                c.push(data)

