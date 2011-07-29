# -*- coding: utf-8 -*-
"""
    Collection of different items.

    :copyright: 2010-2011 by the TML Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""

import os
import shutil
from StringIO import StringIO
from struct import unpack, pack
import warnings
from zlib import decompress

import png

from constants import ITEM_TYPES, LAYER_TYPES, TML_DIR, TILEFLAG_VFLIP, \
     TILEFLAG_HFLIP, TILEFLAG_OPAQUE, TILEFLAG_ROTATE
from utils import ints_to_string

#GAMELAYER_IMAGE = PIL.Image.open(os.path.join(TML_DIR,
#	os.extsep.join(('entities', 'png'))))

class Info(object):
    """Represents a map info object."""

    type_size = 6

    def __init__(self, author=None, map_version=None, credits=None, license=None):
        self.author = author
        self.map_version = map_version
        self.credits = credits
        self.license = license

    def __repr__(self):
        return '<MapInfo ({0})>'.format(self.author or 'None')

class Image(object):
    """Represents an image."""

    # size in ints
    type_size = 6

    def __init__(self, name, width=0, height=0, external=False, data=None,
                 path=''):
        self.name = name
        self.data = data
        self.width = width
        self.height = height
        self.external = external
        if external is True:
            png_path = os.sep.join([TML_DIR, 'mapres', self.name])
            png_path = os.extsep.join([png_path, 'png'])
        else:
            png_path = path

        if data is None:
            try:
                png.Reader(png_path).asRGBA()
            except png.Error:
                warnings.warn('Image is not in RGBA format')
            except IOError:
                warnings.warn('External image "%s" does not exist' % self.name)

    def save(self, dest):
        """Saves the image to the given path.

        :param dest: Path to the image

        """
        if self.external:
            src = os.sep.join([TML_DIR, 'mapres', self.name])
            src = os.extsep.join([src, 'png'])
            if not os.path.exists(src):
                raise ValueError('External image "%s" does not exist' % self.name)
            shutil.copyfile(src, dest)
        else:
            image = open(dest, 'wb')
            png_writer = png.Writer(width=self.width, height=self.height, alpha=True)
            fmt = '{0}B'.format(len(self.data))
            image_data = unpack(fmt, self.data)
            png_writer.write_array(image, image_data)
            image.close()

    def __repr__(self):
        return '<Image ({0})>'.format(self.name)

    @property
    def resolution(self):
        return '{0} x {1}'.format(self.width, self.height)

class Envelope(object):
    """Represents an envelope."""

    type_size = 12

    def __init__(self, name=None, version=None, channels=None, envpoints=None):
        self.name = name
        self.version = version
        self.channels = channels
        self.envpoints = envpoints

    def __repr__(self):
        return '<Envelope ({0})>'.format(self.name or len(self.envpoints))

class Envpoint(object):
    """Represents an envpoint."""

    type_size = 6
    def __init__(self, time=None, curvetype=None, values=None):
        self.time = time
        self.curvetype = curvetype
        self.values = values or []

    def __repr__(self):
        return '<Envpoint ({0})>'.format(self.time)

class Group(object):
    """Represents a group."""

    type_size = 15

    def __init__(self, name=None, offset_x=None, offset_y=None,
                 parallax_x=None, parallax_y=None, use_clipping=None,
                 clip_x=None, clip_y=None, clip_w=None, clip_h=None,
                 layers=None):
        self.name = name
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.parallax_x = parallax_x
        self.parallax_y = parallax_y
        self.use_clipping = use_clipping
        self.clip_x = clip_x
        self.clip_y = clip_y
        self.clip_w = clip_w
        self.clip_h = clip_h
        if layers is not None:
            if not isinstance(layers, list):
                raise TypeError('Param "layers" must be a list.')
            for layer in layers:
                if not isinstance(layer, Layer):
                    raise TypeError('The "layers" list can only contain layers.')
        self.layers = layers or []

    def append(self, layer):
        """Adds a layer to the group.

        :param layer: Layer to append.
        :raises: TypeError

        """
        if not isinstance(layer, Layer):
            raise TypeError('You can only append layers.')
        self.layers.append(layer)

    def __repr__(self):
        return '<Group ({0})>'.format(len(self.self.layers))

class Layer(object):
    """Represents the layer data every layer has."""

    type_size = 3

    @property
    def is_gamelayer(self):
        return False

    @property
    def is_telelayer(self):
        return False

    @property
    def is_speeduplayer(self):
        return False

class TileLayer(Layer):
    """Represents a tilelayer.

    :param width: Default: 50
    :param height: Default: 50
    :param name: Default: 'Tiles'
    :param game: 1 if it should be the gamelayer. Default: 0
    :param color: Tupel with four values for r, g, b, a
                  Default: (255, 255, 255, 255)
    :param color_env: Default: -1
    :param color_env_offset: Default: 0
    :param image_id: Default: -1
    :param tiles: Initial TileManager, used internally
    :param tele_tiles: For race modification
    :param speedup_tiles: For race modification

    """

    type_size = 18

    def __init__(self, width=50, height=50, name='Tiles', game=0,
                 color=(255, 255, 255, 255), color_env=-1, color_env_offset=0,
                 image_id=-1, tiles=None, tele_tiles=None, speedup_tiles=None):
        self.name = name
        self.color = color
        self.width = width
        self.height = height
        self.game = game
        self.color_env = color_env
        self.color_env_offset = color_env_offset
        self.image_id = image_id
        self.tiles = tiles or TileManager(width * height)
        self.tele_tiles = tele_tiles or TileManager(width * height, _type=1)
        self.speedup_tiles = speedup_tiles or TileManager(width * height, _type=2)

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
        """Select an area of the tilelayer.

        Creates a new TileLayer of the section you are selecting. If you are
        selecting over the borders, it will just cut your selection to fit to
        the layer.

        :param x: x-position
        :param y: y-position
        :param w: width, default: 1
        :param h: height, default: 1
        :returns: TileLayer

        """

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
        if self.is_gamelayer():
            return '<Game layer ({0}x{1})>'.format(self.width, self.height)
        elif self.is_telelayer() and self.tele_tiles:
            return '<Tele layer ({0}x{1})>'.format(self.width, self.height)
        elif self.is_speeduplayer() and self.speedup_tiles:
            return '<Speedup layer ({0}x{1})>'.format(self.width, self.height)
        return '<Tilelayer ({0}x{1})>'.format(self.width, self.height)

class QuadLayer(Layer):
    """Represents a quadlayer.

    :param name: Name of the layer, default 'Quads'
    :param image_id: ID of the related image, default -1
    :param quads: Initial QuadManager, used internally

    """

    type_size = 10

    def __init__(self, name='Quads', image_id=-1, quads=None):
        self.name = name
        self.image_id = image_id
        self.quads = quads or QuadManager()

    def __repr__(self):
        return '<Quadlayer ({0})>'.format(len(self.quads))

class QuadManager(object):
    """Handles quads while sparing memory.

    Keeps track of quds as simple strings, but returns a Quad class on demand.

    :param quads: List of quads to put in.
    :param data: Raw quad data, used internally.
    """

    def __init__(self, quads=None, data=None):
        self.quads = []
        if quads:
            self.quads = [self._quad_to_string(quad) for quad in quads]
        elif data:
            self.quads.extend(data)

    def __getitem__(self, value):
        if isinstance(value, slice):
            return QuadManager(self.quads[value])
        return self._string_to_quad(self.quads[value])

    def __setitem__(self, k, v):
        if not isinstance(v, Quad):
            raise TypeError('You can only assign Quad objects.')
        self.quads[k] = self._quad_to_string(v)

    def __len__(self):
        return len(self.quads)

    def pop(self, value):
        return self._string_to_quad(self.quads.pop(value))

    def append(self, value):
        self.quads.append(self._quad_to_string(value))

    def _quad_to_string(self, quad):
        data = []
        for point in quad.points:
            data.extend(point)
        for color in quad.colors:
            data.extend(color)
        for texcoord in quad.texcoords:
            data.extend(texcoord)
        data.extend([quad.pos_env, quad.pos_env_offset, quad.color_env,
                     quad.color_env_offset])
        return pack('38i', *data)

    def _string_to_quad(self, string):
        quad_data = string
        points = []
        for l in range(5):
            points.append(unpack('2i', quad_data[l*8:l*8+8]))
        colors = []
        for l in range(4):
            colors.append(unpack('4i', quad_data[40+l*16:40+l*16+16]))
        texcoords = []
        for l in range(4):
            texcoords.append(unpack('2i', quad_data[104+l*8:104+l*8+8]))
        pos_env, pos_env_offset, color_env, color_env_offset = unpack('4i',
                                                            quad_data[136:152])
        return Quad(pos_env=pos_env, pos_env_offset=pos_env_offset,
                    color_env=color_env, color_env_offset=color_env_offset,
                    points=points, colors=colors, texcoords=texcoords)
class Quad(object):
    """Represents a quad of a quadlayer.

    :param pos_env: Default: -1
    :param pos_env_offset: Default: 0
    :param color_env: Default: -1
    :param color_env_offset: Default: 0
    :param points: List of tuples with point coordinates. Default:
                   [(0, 0), (64, 0), (0, 64), (64, 64), (32, 32)]
    :param colors: List of tuples with color vallues. Default:
                   [(255, 255, 255, 255), (255, 255, 255, 255),
                    (255, 255, 255, 255), (255, 255, 255, 255)]
    :param texcoords: List of tuples with texcoords. Default:
                      [(0, 0), (1024, 0), (0, 1024), (1024, 1024)]

    """

    def __init__(self, pos_env=-1, pos_env_offset=0, color_env=-1,
                 color_env_offset=0, points=None, colors=None, texcoords=None):
        self.pos_env = pos_env
        self.pos_env_offset = pos_env_offset
        self.color_env = color_env
        self.color_env_offset = color_env_offset
        self.points = points or [(0, 0), (64, 0), (0, 64), (64, 64), (32, 32)]
        self.colors = colors or [(255, 255, 255, 255)] * 4
        self.texcoords = texcoords or [(0, 0), (1024, 0), (0, 1024), (1024, 1024)]

    def __repr__(self):
        return '<Quad ({0}:{1})>'.format(*self.points[4])

    def __eq__(self, other):
        if not isinstance(other, Quad):
            return False
        return self.pos_env == other.pos_env and \
               self.pos_env_offset == other.pos_env_offset and \
               self.color_env == other.color_env and \
               self.color_env_offset == other.color_env_offset and \
               self.points == other.points and \
               self.colors == other.colors and \
               self.texcoords == other.texcoords

class TileManager(object):
    """Handles tiles while sparing memory.

    Keeps track of tiles as simple strings, but returns a Tile class on demand.

    :param size: Fill up the manager with n empty tiles.
    :param tiles: List of tiles to put in.
    :param _type: Used for a race modification, you probably don't need it
    """

    def __init__(self, size=0, tiles=None, data=None, _type=0):
        self.type = _type
        if tiles is not None:
            #TODO: convert Tiles to string
            self.tiles = tiles
        elif data is not None:
            self.tiles = data
        else:
            self.tiles = ['\x00\x00\x00\x00'] * size

    def __getitem__(self, value):
        if isinstance(value, slice):
            return TileManager(tiles=self.tiles[value])
        if self.type == 1:
            return TeleTile(self.tiles[value])
        elif self.type == 2:
            return SpeedupTile(self.tiles[value])
        return self._string_to_tile(self.tiles[value])

    def __setitem__(self, k, v):
        if isinstance(v, Tile):
            self.tiles[k] = self._tile_to_string(v)
        elif isinstance(v, str):
            if len(v) != 4:
                raise ValueError('The string must be exactly 4 chars long.')
            self.tiles[k] = v
        else:
            raise TypeError('You can only assign Tile or string objects.')

    def __len__(self):
        return len(self.tiles)

    def _tile_to_string(self, tile):
        return pack('4B', tile.index, tile._flags, tile.skip, tile.reserved)

    def _string_to_tile(self, string):
        index, flags, skip, reserved = unpack('4B', string)
        return Tile(index=index, flags=flags, skip=skip, reserved=reserved)

class Tile(object):
    """Represents a tile of a tilelayer.

    :param index: Default: 0
    :param flags: Default: 0
    :param skip: Default: 0
    :param reserved: Default: 0

    """

    def __init__(self, index=0, flags=0, skip=0, reserved=0):
        self.index = index
        self._flags = flags
        self.skip = skip
        self.reserved = reserved

    def vflip(self):
        """Flip the tile in vertical direction"""
        if self.flags['rotation']:
            self._flags ^= TILEFLAG_HFLIP
        else:
            self._flags ^= TILEFLAG_VFLIP

    def hflip(self):
        """Flip the tile in horizontal direction"""
        if self.flags['rotation']:
            self._flags ^= TILEFLAG_VFLIP
        else:
            self._flags ^= TILEFLAG_HFLIP

    def rotate(self, value):
        """Rotate the tile.

        :param value: Rotationdirection, can be '(l)eft' or '(r)ight'
        :type value: str
        :raises: ValueError

        """
        if value.lower() in ('r', 'right'):
            if self.flags['rotation']:
                self._flags ^= (TILEFLAG_HFLIP|TILEFLAG_VFLIP)
            self._flags ^= TILEFLAG_ROTATE
        elif value.lower() in ('l', 'left'):
            if self.flags['rotation']:
                self._flags ^= (TILEFLAG_HFLIP|TILEFLAG_VFLIP)
            self._flags ^= TILEFLAG_ROTATE
            self.vflip()
            self.hflip()
        else:
            raise ValueError('You can only rotate (l)eft or (r)ight.')

    @property
    def coords(self):
        """Coordinates of the tile in the mapres.

        :returns: (x, y)

        """
        return (self.index % 16, self.index / 16)

    @property
    def flags(self):
        """Gives the flags of the tile.

        The flags contain the rotation, hflip and vflip information.

        :returns: {'rotation': int, 'vflip': int, 'hflip': int}

        """
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
    """Represents a tele tile of a tilelayer. Only for race modification."""

    def __init__(self, data):
        self.number, self.type = unpack('2B', data)

    def __repr__(self):
        return '<TeleTile ({0})>'.format(self.number)

class SpeedupTile(object):
    """Represents a speedup tile of a tilelayer. Only for race modification."""

    def __init__(self, data):
        self.force, self.angle = unpack('Bh', data)

    def __repr__(self):
        return '<SpeedupTile ({0})>'.format(self.index)
