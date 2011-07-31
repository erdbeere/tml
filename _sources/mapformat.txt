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

Now the size of the whole header can be calculated. This is important to
skip the header and go directly to the items and datas themself. It is the sum
of the following:

* num_item_types * 12 (one item type is composed of three int, one int is four
  bits)
* (num_items + num_raw_data) * 4
* num_raw_data * 4
* item_size

Types
=====
After the header the types are stored. For each item type there is a list
containing the type, the number of items for this type and which itme is the
first for this type.

Item offsets
============
Right after the types the item offsets are stored. The first offset is 0. The
offset to the next item will be the size of the previous item. The size of each
item is as big as defined in `mapitems.h` (see teeworlds source) plus 2 more
integers containing the type, id and the item size. Type and id is within the
first integer.
There is always one "envpoint" item with a dynamic size. It consists of the 2
integers and type size multiplicated with the number of envpoints.

Uncompressed data sizes
=======================
The uncompressed data sizes are stored after the item offsets. The sizes are
used to allocate the memory for each data in teeworlds.

Items
=====
Finally the items are stored. Every item will be stored with all its data in
this order:

#. version
#. images
#. envelops
#. groups
#. layers
#. envpoints

Compressed data
===============
Eventually the compressed data is stored. Image- and tilelayers have an index
which tells the position of the corresponding data.
The compressed data part stores image names, tiles, quads and embedded images.
