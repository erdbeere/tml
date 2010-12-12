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

    def __init__(self, teemap, f):
        self.teemap = teemap
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

    def write(self, f):#size, swaplen, num_item_types, num_items, num_raw_data,
                #item_size, data_size):
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
        for data in teemap.data:
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
            self.header = Header(self, f)
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
            compressed_datas = self.data # but they are decompressed...?
            # write header
            self.header.write(f)
            # write types
            item_types = []
            count = 0
            for i, item_type in enumerate(ITEM_TYPES):
                if item_type == 'info':
                    continue
                elif item_type in ('version', 'envpoint'):
                    item_types.append({
                        'type': i,
                        'start': count,
                        'num': 1
                    })
                    count += 1
                    continue
                name = ''.join([item_type, 's'])
                typelist = getattr(self, name)
                if typelist:
                    item_types.append({
                        'type': i,
                        'start': count,
                        'num': len(typelist)
                    })
                    count += len(typelist)
            for item_type in item_types:
                f.write(pack('3i', item_type['type'], item_type['start'], item_type['num']))

            # get items
            itemdata = []
            item_types = []
            for i, item_type in enumerate(ITEM_TYPES):
                if item_type == 'version':
                    itemdata.append(i) # type and id
                    itemdata.append(4) # size
                    itemdata.append(1) # version
                    item_types.append('version')
                elif item_type == 'envpoint':
                    itemdata.append(i<<16)
                    size = 0
                    for envpoint in self.envpoints:
                        size += 6*4
                    itemdata.append(size)
                    for envpoint in self.envpoints:
                        itemdata.append(envpoint.time)
                        itemdata.append(envpoint.curvetype)
                        for value in envpoint.values:
                            itemdata.append(value)
                    item_types.append('envpoint')
                elif item_type == 'image':
                    for id_, image in enumerate(self.images):
                        itemdata.append((i<<16)|id_)
                        itemdata.append(items.Image.size-8)
                        itemdata.append(1) # image version
                        itemdata.append(image.width)
                        itemdata.append(image.height)
                        itemdata.append(image.external)
                        itemdata.append(image.image_name)
                        itemdata.append(image.image_data)
                        item_types.append('image')
                elif item_type == 'envelope':
                    for id_, envelope in enumerate(self.envelopes):
                        itemdata.append((i<<16)|id_)
                        itemdata.append(items.Envelope.size-8)
                        itemdata.append(1) # envelope version
                        itemdata.append(envelope.channels)
                        itemdata.append(envelope.start_point)
                        itemdata.append(envelope.num_points)
                        name = envelope.string_to_ints()
                        for int in name:
                            itemdata.append(int)
                        item_types.append('envelope')
                elif item_type == 'group':
                    for id_, group in enumerate(self.groups):
                        itemdata.append((i<<16)|id_)
                        itemdata.append(items.Group.size-8)
                        itemdata.append(2) # group version
                        itemdata.append(group.offset_x)
                        itemdata.append(group.offset_y)
                        itemdata.append(group.parallax_x)
                        itemdata.append(group.parallax_y)
                        itemdata.append(group.start_layer)
                        itemdata.append(group.num_layers)
                        itemdata.append(group.use_clipping)
                        itemdata.append(group.clip_x)
                        itemdata.append(group.clip_y)
                        itemdata.append(group.clip_w)
                        itemdata.append(group.clip_h)
                        item_types.append('group')
                elif item_type == 'layer':
                    for id_, layer in enumerate(self.layers):
                        itemdata.append((i<<16)|id_)
                        if LAYER_TYPES[layer.type] == 'tile':
                            itemdata.append(items.TileLayer.size-8)
                            itemdata.append(0) # useless version xD
                            itemdata.append(layer.type)
                            itemdata.append(layer.flags)
                            itemdata.append(2) # tile layer version
                            itemdata.append(layer.width)
                            itemdata.append(layer.height)
                            itemdata.append(layer.game)
                            itemdata.append(layer.color['r'])
                            itemdata.append(layer.color['g'])
                            itemdata.append(layer.color['b'])
                            itemdata.append(layer.color['a'])
                            itemdata.append(layer.color_env)
                            itemdata.append(layer.color_env_offset)
                            itemdata.append(layer.image)
                            itemdata.append(layer.data)
                            item_types.append('tile_layer')
                        elif LAYER_TYPES[layer.type] == 'quad':
                            itemdata.append(items.QuadLayer.size-8)
                            itemdata.append(1) # useless version xD
                            itemdata.append(layer.type)
                            itemdata.append(layer.flags)
                            itemdata.append(1) # quad layer version
                            itemdata.append(layer.num_quads)
                            itemdata.append(layer.data)
                            itemdata.append(layer.image)
                            item_types.append('quad_layer')

            # write item offsets
            item_offsets = []
            item_cur_offset = 0
            for type_ in item_types:
                item_offsets.append(item_cur_offset)
                if type_ == 'envpoint':
                    pass
                elif type_ == 'tile_layer':
                    item_cur_offset += items.TileLayer.size
                elif type_ == 'quad_layer':
                    item_cur_offset += items.QuadLayer.size
                else:
                    item_cur_offset += getattr(items, type_.title()).size
            for item_offset in item_offsets:
                f.write(pack('i', item_offset))

            # write data offsets
            data_cur_offset = 0
            for data in compressed_datas:
                f.write(pack('i', data_cur_offset))
                data_cur_offset += len(data)

            # write uncompressed data sizes
            for data in self.data:
                f.write(pack('i', len(decompress(data))))

            # finally write items
            for data in itemdata:
                f.write(pack('i', data))

            # write data
            for data in compressed_datas:
                f.write(data)

            f.close()

    def __repr__(self):
        return '<Teemap {0} ({1}x{2})>'.format(self.name, self.w, self.h)

if __name__ == '__main__':
    t = Teemap()
    t.load('dm1_test.map')
    t.save()
