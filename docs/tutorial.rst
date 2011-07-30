========
Tutorial
========

Welcome! This tutorial will help you using this library to read and create
teeworlds maps.


Load and reading a map
======================

Loading
-------

To load a teeworlds map, simply pass the path (with or without the ``.map``
extension) to the Teemap class. Example:

>>> from tml.tml import Teemap
>>> t = Teemap('dm1')
>>> t = Teemap('dm1.map')

Reading
-------

The structure of the teemap is similiar to the structure you know from the
teeworlds editor, it should be familiar to you.
Example: Getting a list of tiles and their index.

>>> t = Teemap('dm1')
>>> tiles = t.group[5].layers[0].tiles
>>> tiles
<TileManager (3000)>
>>> tiles[0].index
0
>>> tiles[90].index
24

For a full list of all methods and attributes, check :class:`tml.tml.Teemap`

Creating a map from scratch
===========================


Saving a map
============
