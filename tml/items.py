# -*- coding: utf-8 -*-
"""
    Collection of different items.

    :copyright: 2010-2011 by the TML Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""

import os
import png
from StringIO import StringIO
from struct import unpack, pack
from utils import ints_to_string
import warnings
from zlib import decompress

from constants import ITEM_TYPES, LAYER_TYPES, TML_DIR, TILEFLAG_VFLIP, \
     TILEFLAG_HFLIP, TILEFLAG_OPAQUE, TILEFLAG_ROTATE

#GAMELAYER_IMAGE = PIL.Image.open(os.path.join(TML_DIR,
#	os.extsep.join(('entities', 'png'))))

class Info(object):
    """Represents a map info object."""

    type_size = 6

    def __init__(self, teemap, f, item):
        item_size, item_data = item
        fmt = '{0}i'.format(item_size/4)
        item_data = unpack(fmt, item_data)
        version, self.author, self.map_version, self.credits, self.license, \
        self.settings = item_data[:Info.type_size]
        for type_ in ('author', 'map_version', 'credits', 'license'):
            if getattr(self, type_) > -1:
                setattr(self, type_, decompress(teemap.get_compressed_data(f, getattr(self, type_)))[:-1])
            else:
                setattr(self, type_, None)
        # load server settings
        if self.settings > -1:
            self.settings = decompress(teemap.get_compressed_data(f, self.settings)).split('\x00')[:-1]

    def __repr__(self):
        return '<MapInfo ({0})>'.format(self.author or 'None')

class Image(object):
    """Represents an image."""

    # size in ints
    type_size = 6

    def __init__(self, teemap, f, item):
        self.teemap = teemap
        item_size, item_data = item
        fmt = '{0}i'.format(item_size/4)
        item_data = unpack(fmt, item_data)
        version, self.width, self.height, self.external_, image_name, \
        image_data = item_data[:Image.type_size]
        self._get_image_name(f, image_name)

        # load image data
        if self.external_ == 0:
            self._get_image_data(f, image_data)
        else:
            try:
                png_path = os.sep.join([TML_DIR, 'mapres', self.name])
                png_path = os.extsep.join([png_path, 'png'])
                png.Reader(png_path).asRGBA()
            except png.Error:
                warnings.warn('Image is not in RGBA format')
            except IOError:
                warnings.warn('External image „%s“ does not exist' % self.name)

    def _get_image_name(self, f, image_name):
        self.name = decompress(self.teemap.get_compressed_data(f, image_name))
        self.name = self.name[:-1] # remove 0 termination

    def _get_image_data(self, f, image_data):
        self.image_data = decompress(self.teemap.get_compressed_data(f,
                            image_data))

    def save(self):
        if self.external_:
            return
        png_path = os.sep.join([TML_DIR, 'custom_mapres', self.name])
        png_path = os.extsep.join([png_path, 'png'])
        image = open(png_path, 'wb')
        png_writer = png.Writer(width=self.width, height=self.height, alpha=True)
        fmt = '{0}B'.format(len(self.image_data))
        image_data = unpack(fmt, self.image_data)
        png_writer.write_array(image, image_data)
        image.close()

    def __repr__(self):
        return '<Image ({0})>'.format(self.name)

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

        self._assign_envpoints(start_point, num_points)

    def _assign_envpoints(self, start, num):
        self.envpoints = []
        self.envpoints.extend(self.teemap.envpoints[start:start+num])

    def __repr__(self):
        return '<Envelope ({0})>'.format(self_name or len(self.envpoints))

class Envpoint(object):
    """Represents an envpoint."""

    type_size = 6
    def __init__(self, teemap, point):
        self.teemap = teemap
        self.time, self.curvetype = point[:Envpoint.type_size-4] # -4 to strip values
        self.values = list(point[2:Envpoint.type_size])

    def __repr__(self):
        return '<Envpoint ({0})>'.format(self.time)

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
        return '<Group ({0})>'.format(len(self.self.layers))

class Layer(object):
    """Represents the layer data every layer has."""

    type_size = 3

    def __init__(self, f=None, item=None, data=None):
        if f and item:
            item_size, item_data = item
            fmt = '{0}i'.format(item_size/4)
            data = unpack(fmt, item_data)[:Layer.type_size]
        self.version, self.type, self.flags = data

    @property
    def is_gamelayer(self):
        return False

    @property
    def is_telelayer(self):
        return False

    @property
    def is_speeduplayer(self):
        return False

class QuadManager(object):

    def __init__(self, quads=None):
        self.quads = []
        if quads:
            self.quads = quads

    def __getitem__(self, value):
        if isinstance(value, slice):
            return QuadManager(self.quads[value])
        return Quad(self.quads[value])

    def __len__(self):
        return len(self.quads)

    def append(self, value):
        self.quads.append(value)

class Quad(object):
    """Represents a quad of a quadlayer."""

    def __init__(self, data):
        points = []
        for i in range(5):
            points.append(unpack('2i', data[i*8:i*8+8]))
        colors = []
        for i in range(4):
            colors.append(unpack('4i', data[40+i*16:40+i*16+16]))
        texcoords = []
        for i in range(4):
            texcoords.append(unpack('2i', data[104+i*8:104+i*8+8]))
        self.pos_env = unpack('i', data[136:140])[0]
        self.pos_env_offset = unpack('i', data[140:144])[0]
        self.color_env = unpack('i', data[144:148])[0]
        self.color_env_offset = unpack('i', data[148:152])[0]
        self.points = []
        for point in points:
            self.points.append({'x': point[0], 'y': point[1]})
        self.colors = []
        for color in colors:
            self.colors.append({'r': color[0], 'g': color[1],
                                'b': color[2], 'a': color[3]})
        self.texcoords = []
        for texcoord in texcoords:
            self.texcoords.append({'x': texcoord[0], 'y': texcoord[1]})

    def __repr__(self):
        return '<Quad ({0}:{1})>'.format(*self.points[4])

class TileManager(object):

    def __init__(self, size=0, _type=0, tiles=None):
        self.type = _type
        if tiles:
            self.tiles = tiles
        else:
            self.tiles = ['\x00\x00\x00\x00'] * size

    def __getitem__(self, value):
        if isinstance(value, slice):
            return TileManager(tiles=self.tiles[value])
        if self.type == 1:
            return TeleTile(self.tiles[value])
        elif self.type == 2:
            return SpeedupTile(self.tiles[value])
        return Tile(self.tiles[value])

    def __setitem__(self, k, v):
        if isinstance(v, Tile):
            self.tiles[k] = pack('4B', v.index, v._flags, v.skip, v.reserved)
        elif isinstance(v, str):
            if len(v) != 4:
                raise ValueError('The string must be exactly 4 chars long.')
            self.tiles[k] = v
        else:
            raise TypeError('You can only assign Tile or string objects.')

    def __len__(self):
        return len(self.tiles)

    def append(self, value):
        self.tiles.append(value)

class Tile(object):
    """Represents a tile of a tilelayer."""

    def __init__(self, data=None):
        if data is not None:
            self.index, self._flags, self.skip, self.reserved = unpack('4B', data)
        else:
            self.index = self._flags = self.skip = self.reserved = 0

    def vflip(self):
        if self.flags['rotation']:
            self._flags ^= TILEFLAG_HFLIP
        else:
            self._flags ^= TILEFLAG_VFLIP

    def hflip(self):
        if self.flags['rotation']:
            self._flags ^= TILEFLAG_VFLIP
        else:
            self._flags ^= TILEFLAG_HFLIP

    def rotation(self, value):
        if value == 'r':
            if self.flags['rotation']:
                self._flags ^= (TILEFLAG_HFLIP|TILEFLAG_VFLIP)
            self._flags ^= TILEFLAG_ROTATE
        elif value == 'l':
            if self.flags['rotation']:
                self._flags ^= (TILEFLAG_HFLIP|TILEFLAG_VFLIP)
            self._flags ^= TILEFLAG_ROTATE
            self.vflip()
            self.hflip()
        else:
            raise ValueError('You can only rotate left (\'l\') and right (\'r\')')

    @property
    def coords(self):
        return self.index % 16, self.index / 16

    @property
    def flags(self):
        return {'rotation': self._flags & TILEFLAG_ROTATE != 0,
                'vflip': self._flags & TILEFLAG_VFLIP != 0,
                'hflip': self._flags & TILEFLAG_HFLIP != 0}

    def __repr__(self):
        return '<Tile ({0})>'.format(self.index)

    def __eq__(self, other):
        if not isinstance(other, Tile):
            return False
        return self.index == other.index and self.flags == other.flags and \
           self.skip == other.skip and self.reserved == other.reserved

class TeleTile(object):
    """Represents a tele tile of a tilelayer."""

    def __init__(self, data):
        self.number, self.type = unpack('2B', data)

    def __repr__(self):
        return '<TeleTile ({0})>'.format(self.number)

class SpeedupTile(object):
    """Represents a speedup tile of a tilelayer."""

    def __init__(self, data):
        self.force, self.angle = unpack('Bh', data)

    def __repr__(self):
        return '<SpeedupTile ({0})>'.format(self.index)

class QuadLayer(Layer):
    """Represents a quad layer."""

    type_size = 10

    def __init__(self, teemap=None, f=None, item=None):
        item_size, item_data = item
        fmt = '{0}i'.format(item_size/4)
        item_data = unpack(fmt, item_data)
        super(QuadLayer, self).__init__(f, item)
        version, self.num_quads, data, self.image_id = item_data[3:QuadLayer.type_size-3] # layer name
        self.name = None
        if version >= 2:
            name = ints_to_string(item_data[QuadLayer.type_size-3:QuadLayer.type_size])
            if name:
                self.name = name

        if teemap is not None:
            self._load_quads(teemap, f, data)

    def _load_from_file(self, teemap, f, item):
        pass

    def _load_quads(self, teemap, f, data):
        quad_data = decompress(teemap.get_compressed_data(f, data))
        self.quads = QuadManager()
        i = 0
        while(i < len(quad_data)):
            self.quads.append((quad_data[i:i+152]))
            i += 152

    def __repr__(self):
        return '<Quad layer ({0})>'.format(self.num_quads)

class TileLayer(Layer):
    """Represents a tile layer."""

    type_size = 18

    def __init__(self, width=50, height=50, teemap=None, f=None, item=None):
        self.name = None
        self.color = {'r': 255, 'g': 255, 'b': 255, 'a': 255}
        self.width, self.height, self.game, self.color_env, \
        self.color_env_offset, self.image_id = width, height, 0, -1, 0, -1
        self.tiles = TileManager()
        self.tele_tiles = TileManager(_type=1)
        self.speedup_tiles = TileManager(_type=2)
        if teemap and f and item:
            self._load_from_file(teemap, f, item)
        else:
            super(TileLayer, self).__init__(data=(0, 2, 0))
            self.tiles = TileManager(width * height)

    def _load_from_file(self, teemap, f, item):
        item_size, item_data = item
        fmt = '{0}i'.format(item_size/4)
        item_data = unpack(fmt, item_data)
        super(TileLayer, self).__init__(f=f, item=item)
        version, self.width, self.height, self.game, self.color['r'], \
        self.color['g'], self.color['b'], self.color['a'], self.color_env, \
        self.color_env_offset, self.image_id, data = item_data[3:TileLayer.type_size-3] # layer name
        if version >= 3:
            name = ints_to_string(item_data[TileLayer.type_size-3:TileLayer.type_size])
            if name:
                self.name = name
        self._load_tiles(teemap, f, data)
        self._load_tele_tiles(teemap, f, item_data, version)
        self._load_speedup_tiles(teemap, f, item_data, version)

    def _load_tiles(self, teemap, f, data):
        tile_data = decompress(teemap.get_compressed_data(f, data))
        i = 0
        while(i < len(tile_data)):
            self.tiles.append(tile_data[i:i+4])
            i += 4

    def _load_tele_tiles(self, teemap, f, item_data, version):
        if self.is_telelayer:
            if version >= 3:
                # num of tele data is right after the default type length
                if len(item_data) > TileLayer.type_size: # some security
                    tele_data = item_data[TileLayer.type_size]
                    if tele_data > -1 and tele_data < teemap.header.num_raw_data:
                        tele_data = decompress(teemap.get_compressed_data(f, tele_data))
                        i = 0
                        while(i < len(tele_data)):
                            self.tele_tiles.append(tele_data[i:i+2])
                            i += 2
            else:
                # num of tele data is right after num of data for old maps
                if len(item_data) > TileLayer.type_size-3: # some security
                    tele_data = item_data[TileLayer.type_size-3]
                    if tele_data > -1 and tele_data < teemap.header.num_raw_data:
                        tele_data = decompress(teemap.get_compressed_data(f, tele_data))
                        i = 0
                        while(i < len(tele_data)):
                            self.tele_tiles.append(tele_data[i:i+2])
                            i += 2

    def _load_speedup_tiles(self, teemap, f, item_data, version):
        if self.is_speeduplayer:
            if version >= 3:
                # num of speedup data is right after tele data
                if len(item_data) > TileLayer.type_size+1: # some security
                    speedup_data = item_data[TileLayer.type_size+1]
                    if speedup_data > -1 and speedup_data < teemap.header.num_raw_data:
                        speedup_data = decompress(teemap.get_compressed_data(f, speedup_data))
                        i = 0
                        while(i < len(speedup_data)):
                            self.speedup_tiles.append(speedup_data[i:i+4])
                            i += 4
            else:
                # num of speedup data is right after tele data
                if len(item_data) > TileLayer.type_size-2: # some security
                    speedup_data = item_data[TileLayer.type_size-2]
                    if speedup_data > -1 and speedup_data < teemap.header.num_raw_data:
                        speedup_data = decompress(teemap.get_compressed_data(f, speedup_data))
                        i = 0
                        while(i < len(speedup_data)):
                            self.speedup_tiles.append(speedup_data[i:i+4])
                            i += 4

    def _get_tile(self, tiles, x, y):
        x = max(0, min(x, self.width-1))
        y = max(0, min(y, self.height-1))
        return tiles[y*self.width+x]

    def get_tile(self, x, y):
        return self._get_tile(self.tiles, x, y)

    def get_tele_tile(self, x, y):
        return self._get_tile(self.tele_tiles, x, y)

    def get_speedup_tile(self, x, y):
        return self._get_tile(self.speedup_tiles, x, y)

    def select(self, x, y, w=1, h=1):
        x = max(0, min(x, self.width-1))
        y = max(0, min(y, self.height-1))
        w = max(1, min(w, self.width-x))
        h = max(1, min(h, self.height-y))
        layer = TileLayer(w, h)
        layer.color = self.color
        layer.game = self.game
        for _y in range(h):
            for _x in range(w):
                layer.tiles[_y * w + _x] = self.tiles.tiles[(y+_y)*self.width+(x+_x)]
        if len(self.tele_tiles.tiles) == len(self.tiles.tiles):
            for _y in range(h):
                for _x in range(w):
                    layer.tele_tiles[_y * w + _x] = self.tele_tiles.tiles[(y+_y)*self.width+(x+_x)]
        if len(self.speedup_tiles.tiles) == len(self.tiles.tiles):
            for _y in range(h):
                for _x in range(w):
                    layer.speedup_tiles[_y * w + _x] = self.speedup_tiles.tiles[(y+_y)*self.width+(x+_x)]
        return layer

    @property
    def is_gamelayer(self):
        return self.game == 1

    @property
    def is_telelayer(self):
        return self.game == 2

    @property
    def is_speeduplayer(self):
        return self.game == 4

    def __repr__(self):
        if self.game == 1:
            return '<Game layer ({0}x{1})>'.format(self.width, self.height)
        elif self.game == 2 and self.tele_tiles:
            return '<Tele layer ({0}x{1})>'.format(self.width, self.height)
        elif self.game == 4 and self.speedup_tiles:
            return '<Speedup layer ({0}x{1})>'.format(self.width, self.height)
        return '<Tile layer ({0}x{1})>'.format(self.width, self.height)
