# -*- coding: utf-8 -*-

from struct import unpack

from constants import ITEM_TYPES, LAYER_TYPES

class Group(object):
    """Represents a group."""

    def __init__(self, num, data):
        self.num = num
        self.version, self.offset_x, self.offset_y, self.parallax_x, \
        self.parallax_y, self.start_layer, self.num_layers, self.use_clipping, \
        self.clip_x, self.clip_y, self.clip_w, self.clip_h = data

    def __repr__(self):
        return '<Group {0} (Start Layer: {1}, Num Layers: {2})>'.format(self.num, self.start_layer, self.num_layers)

class Layer(object):
    """Represents the layer data every layer has."""

    def __init__(self, num, data):
        self.num = num
        self.version, self.type, self.flags = data[:3]

class LayerQuad(object):
    """Represents a quad layer."""

    def __init__(self, num, data):
        self.layer = Layer(num, data)
        self.version, self.num_quads, self.data, self.image = data[3:]

    def __repr__(self):
        return '<Quad layer {0} (Num Quads: {1})>'.format(self.layer.num, self.num_quads)

class LayerTile(object):
    """Represents a tile layer."""

    def __init__(self, num, data):
        self.layer = Layer(num, data)
        self.color = {'r': 0, 'g': 0, 'b': 0, 'a':0}
        self.version, self.width, self.height, self.flags, self.color['r'], \
        self.color['g'], self.color['b'], self.color['a'], self.color_env, \
        self.color_env_offset, self.image, self.data = data[3:]

    def __repr__(self):
        return '<Tile layer {0} (width: {1} x  {2} :height)>'.format(self.layer.num, self.width, self.height)

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


