#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A library which makes it possible to read teeworlds map files.

    :copyright: 2010-2011 by the TML Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""
from constants import *
from datafile import DataFileReader, DataFileWriter

class MapError(BaseException):
    """Raised when your map is not a valid teeworlds map.

    For example, it will be raised when there is no gamelayer or more than one.

    """

class Teemap(object):
    """Representation of a teeworlds map.

    All information about the map can be accessed through this class.

    :param map_path: Path to the teeworlds mapfile.
    """

    def __init__(self, map_path=None):
        self.name = ''

        if map_path:
            self._load(map_path)
        else:
            # default item types
            for type_ in ITEM_TYPES:
                if type_ not in ('version', 'layer', 'info'):
                    setattr(self, ''.join([type_, 's']), [])
            self.info = None

    @property
    def layers(self):
        """Returns a list of all layers, collected from the groups."""
        layers = []
        for group in self.groups:
            layers.extend(group.layers)
        return layers

    @property
    def gamelayer(self):
        """Returns the gamelayer.

        If you have multiple gamelayers (**don't** do that!), it will return
        the first one

        """
        i = 0
        for layer in self.layers:
            if layer.is_gamelayer:
                gamelayer = layer
                i += 1
        if i < 1:
            raise MapError('There is no gamelayer')
        elif i > 1:
            raise MapError('There is more than one gamelayer')
        return gamelayer

    @property
    def telelayer(self):
        """Returns the telelayer. Only for race modification."""
        for layer in self.layers:
            if layer.is_telelayer:
                return layer

    @property
    def speeduplayer(self):
        """Returns the speeduplayer. Only for race modification."""
        for layer in self.layers:
            if layer.is_speeduplayer:
                return layer

    @property
    def width(self):
        return self.gamelayer.width

    @property
    def height(self):
        return self.gamelayer.height

    @property
    def valid(self):
        """Check if the map is a valid teeworlds map.

        Returns ``True`` or raises an exception.

        """
        gamelayer = 0
        for layer in self.layers:
            if layer.is_gamelayer:
                gamelayer += 1
        if gamelayer < 1:
            raise MapError('This map contains no gamelayer.')
        if gamelayer > 1:
            raise MapError('This map contains {0} gamelayers.'.format(gamelayer))
        if len(gamelayer.tiles) == 0:
            raise MapError('The gamelayer does not contain any tiles')

        return True

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

    def save(self, map_path):
        """Saves the current map to `map_path`."""
        DataFileWriter(self, map_path)

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
        return '<Teemap ({0})>'.format(self.name or 'new')
