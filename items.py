# -*- coding: utf-8 -*-

from struct import unpack

from constants import ITEM_TYPES, LAYER_TYPES

class Item(object):
    """Represents an item."""

    def __init__(self, type_num):
        self.type = ITEM_TYPES[type_num]

    def load(self, info):
        fmt = '{0}i'.format(len(info) / 4)
        self.data = unpack(fmt, info)
        #print 'Type:', self.type
        #print 'Length:', len(unpack(fmt, info))
        #print 'Data:', self.data
        #print ''

    def __repr__(self):
        return '<{0} Item>'.format(self.type.title())

class Layer(object):
    """Represents the layer data every layer has."""

    num = 0

    def __init__(self, item):
        self.version, self.type, self.flags = item.data[2:5]
        Layer.num += 1
        self.num = Layer.num

class Group(object):
    """Represents a group."""

    num = 0

    def __init__(self, item):
        self.version, self.offset_x, self.offset_y, self.parallax_x, \
        self.parallax_y, self.start_layer, self.num_layers, self.use_clipping, \
        self.clip_x, self.clip_y, self.clip_w, self.clip_h = item.data[2:]
        Group.num += 1
        self.num = Group.num
        print self.num

    def __repr__(self):
        return '<Group {0} (Start Layer: {1}, Num Layers: {2})>'.format(self.num, self.start_layer, self.num_layers)

class Quad(Layer):
    """Represents a quad layer."""

    def __init__(self, item):
        super(Quad, self).__init__(item)
        #print item.data[3]
        self.version, self.num_quads, self.data, self.image = item.data[5:]

    def __repr__(self):
        return '<Quad layer {0} (Num Quads: {1})>'.format(self.num, self.num_quads)

class Tile(Layer):
    """Represents a tile layer."""

    def __init__(self, item):
        super(Tile, self).__init__(item)
        self.color = {'r': 0, 'g': 0, 'b': 0, 'a':0}
        self.version, self.width, self.height, self.flags, self.color['r'], \
        self.color['g'], self.color['b'], self.color['a'], self.color_env, \
        self.color_env_offset, self.image, self.data = item.data[5:]

    def __repr__(self):
        return '<Tile layer {0} (width: {1} x  {2} :height)>'.format(self.num, self.width, self.height)
