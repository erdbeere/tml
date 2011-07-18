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

import PIL.Image
import PIL.ImageChops

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

    def __init__(self, teemap, f=None):
        self.teemap = teemap
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
            self.size = self.num_item_types * 12
            self.size += (self.num_items + self.num_raw_data) * 4
            self.size += self.num_raw_data * 4
            self.size += self.item_size

        # why the hell 36?
        self.size += 36

    def write(self, f):
        """Write the header itself in tw map format to a file.

        It calculates the item sizes. Every item consists of a special number of
        ints plus two additional ints which are added later (this is the +8).
        There is allways one envpoint item and one version item. All other items
        counted.
        """

        # count all items
        teemap = self.teemap
        item_size = len(teemap.layers + teemap.groups + teemap.images + \
                        teemap.envelopes) + 1 # 1 = envpoint item
        # calculate compressed data size and store the compressed data
        datas = []
        data_size = 0
        for data in teemap.compressed_data:
            data_size += len(data)
            datas.append(data)
        # calculate the item size
        layers_size = 0
        for layer in teemap.layers:
            if LAYER_TYPES[layer.type] == 'tile':
                layers_size += items.TileLayer.size
            else:
                layers_size += items.QuadLayer.size
        version_size = 4+8
        envelopes_size = len(teemap.envelopes)*items.Envelope.size
        groups_size = len(teemap.groups)*items.Group.size
        envpoints_size = len(teemap.envpoints)*24+8
        images_size = len(teemap.images)*items.Image.size
        item_size = version_size+groups_size+layers_size+envelopes_size \
                    +images_size+envpoints_size
        num_items = len(teemap.envelopes + teemap.groups + teemap.layers + \
                        teemap.images) + 2 # 2 = version item + envpoint item
        num_item_types = 2 # version and envpoints
        for type_ in ITEM_TYPES[2:]:
            if type_ == 'envpoint':
                continue
            name = ''.join([type_, 's'])
            if getattr(teemap, name):
                num_item_types += 1
        num_raw_data = len(datas)
        # calculate some other sizes
        header_size = 36
        type_size = num_item_types*12
        offset_size = (num_items+2*num_raw_data)*4
        size = header_size+type_size+offset_size+item_size+data_size-16
        swaplen = size-data_size

        f.write(pack('4c', *'DATA'))
        f.write(pack('8i', 4, size, swaplen, num_item_types, num_items,
                           num_raw_data, item_size, data_size))

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
        self.header = Header(self)

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

    def load(self, map_path):
        """Load a new teeworlds map from `map_path`."""

        path, filename = os.path.split(map_path)
        self.name, extension = os.path.splitext(filename)
        if extension == '':
            map_path = os.extsep.join([map_path, 'map'])
        elif extension != ''.join([os.extsep, 'map']):
            raise TypeError('Invalid file')
        with open(map_path, 'rb') as f:
            self.race = False
            self.header = Header(self, f)
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
            for item_type in self.item_types:
                for i in range(item_type['num']):
                    size = sizes[item_type['start'] + i]
                    print size
                    if self.race == False and (size == 76 or size == 88): # detect race map
                        self.race = True
                    item = items.Item(item_type['type'])
                    item.load(f.read(size), self.compressed_data, self.race)

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

        # usefull for some people like bnn :P
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
    t.load('dm1_test')
