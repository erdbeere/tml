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

A new Teemap objekt does not contain any layers or groups. To create a
minimalistic, but valid teeworlds map, you need to add one group and a
gamelayer.

>>> from tml.tml import Teemap
>>> from tml import items
>>> t = Teemap()
>>> t.groups
[]
>>> t.groups.append(items.Group())
>>> t.groups[0].layers
[]
>>> t.groups[0].layers.append(items.TileLayer(game=True))
>>> t.layers
[<Game layer (50x50)>]
>>> t.groups
[<Group (1)>]
>>> t.save('hello map')

Note that a gamelayer is just a tilelayer with a special ``game flag``

Saving a map
============
