# -*- coding: utf-8 -*-
"""
    Collection of different items.

    :copyright: 2010-2011 by the TML Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""

import os
from StringIO import StringIO
from struct import unpack, pack
from utils import ints_to_string
from zlib import decompress

from constants import ITEM_TYPES, LAYER_TYPES, TML_DIR

#GAMELAYER_IMAGE = PIL.Image.open(os.path.join(TML_DIR,
#	os.extsep.join(('entities', 'png'))))

class Quad(object):
    """Represents a quad of a quadlayer."""

    def __init__(self, points=None, colors=None, texcoords=None, pos_env=-1,
                    pos_env_offset=0, color_env=-1, color_env_offset=0):
        self.points = []
        if points:
            for i in range(5):
                point = {'x': points[i*2], 'y': points[i*2+1]}
                self.points.append(point)
            points = []
        else:
            for i in range(5):
                point = {'x': 0, 'y': 0}
                self.points.append(point)
        self.colors = []
        if colors:
            for i in range(4):
                color = {'r': colors[i*4], 'g': colors[i*4+1],
                        'b': colors[i*4+2], 'a': colors[i*4+3]}
                self.colors.append(color)
            colors = []
        else:
            for i in range(4):
                color = {'r': 255, 'g': 255, 'b': 255, 'a': 255}
                self.colors.append(color)
        self.texcoords = []
        if texcoords:
            for i in range(4):
                texcoord = {'x': texcoords[i*2], 'y': texcoords[i*2+1]}
                self.texcoords.append(texcoord)
            texcoords = []
        else:
            texcoord = [{'x': 0, 'y': 0}, {'x': 1<<10, 'y': 0},
                       {'x': 0, 'y': 1<<10}, {'x': 1<<10, 'y': 1<<10}]
            self.texcoords.extend(texcoord)
        self.pos_env = pos_env
        self.pos_env_offset = pos_env_offset
        self.color_env = color_env
        self.color_env_offset = color_env_offset

    def __repr__(self):
        return '<Quad {0} {1}>'.format(self.pos_env, self.color_env)

class Tile(object):
    """Represents a tile of a tilelayer."""

    def __init__(self, index=0, flags=0, skip=0, reserved=0):
        self.index = index
        self._flags = flags
        self.skip = skip
        self.reserved = reserved

    @property
    def vflip(self):
        return self._flags & 1 != 0

    @vflip.setter
    def vflip(self, value):
        if value:
            self._flags |= 1
        else:
            if self.vflip:
                self._flags ^= 1

    @property
    def hflip(self):
        return self._flags & 2 != 0

    @hflip.setter
    def hflip(self, value):
        if value:
            self._flags |= 2
        else:
            if self.hflip:
                self._flags ^= 2

    def __repr__(self):
        return '<Tile {0}>'.format(self.index)

class TileTele(object):
    """Represents an overlay tile with teleport data."""

    def __init__(self, number=0, type=0):
        self.number = number
        self.type = type

    """@property
    def telein(self):
        return self.number > 0 and self.type == 26

    @property
    def teleout(self):
        return self.number > 0 and self.type == 27

    @property
    def number(self):
        return self.number

    @telein.setter
    def telein(self, value):
        if value:
            self.type = 26

    @teleout.setter
    def teleout(self, value):
        if value:
            self.type = 27

    @number.setter
    def number(self, value):
        self.number = max(0, min(value, 255))"""

class TileSpeedup(object):
    """Represents an overlay tile with speedup data."""

    def __init__(self, force=0, angle=0):
        self.force = force
        self.angle = angle

    """@property
    def force(self):
        return self.force

    @property
    def angle(self):
        return self.angle

    @force.setter
    def force(self, value):
        self.force = max(0, min(value, 255))

    @angle.setter
    def angle(self, value):
        self.angle = max(0, min(value, 359))"""

class Image(object):

    type_size = 6 # size in ints

    def __init__(self, teemap, f, item):
        self.teemap = teemap
        item_size, item_data = item
        fmt = '{0}i'.format(item_size/4)
        item_data = unpack(fmt, item_data)
        version, self.width, self.height, self.external_, image_name, \
        image_data = item_data[:Image.type_size]
        self._get_image_name(f, image_name)

        # load image data
        if self.external_ != 0 and image_data > -1:
            self._get_image_data(f, image_data)

    def _get_image_name(self, f, image_name):
        self.name = decompress(self.teemap.get_compressed_data(f, image_name))
        self.name = self.name[:-1] # remove 0 termination

    def _get_image_data(self, f, image_data):
        self.image_data = decompress(self.teemap.get_compressed_data(f, 
                            image_data))

    def __repr__(self):
        return '<Image {0}>'.format(self.name)

    @property
    def resolution(self):
        return '{0} x {1}'.format(self.width, self.height)

    @property
    def external(self):
        if self.external_:
            return True
        return False

class Envelope(object):
    """Represents an envelope."""

    type_size = 12

    def __init__(self, teemap, f, item):
        self.teemap = teemap
        item_size, item_data = item
        fmt = '{0}i'.format(item_size/4)
        item_data = unpack(fmt, item_data)
        self.version, self.channels, start_point, \
        num_points = item_data[:Envelope.type_size-8] # -8 to strip envelope name
        self.name = ints_to_string(item_data[4:Envelope.type_size])

        # assign envpoints
        self._assign_envpoints(start_point, num_points)

    def _assign_envpoints(self, start, num):
        self.envpoints = []
        self.envpoints.extend(self.teemap.envpoints[start:start+num])
    
    def __repr__(self):
        return '<Envelope ({0})>'.format(len(self.envpoints))

class Envpoint(object):
    """Represents an envpoint."""

    type_size = 6
    def __init__(self, teemap, point):
        self.teemap = teemap
        self.time, self.curvetype = point[:Envpoint.type_size-4] # -4 to strip values
        self.values = point[2:Envpoint.type_size]

    def __repr__(self):
        return '<Envpoint>'.format()

class Group(object):
    """Represents a group."""

    type_size = 15

    def __init__(self, teemap, f, item):
        self.teemap = teemap
        item_size, item_data = item
        fmt = '{0}i'.format(item_size/4)
        item_data = unpack(fmt, item_data)
        version, self.offset_x, self.offset_y, self.parallax_x, \
        self.parallax_y, start_layer, num_layers, self.use_clipping, \
        self.clip_x, self.clip_y, self.clip_w, self.clip_h = item_data[:Group.type_size-3] # group name
        self.name = None
        if version >= 3:
            name = ints_to_string(item_data[Group.type_size-3:Group.type_size])
            if name:
                self.name = name
        self.layers = []

    def add_layer(self, layer):
        self.layers.append(layer)

    def __repr__(self):
        return '<Group>'

class Layer(object):
    """Represents the layer data every layer has."""

    type_size = 3

    def __init__(self, teemap, f, item):
        self.teemap = teemap
        item_size, item_data = item
        fmt = '{0}i'.format(item_size/4)
        item_data = unpack(fmt, item_data)
        self.version, self.type, self.flags = item_data[:Layer.type_size]

class QuadLayer(Layer):
    """Represents a quad layer."""

    type_size = 10

    def __init__(self, teemap, f, item):
        self.teemap = teemap
        item_size, item_data = item
        fmt = '{0}i'.format(item_size/4)
        item_data = unpack(fmt, item_data)
        super(QuadLayer, self).__init__(teemap, f, item)
        version, self.num_quads, data, self._image = item_data[3:QuadLayer.type_size-3] # layer name
        self.name = None
        if version >= 2:
            name = ints_to_string(item_data[QuadLayer.type_size-3:QuadLayer.type_size])
            if name:
                self.name = name
        self.quads = []

        # load quads
        self._load_quads(f, data)

    def _load_quads(self, f, data):
        quad_data = decompress(self.teemap.get_compressed_data(f, data))
        fmt = '{0}i'.format(len(quad_data)/4)
        quad_data = unpack(fmt, quad_data)
        self.quads = []
        i = 0
        while(i < len(quad_data)):
            self.quads.append(Quad(quad_data[i:i+10], quad_data[i+10:i+26],
                                   quad_data[i+26:i+34], quad_data[i+34],
                                   quad_data[i+35], quad_data[i+36],
                                   quad_data[i+37]))
            i += 38

    @property
    def image(self):
        if self._image > -1:
            return self.teemap.images[self._image]
        return None

    def __repr__(self):
        return '<Quad layer ({0})>'.format(self.num_quads)

class TileLayer(Layer):
    """Represents a tile layer."""

    type_size = 18

    def __init__(self, teemap, f, item):
        self.teemap = teemap
        item_size, item_data = item
        fmt = '{0}i'.format(item_size/4)
        item_data = unpack(fmt, item_data)
        super(TileLayer, self).__init__(teemap, f, item)
        self.color = {'r': 0, 'g': 0, 'b': 0, 'a': 0}
        version, self.width, self.height, self.game, self.color['r'], \
        self.color['g'], self.color['b'], self.color['a'], self.color_env, \
        self.color_env_offset, self._image, data = item_data[3:TileLayer.type_size-3] # layer name
        self.name = None
        if version >= 3:
            name = ints_to_string(item_data[TileLayer.type_size-3:TileLayer.type_size])
            if name:
                self.name = name

        # load tile data
        self._load_tiles(f, data)

    def _load_tiles(self, f, data):
        tile_data = decompress(self.teemap.get_compressed_data(f, data))
        fmt = '{0}B'.format(len(tile_data))
        tile_data = unpack(fmt, tile_data)
        self.tiles = []
        i = 0
        while(i < len(tile_data)):
            self.tiles.append(Tile(*tile_data[i:i+4]))
            i += 4

    @property
    def image(self):
        if self._image > -1:
            return self.teemap.images[self._image]
        return None

    @property
    def is_gamelayer(self):
        return self.game == 1

    def __repr__(self):
        if self.game == 1:
            return '<Game layer ({0}x{1})>'.format(self.width, self.height)
        return '<Tile layer ({0}x{1})>'.format(self.width, self.height)
