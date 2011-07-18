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

from constants import ITEM_TYPES, LAYER_TYPES
import items

def int32(x):
    if x>0xFFFFFFFF:
        raise OverflowError
    if x>0x7FFFFFFF:
        x=int(0x100000000-x)
        if x<2147483648:
            return -x
        else:
            return -2147483648
    return x

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
                self.num_item_types * 12,
                (self.num_items + self.num_raw_data) * 4,
                self.num_raw_data * 4,
                self.item_size,
                36, #XXX: find out why 36
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
            if type_ != 'layer':
                setattr(self, ''.join([type_, 's']), [])

        if map_path:
            self.load(map_path)
        else:
            self.create_default()

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
            if self.item_types[i]['type'] == type:
                return (self.item_types[i]['start'], self.item_types[i]['num'])
        return (0, 0)

    def _get_item_size(self, index):
        """Returns the size of the item."""
        if index == self.num_items -1:
            return self.header.item_size - self.item_offsets[index]
        return self.item_offsets[index+1] - self.item_offsets[index]

    def get_item(self, f, index):
        """Returns the item from the file."""
        f.seek((self.header.size - self.header.item_size) + self.item_offsets[index])
        return f.read(_get_item_size(index))

    def _get_compressed_data_size(self, index):
        """Returns the size of the compressed data part."""
        if index == self.num_items -1:
            return self.header.data_size - self.data_offsets[index]
        return self.data_offset[index+1] - self.data_offsets[index]

    def get_compressed_data(self, f, index):
        """Returns the compressed data and size of it from the file."""
        size = _get_compressed_data_size(index)
        f.seek(self.header.size + self.data_offsets[index])
        return (size, f.read(size))

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

            # "data uncompressed size"
            # print repr(f.read(self.header.num_raw_data * 4))

            data_start_offset = self.header.size
            item_start_offset = self.header.size - self.header.item_size

            self.compressed_data = []
            f.seek(data_start_offset)
            for offset in (self.data_offsets + (self.header.data_size,)):
                if offset > 0:
                    self.compressed_data.append(f.read(offset - last_offset))
                last_offset = offset

            # calculate with the offsets and the whole item size the size of
            # each item
            sizes = []
            for offset in self.item_offsets + (self.header.item_size,):
                if offset > 0:
                    sizes.append(offset - last_offset)
                last_offset = offset

            f.seek(item_start_offset)
            layers = []
            self.envpoints = []
            race = False
            for item_type in self.item_types:
                for i in range(item_type['num']):
                    size = sizes[item_type['start'] + i]
                    #FIXME: Workaround to detect race maps
                    if size in (76, 88):
                        race = True
                    item = items.Item(item_type['type'])
                    item.load(f.read(size), self.compressed_data, race)

                    if item.type == 'envpoint':
                        for i in range((len(item.info)-2) / 6):
                            info = item.info[2+(i*6):2+(i*6+6)]
                            self.envpoints.append(items.Envpoint(info))
                    elif item.type == 'layer':
                        layer = items.Layer(item)
                        layerclass = ''.join([LAYER_TYPES[layer.type].title(),
                                             'Layer'])
                        class_ = getattr(items, layerclass)
                        layers.append(class_(item, self.images))
                    else:
                        name = ''.join([item.type, 's'])
                        class_ = getattr(items, item.type.title())
                        getattr(self, name).append(class_(item))

            # assign layers to groups
            for group in self.groups:
                start = group.start_layer
                end = group.start_layer + group.num_layers
                group.layers = [layer for layer in layers[start:end]]

        return self

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
