#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from struct import unpack
from zlib import decompress

from constants import ITEM_TYPES, LAYER_TYPES
import items

class Header(object):
    """Contains fileheader information.

    Takes a file as argument, please make sure it is at the beginning.
    Note that the file won't be rewinded!
    """

    def __init__(self, f):
        sig = ''.join(unpack('4c', f.read(4)))
        if sig not in ('DATA', 'ATAD'):
            raise TypeError('Invalid signature')
        self.version, self.size, self.swaplen, self.num_item_types, \
        self.num_items, self.num_raw_data, self.item_size, \
        self.data_size = unpack('8i', f.read(32))
        if self.version != 4:
            raise TypeError('Wrong version')

        # calculate the size of the whole header
        self.size = self.num_item_types * 12
        self.size += (self.num_items + self.num_raw_data) * 4
        self.size += self.num_raw_data * 4
        self.size += self.item_size

        # why the hell 36?
        self.size += 36

class Teemap(object):


    def __init__(self):
        self.name = ''
        self.w = self.h = 0

    def load(self, map_path):
        """Load a new teeworlds map."""

        path, filename = os.path.split(map_path)
        self.name, extension = os.path.splitext(filename)
        if extension != ''.join([os.extsep, 'map']):
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

            self.data_start_offset = self.header.size
            self.item_start_offset = self.header.size - self.header.item_size

            self.data = []
            f.seek(self.data_start_offset)
            for offset in (self.data_offsets + (self.header.data_size,)):
                if offset > 0:
                    self.data.append(f.read(offset - last_offset))
                last_offset = offset

            # calculate with the offsets and the whole item size the size of each item
            sizes = []
            for offset in self.item_offsets + (self.header.item_size,):
                if offset > 0:
                    sizes.append(offset - last_offset)
                last_offset = offset

            f.seek(self.item_start_offset)
            self.itemlist = []
            for item_type in self.item_types:
                for i in range(item_type['num']):
                    size = sizes[item_type['start'] + i]
                    item = items.Item(item_type['type'])
                    item.load(f.read(size), self.data)
                    self.itemlist.append(item)

            # order the items
            for type_ in ITEM_TYPES:
                name = ''.join([type_, 's'])
                class_ = getattr(items, type_.title())
                setattr(self, name, [class_(item) for item in self.itemlist
                                    if item.type == type_])

            # specify layers (tile- or quadlayer)
            layers = self.layers
            self.layers = []
            for layer in layers:
                layerclass = ''.join([LAYER_TYPES[layer.type].title(), 'Layer'])
                class_ = getattr(items, layerclass)
                self.layers.append(class_(layer.item))

            # assign layers to groups
            for group in self.groups:
                start = group.start_layer
                end = group.start_layer + group.num_layers
                group.layers = [layer for layer in self.layers[start:end]]

            #for item in self.items:
            #    # load groups
            #    if item.type == 'group':
            #        group = items.Group(len(self.groups)+1, item.data[2:])
            #        self.groups.append(group)

            #    #load layers
            #    elif item.type == 'layer':
            #        # quad layer
            #        if item.data[3] == LAYER_TYPES['quads']:
            #            layer = items.LayerQuad(len(self.layers)+1, item.data[2:])
            #            self.layers.append(layer)
            #        # tile layer
            #        elif item.data[3] == LAYER_TYPES['tiles']:
            #            layer = items.LayerTile(len(self.layers)+1, item.data[2:])
            #            self.layers.append(layer)


            self.w, self.h = (0, 0) # should contain size of the game layer
            #self.w, self.h = unpack('2i', f.read(8))
            #print self.w, 'x', self.h
            #f.read(44)
            #self.raw_data = decompress(f.read())
            #fmt = '{0}i'.format(len(self.raw_data) / 4)
            #layer = []
            #tiles = unpack(fmt, self.raw_data)
            #for i in range(self.h):
            #    layer.append(tiles[i*self.w:i*self.w+self.w])
            #for row in layer:
            #    for col in row:
            #        print '{0:3}'.format(col),
            #    print

    def __repr__(self):
        return '<Teemap {0} ({1}x{2})>'.format(self.name, self.w, self.h)

if __name__ == '__main__':
    t = Teemap()
    t.load('dm1_test.map')
