# -*- coding: utf-8 -*-
from bisect import insort
from struct import unpack
from zlib import decompress

from constants import *
import items
from utils import ints_to_string

class Header(object):
    """Contains fileheader information.

    Please make sure the passed file is at the beginning.
    Note that the file won't be rewinded!

    :param f: The file with the information.
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

class DataFileReader(object):

    def __init__(self, map_path):
        # default list of item types
        for type_ in ITEM_TYPES:
            if type_ != 'version' and type_ != 'layer':
                setattr(self, ''.join([type_, 's']), [])

        path, filename = os.path.split(map_path)
        self.name, extension = os.path.splitext(filename)
        if extension == '':
            self.map_path = os.extsep.join([map_path, 'map'])
        elif extension != ''.join([os.extsep, 'map']):
            raise TypeError('Invalid file')
        else:
            self.map_path = map_path

        with open(self.map_path, 'rb') as f:
            self.f = f
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
                raise ValueError('Wrong version')

            # load items
            # begin with map info
            info_item = self.find_item(f, ITEM_INFO, 0)
            self.info = items.Info(self, f, info_item) if info_item else None

            # load images
            start, num = self.get_item_type(ITEM_IMAGE)
            for i in range(num):
                item = self.get_item(f, start+i)
                item_size, item_data = item
                fmt = '{0}i'.format(item_size/4)
                item_data = unpack(fmt, item_data)
                version, width, height, external, image_name, \
                image_data = item_data[:items.Image.type_size]
                external = bool(external)
                name = decompress(self.get_compressed_data(f, image_name))[:-1]
                data = decompress(self.get_compressed_data(f, image_data)) if not external else None
                image = items.Image(external=external, name=name,
                                   data=data, width=width, height=height)
                self.images.append(image)

            # load groups
            group_item_start, group_item_num = self.get_item_type(ITEM_GROUP)
            for i in range(group_item_num):
                item_size, item_data = self.get_item(f, group_item_start+i)
                fmt = '{0}i'.format(item_size/4)
                item_data = unpack(fmt, item_data)
                version, offset_x, offset_y, parallax_x, parallax_y, \
                start_layer, num_layers, use_clipping, clip_x, clip_y, \
                clip_w, clip_h = item_data[:items.Group.type_size-3]
                if version >= 3:
                    data = item_data[items.Group.type_size-3:items.Group.type_size]
                    group_name = ints_to_string(data) or None
                else:
                    group_name = None
                start_layer, num_layers = item_data[5:7]

                # load layers in group
                layer_item_start, layer_item_num = self.get_item_type(ITEM_LAYER)
                layers = []
                for j in range(num_layers):
                    item_size, item_data = self.get_item(f, layer_item_start+start_layer+j)
                    fmt = '{0}i'.format(item_size/4)
                    item_data = unpack(fmt, item_data)
                    layer_version, type_, flags = item_data[:items.Layer.type_size]

                    if LAYER_TYPES[type_] == 'tile':
                        type_size = items.TileLayer.type_size
                        color = {}
                        version, width, height, game, color['r'], color['g'], \
                        color['b'], color['a'], color_env, color_env_offset, \
                        image_id, data = item_data[3:type_size-3]
                        name = None
                        if version >= 3:
                            name = ints_to_string(item_data[type_size-3:type_size]) or None
                        tile_list = []
                        tile_data = decompress(self.get_compressed_data(f, data))
                        for i in xrange(0, len(tile_data), 4):
                            tile_list.append(tile_data[i:i+4])
                        tiles = items.TileManager(data=tile_list)
                        tele_tiles = None
                        speedup_tiles = None
                        if game == 2:
                            tele_list = []
                            if version >= 3:
                                # num of tele data is right after the default type length
                                if len(item_data) > items.TileLayer.type_size: # some security
                                    tele_data = item_data[items.TileLayer.type_size]
                                    if tele_data > -1 and tele_data < self.header.num_raw_data:
                                        tele_data = decompress(self.get_compressed_data(f, tele_data))
                                        for i in xrange(0, len(tele_data), 2):
                                            tele_list.append(tele_data[i:i+2])
                                        tele_tiles = items.TileManager(data=tele_list, _type=1)
                            else:
                                # num of tele data is right after num of data for old maps
                                if len(item_data) > items.TileLayer.type_size-3: # some security
                                    tele_data = item_data[items.TileLayer.type_size-3]
                                    if tele_data > -1 and tele_data < self.header.num_raw_data:
                                        tele_data = decompress(self.get_compressed_data(f, tele_data))
                                        for i in xrange(0, len(tele_data), 2):
                                            tele_list.append(tele_data[i:i+2])
                                        tele_tiles = items.TileManager(data=tele_list, _type=1)
                        elif game == 4:
                            speedup_list = []
                            if version >= 3:
                                # num of speedup data is right after tele data
                                if len(item_data) > items.TileLayer.type_size+1: # some security
                                    speedup_data = item_data[items.TileLayer.type_size+1]
                                    if speedup_data > -1 and speedup_data < self.header.num_raw_data:
                                        speedup_data = decompress(self.get_compressed_data(f, speedup_data))
                                        for i in xrange(0, len(speedup_data), 4):
                                            speedup_list.append(speedup_data[i:i+4])
                                        speedup_tiles = items.TileManager(data=speedup_list, _type=2)
                            else:
                                # num of speedup data is right after tele data
                                if len(item_data) > items.TileLayer.type_size-2: # some security
                                    speedup_data = item_data[items.TileLayer.type_size-2]
                                    if speedup_data > -1 and speedup_data < self.header.num_raw_data:
                                        speedup_data = decompress(self.get_compressed_data(f, speedup_data))
                                        for i in xrange(0, len(speedup_data), 4):
                                            speedup_list.append(speedup_data[i:i+4])
                                        speedup_tiles = items.TileManager(data=speedup_list, _type=2)
                        layer = items.TileLayer(width=width, height=height,
                                                name=name, game=game,
                                                color=color, color_env=color_env,
                                                color_env_offset=color_env_offset,
                                                image_id=image_id, tiles=tiles,
                                                tele_tiles=tele_tiles,
                                                speedup_tiles=speedup_tiles)
                    elif LAYER_TYPES[type_] == 'quad':
                        type_size = items.QuadLayer.type_size
                        version, num_quads, data, image_id = item_data[3:type_size-3]
                        name = None
                        if version >= 2:
                            name = ints_to_string(item_data[type_size-3:type_size]) or None
                        quad_data = decompress(self.get_compressed_data(f, data))
                        quad_list = []
                        for k in xrange(0, len(quad_data), 152):
                            quad_list.append(quad_data[k:k+152])
                        quads = items.QuadManager(data=quad_list)
                        layer = items.QuadLayer(name=name, image_id=image_id,
                                                quads=quads)

                    layers.append(layer)

                group = items.Group(name=group_name, offset_x=offset_x,
                                    offset_y=offset_y, parallax_x=parallax_x,
                                    parallax_y=parallax_y,
                                    use_clipping=use_clipping, clip_x=clip_x,
                                    clip_y=clip_y, clip_w=clip_w,
                                    clip_h=clip_h, layers=layers)
                self.groups.append(group)

            # load envpoints
            item_size, item = self.find_item(f, ITEM_ENVPOINT, 0)
            fmt = '{0}i'.format(item_size/4)
            item = unpack(fmt, item)
            type_size = items.Envpoint.type_size
            for i in range(len(item)/6):
                point = item[(i*6):(i*6+6)]
                time, curvetype = point[:type_size-4]
                values = list(point[type_size-4:type_size])
                envpoint = items.Envpoint(time=time, curvetype=curvetype,
                                          values=values)
                self.envpoints.append(envpoint)

            # load envelopes
            start, num = self.get_item_type(ITEM_ENVELOPE)
            type_size = items.Envelope.type_size
            for i in range(num):
                item_size, item_data = self.get_item(f, start+i)
                fmt = '{0}i'.format(item_size/4)
                item_data = unpack(fmt, item_data)
                version, channels, start_point, \
                num_point = item_data[:type_size-8]
                name = ints_to_string(item_data[type_size-8:type_size])
                envpoints = self.envpoints[start_point:num_point]
                envelope = items.Envelope(name=name, version=version,
                                          channels=channels,
                                          envpoints=envpoints)
                self.envelopes.append(envelope)

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
        """Finds the item and returns it from the file.

        :param f: Filepointer
        :param item_type:
        :param index:
        """
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

