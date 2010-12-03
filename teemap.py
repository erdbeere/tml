#!/usr/bin/env python
# -*- coding: utf-8 -*-

from struct import unpack
import zlib

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

class Teemap(object):

    def __init__(self, filename):
        self.name = filename
        with open(filename, 'rb') as f:
            header = Header(f)
            self.item_types = []
            for i in range(header.num_item_types):
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
            fmt = '{0}i'.format(header.num_items)
            item_offsets = unpack(fmt, f.read(header.num_items * 4))
            print ' - item_offsets - '
            print item_offsets
            fmt = '{0}i'.format(header.num_raw_data)
            data_offsets = unpack(fmt, f.read(header.num_raw_data * 4))
            print ' - data_offsets - '
            print data_offsets

            # "data uncompressed size"
            f.read(header.num_raw_data * 4)


            self.rest = f.read()

            self.w, self.h = (0, 0) # should contain size of the game layer
            #self.w, self.h = unpack('2i', f.read(8))
            #print self.w, 'x', self.h
            #f.read(44)
            #self.raw_data = zlib.decompress(f.read())
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
    t = Teemap('maps/dm1.map')
    #print repr(t.rest)
