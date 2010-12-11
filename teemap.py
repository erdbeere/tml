#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from struct import unpack, pack
from zlib import decompress, compress

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

    def write(self, f, size, swaplen, num_item_types, num_items, num_raw_data,
                item_size, data_size):
        """Write the header itself in tw map format to a file."""

        f.write(pack('4c', *'DATA'))
        f.write(pack('8i', 4, size, swaplen, num_item_types, num_items,
                           num_raw_data, item_size, data_size))

class Teemap(object):


    item_count = 0

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
            Teemap.item_count = self.header.num_items
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

            # calculate with the offsets and the whole item size the size of
            # each item
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
                # envpoints will be handled separately
                if type_ == 'envpoint':
                    pass
                else:
                    name = ''.join([type_, 's'])
                    class_ = getattr(items, type_.title())
                    setattr(self, name, [class_(item) for item in self.itemlist
                                        if item.type == type_])

            # devide the envpoints item into the single envpoints
            self.envpoints = []
            for item in self.itemlist:
                if item.type == 'envpoint':
                    for i in range((len(item.info)-2) / 6):
                        info = item.info[2+(i*6):2+(i*6+6)]
                        self.envpoints.append(items.Envpoint(info))

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

            self.w, self.h = (0, 0) # should contain size of the game layer

    def save(self, map_path='unnamed'):
        """Save the current map to `map_path`."""

        path, filename = os.path.split(map_path)
        self.name, extension = os.path.splitext(filename)
        if extension != ''.join([os.extsep, 'map']):
            map_path = ''.join([map_path, os.extsep, 'map'])
        with open(map_path, 'wb') as f:
            # some sizes
            compressed_datas, size, swaplen, num_item_types, num_items, num_raw_data, \
            item_size, data_size = self.calculate_header_sizes()
            # write header
            self.header.write(f, size, swaplen, num_item_types, num_items, num_raw_data,
                                item_size, data_size)
            # write types
            item_types = []
            count = 0
            for id in range(len(ITEM_TYPES)):
                if ITEM_TYPES[id] == 'info':
                    continue
                if ITEM_TYPES[id] == 'version' or ITEM_TYPES[id] == 'envpoint':
                    item_types.append({
                        'type': id,
                        'start': count,
                        'num': 1
                    })
                    count += 1 
                    continue
                name = ''.join([ITEM_TYPES[id], 's'])
                class_ = getattr(self, name)
                if class_:
                    item_types.append({
                        'type': id,
                        'start': count,
                        'num': len(class_)
                    })
                    count += len(class_)
            for item_type in item_types:
                f.write(pack('3i', item_type['type'], item_type['start'], item_type['num']))

            #write item offsets
            item_offsets = []
            item_cur_offset = 0
            for item in self.itemlist:
                item_offsets.append(item_cur_offset)
                if item.type == 'envpoint':
                    pass
                elif item.type == 'layer':
                    layerclass = ''.join([LAYER_TYPES[item.info[3]].title(), 'Layer'])
                    item_cur_offset += getattr(items, layerclass).size
                else:
                    item_cur_offset += getattr(items, item.type.title()).size
            for item_offset in item_offsets:
                f.write(pack('i', item_offset))

            # write data offsets
            data_cur_offset = 0
            for data in compressed_datas:
                f.write(pack('i', data_cur_offset))
                data_cur_offset += len(data)

            # write uncompressed data sizes
            for data in self.datas:
                f.write(pack('i', len(data)))

    def calculate_header_sizes(self):
        """This function returns the sizes important for the header. Also it
        returns the compressed data.

        It calculates the item sizes. Every item consists of a special number of 
        ints plus two additional ints which are added later (this is the +8).
        There is allways one envpoint item and one version item. All other items 
        counted.
        """

        # count all items
        item_size = len(self.layers)+len(self.groups)+len(self.images) \
                    +len(self.envelopes)+1 # 1 = envpoint item
        # calculate compressed data sice and store the compressed data
        datas = []
        data_size = 0
        for data in self.data:
            compressed_data = compress(data)
            data_size += len(compressed_data)
            datas.append(compressed_data)
        # calculate the item size
        layers_size = 0
        for layer in self.layers:
            if LAYER_TYPES[layer.type] == 'tile':
                layers_size += items.TileLayer.size
            else:
                layers_size += items.QuadLayer.size
        version_size = 4+8
        envelopes_size = len(self.envelopes)*items.Envelope.size
        groups_size = len(self.groups)*items.Group.size
        envpoints_size = len(self.envpoints)*24+8
        images_size = len(self.images)*items.Image.size
        item_size = version_size+groups_size+layers_size+envelopes_size \
                    +images_size+envpoints_size
        num_items = 2+len(self.envelopes)+len(self.groups)+len(self.layers) \
                   +len(self.images) # 2 = version item + envpoint item
        num_item_types = 2 # version and envpoints
        for type_ in ITEM_TYPES[2:]:
            if type_ == 'envpoint':
                continue
            name = ''.join([type_, 's'])
            if getattr(self, name):
                num_item_types += 1
        num_raw_data = len(datas)
        # calculate some other sizes
        header_size = 48
        type_size = num_item_types*12
        offset_size = (num_items+2*num_raw_data)*4
        size = header_size+type_size+offset_size+item_size+data_size-16
        swaplen = size-data_size-16
        return datas, size, swaplen, num_item_types, num_items, num_raw_data, \
                item_size, data_size

    def __repr__(self):
        return '<Teemap {0} ({1}x{2})>'.format(self.name, self.w, self.h)

if __name__ == '__main__':
    t = Teemap()
    t.load('dm1_test.map')
