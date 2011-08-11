***********************************
Excursion: The Teeworlds map format
***********************************

In this chapter you will learn how a teeworlds map is structured. This
knowledge is not necessary for using tml, but it can be helpfull if you are
interested in understanding what is going on under the hood or just want
to hack a map yourself.

Header
======
The first bytes just contain the word "DATA" or "ATAD" (little oder big endian),
it is the "signature" of a teeworlds map. After that there is an int which
contains the version of the mapformat, teeworlds 0.5 uses version 4 but also
supports 3, this libary only supports 4.

   ``DATA\\x04\\x00\\x00\\x00``

Then there are four more ints which can be read straight from the file.
These are "size", "swaplen", "num_item_types", "num_items", "num_raw_data",
"item_size" and "data_size".

Now the offsets can be calculated. This is important to seek directly to the
items or datas which contain the actual data.
The item offset is the sum of the following:

* num_item_types * 12 (one item type is composed of three int, one int is four
  bytes)
* num_items * 4
* num_raw_data * 2 * 4

To access the data an additional value gets added to the item offset

* item_size

Item types
=====
After the header the types are stored. For each item type there is a list
containing the type, the number of items for this type and which itme is the
first for this type. The list is sorted by item type and item id.

Item offsets
============
Right after the types the item offsets are stored. The first offset is 0. The
offset to the next item will be the size of the previous item. The size of each
item is as big as defined in `mapitems.h` (see teeworlds source) plus 2 more
integers containing the type, id and the item size.

Data offsets
============
After the item offsets the data offsets are stored. The first offset is 0. The
offset to the next data will be the size of the previous data. The size of each
data gets generated when saveing the map.

Uncompressed data sizes
=======================
The uncompressed data sizes are stored after the data offsets. The sizes are
used to allocate the memory for each data in teeworlds.

Items
=====
Finally the items are stored. Every item will be stored with all its data in
this order:

#. version
#. info
#. images
#. envelops
#. groups
#. layers
#. envpoints

Every item contains the data as defined in `mapitems.h` (see teeworlds source)
plus 2 more integers containing the type, id and the item size.
Type and id is within the first integer. To extract the type and id the
following formulas are used:

* type = (type_and_id >> 16) & 0xffff
* id = type_and_id & 0xffff

Datas
===============
Eventually the datas are stored. The data is compressed using zlib. Each item
which requires data has an index which tells the position of the corresponding
data.
The compressed data part stores image names, tiles, quads and embedded images.
