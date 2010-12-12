# -*- coding: utf-8 -*-

#import png
from struct import unpack
from zlib import decompress

from constants import ITEM_TYPES, LAYER_TYPES

class Tile(object):
    """Represents a tile of a tilelayer."""

    def __init__(self, index=0, flags=0, skip=0, reserved=0):
        self.index = index
        self.flags = flags
        self.skip = skip
        self.reserved = reserved

    def __repr__(self):
        return '<Tile {0}>'.format(self.index)

class Version(object):

    size = 12

    def __init__(self, item):
        self.item = item

class Info(object):

    def __init__(self, item):
        self.item = item

class Image(object):
    """Represents an image."""

    size = 32

    def __init__(self, item):
        self.version, self.width, self.height, self.external, self.image_name, self.image_data = item.info[2:]
        self.name = item.name
        self.item = item
        self.image = item.data if not self.external else None

    #def save(self):
    #    if not self.external:
    #        if not os.path.isdir('images'):
    #            os.mkdir('images')
    #        f = open(os.path.join('images', self.name)+'.png', 'wb')
    #        w = png.Writer(self.width, self.height, alpha=True)
    #        w.write(f, self.image)
    #        f.close()

    @property
    def itemdata(self):
        return (Image.size-8, 1, self.width, self.height, self.external,
                self.image_name, self.image_data)

    def __repr__(self):
        return '<Image>'

class Envelope(object):
    """Represents an envelope."""

    size = 56

    def __init__(self, item):
        self.version, self.channels, self.start_point, self.num_points = item.info[2:6]
        self.name = self.ints_to_string(item.info[6:])
        self.item = item

    def ints_to_string(self, num):
        string = ''
        for i in range(len(num)):
            string += chr(((num[i]>>24)&0xff)-128)
            string += chr(((num[i]>>16)&0xff)-128)
            string += chr(((num[i]>>8)&0xff)-128)
            if i < 7:
                string += chr((num[i]&0xff)-128)
        return string

    def string_to_ints(self):
        ints = []
        for i in range(8):
            string = ''
            for j in range(i*4, i*4+4):
                if j < len(self.name):
                    string += self.name[j]
                else:
                    string += chr(0)
            ints.append(((ord(string[0])+128)<<24)|((ord(string[1])+128)<<16)|((ord(string[2])+128)<<8)|(ord(string[3])+128))
        ints[-1] &= 0xffffff00
        return ints

    @property
    def itemdata(self):
        return (Envelope.size-8, 1, self.channels, self.start_point,
                self.num_points)

    def __repr__(self):
        return '<Envelope>'

class Envpoint(object):
    """Represents an envpoint."""

    def __init__(self, info):
        self.time, self.curvetype = info[:2]
        self.values = info[2:]

    def __repr__(self):
        return '<Envpoint>'.format()

class Item(object):
    """Represents an item."""

    def __init__(self, type_num):
        self.type = ITEM_TYPES[type_num]

    def load(self, info, data):
        fmt = '{0}i'.format(len(info) / 4)
        self.info = unpack(fmt, info)

        # load data to layers
        if self.type == 'layer':
            if LAYER_TYPES[self.info[3]] == 'tile':
                data = decompress(data[self.info[-1]])
                fmt = '{0}B'.format(len(data))
                self.data = list(unpack(fmt, data))
            elif LAYER_TYPES[self.info[3]] == 'quad':
                data = decompress(data[self.info[-2]])
                fmt = '{0}i'.format(len(data) / 4)
                self.data = list(unpack(fmt, data))
        # load image data
        if self.type == 'image':
            name = decompress(data[self.info[-2]])
            fmt = '{0}c'.format(len(name))
            self.name = ''
            for char in unpack(fmt, name):
                if char == '\x00':
                    break
                self.name += char

            if not self.info[5]:
                data = decompress(data[self.info[-1]])
                fmt = '{0}B'.format(len(data))
                data = list(unpack(fmt, data))
                self.data = []
                for i in range(self.info[4]):
                    self.data.append(data[i*self.info[3]*4:(self.info[3]*4)+(i*self.info[3]*4)])

    def __repr__(self):
        return '<{0} Item>'.format(self.type.title())

class Group(object):
    """Represents a group."""

    size = 56

    def __init__(self, item):
        self.version, self.offset_x, self.offset_y, self.parallax_x, \
        self.parallax_y, self.start_layer, self.num_layers, self.use_clipping, \
        self.clip_x, self.clip_y, self.clip_w, self.clip_h = item.info[2:]
        self.layers = []

    @property
    def itemdata(self):
        return (Group.size-8, 2, self.offset_x, self.offset_y,
                self.parallax_x, self.parallax_y, self.start_layer,
                self.num_layers, self.use_clipping, self.clip_x, self.clip_y,
                self.clip_w, self.clip_h)
    def __repr__(self):
        return '<Group>'

class Layer(object):
    """Represents the layer data every layer has."""

    def __init__(self, item):
        self.version, self.type, self.flags = item.info[2:5]
        self.item = item

    @property
    def is_gamelayer(self):
        return False

class QuadLayer(Layer):
    """Represents a quad layer."""

    size = 36

    def __init__(self, item):
        super(QuadLayer, self).__init__(item)
        self.version, self.num_quads, self._data, self.image = item.info[5:]
        # load quads
        self.quads = []
        points = []
        for i in range(len(item.data)/38):
            for j in range(5):
                point = {'x': item.data[i*38+j*2], 'y': item.data[i*38+j*2+1]}
                points.append(point)
            colors = []
            for j in range(4):
                color = {'r': item.data[i*38+j*4+10], 'g': item.data[i*38+j*4+11], 'b': item.data[i*38+j*4+12], 'a': item.data[i*38+j*4+13]}
                colors.append(color)
            texcoords = []
            for j in range(4):
                texcoord = {'x': item.data[i*38+j*2+26], 'y': item.data[i*38+j*2+27]}
                texcoords.append(texcoord)
            quad = {'points': points, 'colors': colors, 'texcoords': texcoords, 'pos_env': item.data[i*38+34],
                    'pos_env_off': item.data[i*38+35], 'color_env': item.data[i*38+36], 'color_env_off': item.data[i*38+37]}
            self.quads.append(quad)

    @property
    def itemdata(self):
        return (QuadLayer.size-8, 1, self.type, self.flags, 1, self.num_quads,
                self._data, self.image)

    def __repr__(self):
        return '<Quad layer>'

class TileLayer(Layer):
    """Represents a tile layer."""

    size = 68

    def __init__(self, item):
        super(TileLayer, self).__init__(item)
        self.color = {'r': 0, 'g': 0, 'b': 0, 'a': 0}
        self.version, self.width, self.height, self.game, self.color['r'], \
        self.color['g'], self.color['b'], self.color['a'], self.color_env, \
        self.color_env_offset, self.image, self._data = item.info[5:]
        # load tile data
        self.tiles = []
        i = 0
        while(i < len(item.data)):
            self.tiles.append(Tile(*item.data[i:i+4]))
            i += 4

    @property
    def is_gamelayer(self):
        return self.game == 1

    @property
    def itemdata(self):
        return (TileLayer.size-8, 0, self.type, self.flags, 2, self.width,
                self.height, self.game, self.color['r'], self.color['g'],
                self.color['b'], self.color['a'], self.color_env,
                self.color_env_offset, self.image, self._data)

    def __repr__(self):
        return '<Tile layer ({0}x{1})>'.format(self.width, self.height)
