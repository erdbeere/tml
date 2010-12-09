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

    def __init__(self, item):
        self.item = item

class Info(object):

    def __init__(self, item):
        self.item = item

class Image(object):

    def __init__(self, item):
        self.item = item

class Envelope(object):
    """Represents an envelope."""

    num = 0

    def __init__(self, item):
        self.version, self.channels, self.start_point, self.num_points = item.info[2:6]
        self.name = self.ints_to_string(item.info[6:])
        Envelope.num += 1
        self.id = Envelope.num

    def ints_to_string(self, num):
        string = ''
        for i in range(len(num)):
            string += chr(((num[i]>>24)&0xff)-128)
            string += chr(((num[i]>>16)&0xff)-128)
            string += chr(((num[i]>>8)&0xff)-128)
            if i < 7:
                string += chr((num[i]&0xff)-128)
        return string

    def __repr__(self):
        return '<Envelope {0}>'.format(self.id)

class Envpoint(object):
    """Represents an envpoint."""

    num = 0

    def __init__(self, item):
        self.time, self.curvetype = item.info[:2]
        self.values = item.info[2:]
        Envpoint.num += 1
        self.id = Envpoint.num

    def __repr__(self):
        return '<Envpoint {0}>'.format(self.id)

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

        #print 'Type:', self.type
        #fmt = '{0}i'.format(len(info) / 4)
        #print 'Length:', len(unpack(fmt, info))
        #print 'Data:', self.info
        #print ''

    def __repr__(self):
        return '<{0} Item>'.format(self.type.title())

class Group(object):
    """Represents a group."""

    num = 0

    def __init__(self, item):
        self.version, self.offset_x, self.offset_y, self.parallax_x, \
        self.parallax_y, self.start_layer, self.num_layers, self.use_clipping, \
        self.clip_x, self.clip_y, self.clip_w, self.clip_h = item.info[2:]
        self.layers = []
        Group.num += 1
        self.id = Group.num

    def __repr__(self):
        return '<Group {0}>'.format(self.id)

class Image(object):
    """Represents an image."""

    num = 0

    def __init__(self, item):
        self.version, self.width, self.height, self.external, self.image_name, self.image_data = item.info[2:]
        self.name = item.name
        if not self.external:
            self.image = item.data
        Image.num += 1
        self.id = Image.num

    #def save(self):
    #    if not self.external:
    #        if not os.path.isdir('images'):
    #            os.mkdir('images')
    #        f = open(os.path.join('images', self.name)+'.png', 'wb')
    #        w = png.Writer(self.width, self.height, alpha=True)
    #        w.write(f, self.image)
    #        f.close()

    def __repr__(self):
        return '<Image {0}>'.format(self.id)

class Layer(object):
    """Represents the layer data every layer has."""

    num = 0

    def __init__(self, item):
        self.version, self.type, self.flags = item.info[2:5]
        Layer.num += 1
        self.id = Layer.num
        self.item = item

    @property
    def is_gamelayer(self):
        return False

class QuadLayer(Layer):
    """Represents a quad layer."""

    def __init__(self, item):
        super(QuadLayer, self).__init__(item)
        self.version, self.num_quads, self.data, self.image = item.info[5:]
        # load quads
        self.quads = []
        while(len(item.data)):
            points = []
            for i in range(5):
                point = {'x': item.data.pop(0), 'y': item.data.pop(0)}
                points.append(point)
            colors = []
            for i in range(4):
                color = {'r': item.data.pop(0), 'g': item.data.pop(0), 'b': item.data.pop(0), 'a': item.data.pop(0)}
                colors.append(color)
            texcoords = []
            for i in range(4):
                texcoord = {'x': item.data.pop(0), 'y': item.data.pop(0)}
                texcoords.append(texcoord)
            quad = {'points': points, 'colors': colors, 'texcoords': texcoords, 'pos_env': item.data.pop(0),
                    'pos_env_off': item.data.pop(0), 'color_env': item.data.pop(0), 'color_env_off': item.data.pop(0)}
            self.quads.append(quad)

    def __repr__(self):
        return '<Quad layer {0}>'.format(self.id)

class TileLayer(Layer):
    """Represents a tile layer."""

    def __init__(self, item):
        super(TileLayer, self).__init__(item)
        self.color = {'r': 0, 'g': 0, 'b': 0, 'a': 0}
        self.version, self.width, self.height, self.flags, self.color['r'], \
        self.color['g'], self.color['b'], self.color['a'], self.color_env, \
        self.color_env_offset, self.image, self.data = item.info[5:]
        # load tile data
        self.tiles = []
        while(item.data):
            self.tiles.append(Tile(item.data.pop(0), item.data.pop(0),
                                   item.data.pop(0), item.data.pop(0)))

    @property
    def is_gamelayer(self):
        return self.flags == 1

    def __repr__(self):
        return '<Tile layer {0} ({1}x{2})>'.format(self.id, self.width, self.height)
