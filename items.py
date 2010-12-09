# -*- coding: utf-8 -*-

from struct import unpack
from zlib import decompress

from constants import ITEM_TYPES, LAYER_TYPES

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

        #print 'Type:', self.type
        #print 'Length:', len(unpack(fmt, info))
        #print 'Data:', self.data
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
        return '<Group {0}>'.format(self.num)

class Layer(object):
    """Represents the layer data every layer has."""

    num = 0

    def __init__(self, item):
        self.version, self.type, self.flags = item.info[2:5]
        Layer.num += 1
        self.id = Layer.num

    @property
    def is_gamelayer(self):
        return False

class QuadLayer(Layer):
    """Represents a quad layer."""

    def __init__(self, item):
        super(QuadLayer, self).__init__(item)
        self.version, self.num_quads, self.data, self.image = item.info[5:]

    def __repr__(self):
        return '<Quad layer {0}>'.format(self.id)

class TileLayer(Layer):
    """Represents a tile layer."""

    def __init__(self, item):
        super(TileLayer, self).__init__(item)
        self.color = {'r': 0, 'g': 0, 'b': 0, 'a':0}
        self.version, self.width, self.height, self.flags, self.color['r'], \
        self.color['g'], self.color['b'], self.color['a'], self.color_env, \
        self.color_env_offset, self.image, self.data = item.info[5:]
        # load tile data
        self.tiles = []
        while(item.data):
            tile = {
                'index': item.data.pop(0),
                'flags': item.data.pop(0),
                'skip': item.data.pop(0),
                'reserved': item.data.pop(0)
            }
            self.tiles.append(tile)

    @property
    def is_gamelayer(self):
        return self.flags == 1

    def __repr__(self):
        return '<Tile layer {0} ({1}x{2})>'.format(self.id, self.width, self.height)
