#!/usr/bin/env python
# -*- coding: utf-8 -*-

from struct import unpack
from zlib import decompress

class Item(object):


    def __init__(self):
        self.type = 0
        self.id = 0
        self.size = 0
        self.next = 0
        self.prev = 0
        self.data = None

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

class Teemap(object):


    def __init__(self, filename):
        self.name = filename
        with open(filename, 'rb') as f:
            self.header = Header(f)
            self.item_types = []
            for i in range(self.header.num_item_types):
                val = unpack('3i', f.read(12))
                self.item_types.append({
                    'type': val[0],
                    'start': val[1],
                    'num': val[2],
                })
            print ' - item_types - '
            for item_type in self.item_types:
                print 'type={0:2} start={1:2} num={2:2}'.format(
                    item_type['type'], item_type['start'], item_type['num'])
            fmt = '{0}i'.format(self.header.num_items)
            self.item_offsets = unpack(fmt, f.read(self.header.num_items * 4))
            print ' - item_offsets - '
            print self.item_offsets
            fmt = '{0}i'.format(self.header.num_raw_data)
            self.data_offsets = unpack(fmt, f.read(self.header.num_raw_data * 4))
            print ' - data_offsets - '
            print self.data_offsets

            # "data uncompressed size"
            # print repr(f.read(self.header.num_raw_data * 4))

            self.data_start_offset = self.header.size + 36
            self.item_start_offset = self.header.size - self.header.item_size

            self.data = []
            f.seek(self.data_start_offset)
            for offset in (self.data_offsets + (self.header.data_size,)):
                if offset > 0:
                    self.data.append(decompress(f.read(offset - last_offset)))
                last_offset = offset

            self.items = []
            f.seek(self.item_start_offset)
            for offset in (self.item_offsets + (self.header.item_size,)):
                if offset > 0:
                    self.items.append(f.read(offset - last_offset))
                last_offset = offset

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
    t = Teemap('5x5.map')
