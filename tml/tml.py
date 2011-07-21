#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A library which makes it possible to read teeworlds map files.

    :copyright: 2010-2011 by the TML Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""

import os
from struct import unpack, pack
from zlib import decompress, compress

from constants import *
import items

class Header(object):
    """Contains fileheader information.

    Takes a file as argument, please make sure it is at the beginning.
    Note that the file won't be rewinded!
    """

    def __init__(self, f=None):
        self.version = 4
        self.size = 0
        if f != None:
            sig = ''.join(unpack('4c', f.read(4)))
            if sig not in ('DATA', 'ATAD'):
                raise TypeError('Invalid signature')
            self.version, self.size_, self.swaplen, self.num_item_types, \
            self.num_items, self.num_raw_data, self.item_size, \
            self.data_size = unpack('8i', f.read(32))

            if self.version != 4:
                raise TypeError('Wrong version')

            # calculate the size of the whole header
            self.size = sum([
                36, # header data before the offsets
                self.num_item_types * 12,
                (self.num_items + (2 * self.num_raw_data)) * 4 # item offsets, data offsets, uncompressed data sizes
            ])

class Teemap(object):

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
        self.header = Header()

        # default list of item types
        for type_ in ITEM_TYPES:
            if type_ != 'version' and type_ != 'layer':
                setattr(self, ''.join([type_, 's']), [])

        if map_path:
            self.load(map_path)
        else:
            pass#self.create_default()

    @property
    def layers(self):
        """Returns a list of all layers, collected from the groups."""
        layers_ = []
        for group in self.groups:
            layers_.extend(group.layers)
        return layers_

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

    def get_item_type(self, item_type):
        """Returns the index of the first item and the number of items for the type."""
        for i in range(self.header.num_item_types):
            if self.item_types[i]['type'] == item_type:
                return (self.item_types[i]['start'], self.item_types[i]['num'])
        return (0, 0)

    def _get_item_size(self, index):
        """Returns the size of the item."""
        if index == self.header.num_items - 1:
            return (self.header.item_size - self.item_offsets[index]) - 8   # -8 to cut out type_and_id and size
        return (self.item_offsets[index+1] - self.item_offsets[index]) - 8

    def get_item(self, f, index):
        """Returns the item from the file."""
        if index < self.header.num_items:
            f.seek(self.header.size + self.item_offsets[index] + 8) # +8 to cut out type_and_id and size
            size = self._get_item_size(index)
            return (size, f.read(size))
        return None

    def find_item(self, f, item_type, index):
        """Finds the item and returns it from the file."""
        start, num = self.get_item_type(item_type)
        if index < num:
            return self.get_item(f, start+index)
        return None

    def _get_compressed_data_size(self, index):
        """Returns the size of the compressed data part."""
        if index == self.header.num_raw_data - 1:
            return self.header.data_size - self.data_offsets[index]
        return self.data_offsets[index+1] - self.data_offsets[index]

    def get_compressed_data(self, f, index):
        """Returns the compressed data and size of it from the file."""
        size = self._get_compressed_data_size(index)
        f.seek(self.header.size + self.header.item_size + self.data_offsets[index])
        return f.read(size)

    def load(self, map_path):
        """Load a new teeworlds map from `map_path`."""

        path, filename = os.path.split(map_path)
        self.name, extension = os.path.splitext(filename)
        if extension == '':
            map_path = os.extsep.join([map_path, 'map'])
        elif extension != ''.join([os.extsep, 'map']):
            raise TypeError('Invalid file')
        with open(map_path, 'rb') as f:
            self.header = Header(f)
            self.item_types = []
            for i in range(self.header.num_item_types):
                val = unpack('3i', f.read(12))
                self.item_types.append({
                    'type': val[0],
                    'start': val[1],
                    'num': val[2],
                })
            fmt = '{0}i'.format(self.header.num_items)
            self.item_offsets = unpack(fmt, f.read(self.header.num_items * 4))
            fmt = '{0}i'.format(self.header.num_raw_data)
            self.data_offsets = unpack(fmt, f.read(self.header.num_raw_data * 4))

            # check version
            item_size, version_item = self.find_item(f, ITEM_VERSION, 0)
            fmt = '{0}i'.format(item_size/4)
            version = unpack(fmt, version_item)[0] # we only expect 1 element here
            if version != 1:
                raise TypeError('Wrong version')

            # load items
            # begin with map info
            info_item = self.find_item(f, ITEM_INFO, 0)
            if info_item:
                self.map_info = items.Info(self, f, info_item)

            # load images
            start, num = self.get_item_type(ITEM_IMAGE)
            for i in range(num):
                self.images.append(items.Image(self, f, self.get_item(f, start+i)))

            # load groups
            group_item_start, group_item_num = self.get_item_type(ITEM_GROUP)
            for i in range(group_item_num):
                group_size, group_item = self.get_item(f, group_item_start+i)
                group = items.Group(self, f, (group_size, group_item))
                fmt = '{0}i'.format(group_size/4)
                group_item = unpack(fmt, group_item)
                start_layer, num_layers = group_item[5:7]

                # load layers in group
                layer_item_start, layer_item_num = self.get_item_type(ITEM_LAYER)
                for j in range(num_layers):
                    # create general layer
                    layer_item = self.get_item(f, layer_item_start+start_layer+j)
                    layer = items.Layer(f, layer_item)

                    #find out which layer we have
                    if LAYER_TYPES[layer.type] == 'tile':
                        layer = items.TileLayer(teemap=self, f=f, item=layer_item)
                    elif LAYER_TYPES[layer.type] == 'quad':
                        layer = items.QuadLayer(teemap=self, f=f, item=layer_item)

                    # add layer to group
                    group.add_layer(layer)

                # add group
                self.groups.append(group)

            # load envpoints
            item_size, item = self.find_item(f, ITEM_ENVPOINT, 0)
            fmt = '{0}i'.format(item_size/4)
            item = unpack(fmt, item)
            for i in range(len(item)/6):
                point = item[(i*6):(i*6+6)]
                self.envpoints.append(items.Envpoint(self, point))

            # load envelopes
            start, num = self.get_item_type(ITEM_ENVELOPE)
            for i in range(num):
                self.envelopes.append(items.Envelope(self, f, self.get_item(f, start+i)))

    def create_default(self):
        """Creates the default map.

        The default map consists out of two groups containing a quadlayer
        with the background and the game layer.
        """

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

if __name__ == '__main__':
    t = Teemap()
    t.load('tml/maps/dm1')
