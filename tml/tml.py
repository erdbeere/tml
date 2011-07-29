#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A library which makes it possible to read teeworlds map files.

    :copyright: 2010-2011 by the TML Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""
from constants import *
from datafile import DataFileReader

class Teemap(object):
    """Representation of a teeworlds map.

    All information about the map can be accessed through this class.

    :param map_path: Path to the teeworlds mapfile.
    """

    @staticmethod
    def check(map_path):
        try:
            path, filename = os.path.split(map_path)
            name, extension = os.path.splitext(filename)
            if extension == '':
                map_path = os.extsep.join([map_path, 'map'])
            elif extension != ''.join([os.extsep, 'map']):
                raise TypeError('Invalid file')
            with open(map_path, 'rb') as f:
                sig = ''.join(unpack('4c', f.read(4)))
                if sig not in ('DATA', 'ATAD'):
                    raise TypeError('Invalid signature')
                version = unpack('i', f.read(4))[0]

                if version != 4:
                    raise TypeError('Wrong version')
            return True
        except TypeError as error:
            print 'No valid mapfile ({0})'.format(error.message)
            return False
        except IOError as (errno, strerror):
            print "I/O error({0}): {1}".format(errno, strerror)
            return False

    def __init__(self, map_path=None):
        self.name = ''

        if map_path:
            self._load(map_path)
        else:
            # default list of item types
            for type_ in ITEM_TYPES:
                if type_ != 'version' and type_ != 'layer':
                    setattr(self, ''.join([type_, 's']), [])

    @property
    def layers(self):
        """Returns a list of all layers, collected from the groups."""
        layers = []
        for group in self.groups:
            layers.extend(group.layers)
        return layers

    @property
    def gamelayer(self):
        """Just returns the gamelayer."""
        for layer in self.layers:
            if layer.is_gamelayer:
                return layer

    @property
    def telelayer(self):
        """Just returns the telelayer."""
        for layer in self.layers:
            if layer.is_telelayer:
                return layer

    @property
    def speeduplayer(self):
        """Just returns the speeduplayer."""
        for layer in self.layers:
            if layer.is_speeduplayer:
                return layer

    @property
    def width(self):
        return self.gamelayer.width

    @property
    def height(self):
        return self.gamelayer.height

    def _load(self, map_path):
        """Load a new teeworlds map from `map_path`.

        Should only be called by __init__.
        """
        datafile = DataFileReader(map_path)
        self.envelopes = datafile.envelopes
        self.envpoints = datafile.envpoints
        self.groups = datafile.groups
        self.images = datafile.images
        self.info = datafile.info

    def _create_default(self):
        """Creates the default map.

        The default map consists out of two groups containing a quadlayer
        with the background and the game layer. Should only be called by
        __init__.
        """

        self.info = items.Info()
        self.groups = []
        background_group = items.Group()
        self.groups.append(background_group)
        background_group.default_background()
        background_layer = items.QuadLayer()
        background_layer.add_background_quad()
        background_group.layers.append(background_layer)
        game_group = items.Group()
        self.groups.append(game_group)
        game_layer = items.TileLayer(game=1)
        game_group.layers.append(game_layer)

    def __repr__(self):
        '<Teemap ({0})>'.format(self.name or 'new')
