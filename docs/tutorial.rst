********
Tutorial
********

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

Modifying & creating a map from scratch
=======================================

A new Teemap objekt does not contain any layers or groups. To create a
minimalistic, but valid teeworlds map, you need to add one group and a
gamelayer.

>>> from tml.tml import Teemap
>>> from tml.items import Group, TileLayer
>>> t = Teemap()
>>> t.groups
[]
>>> t.groups.append(Group())
>>> t.groups[0].layers
[]
>>> t.groups[0].layers.append(TileLayer(game=True))
>>> t.layers
[<Game layer (50x50)>]
>>> t.groups
[<Group (1)>]
>>> t.save('hello map')

Note that a gamelayer is just a tilelayer with a special ``game flag``

You can at any time call the :meth:`validate <tml.tml.Teemap.validate>`
method, which will return ``True`` if your map is ready to be saved, or raise
an error with information what is wrong with your map.

Managers
--------

For an efficiently memory usage, we do not save the :class:`Tile
<tml.items.Tile>` and :class:`Quad <tml.items.Quad>` objects in simple lists.
There is a huge number of tiles and quads in a average map, saving them as
Tile and Quad objects will eat up your ram. For this reason, we save them as
plain strings. A single tile may look like this:

   ``\x01\x00\x00\x00``

The quads, too, just a bit longer. Nevertheless, we want you to provide a
simple interface, and not give you those ugly strings. This is why we invented
the :class:`Quad- <tml.items.QuadManager` and :class:`TileManager
<tml.items.TileManager`. You can access the tiles through the manager like a
normal list, and the manager will generate a Tile or Quad object for you on the
fly. But keep in mind, that the generate object is **only a copy** of the
string representation of the tile or quad! That means, that you need to
explicity assign the tile, if you changed it! This will NOT work:

  >>> layer.tiles[10].rotate('l')

Instead, do this:

  >>> tile = layer.tiles[10]
  >>> tile.rotate('l')
  >>> layer.tiles[10] = tile

Selecting a subset of a tilelayer
---------------------------------

You can cut out an rectangle of a layer and get a new layer. Use :meth:`select
<tml.items.TileLayer.select>` for that purpose. If you try to select over the
edges of the layer, your values will just be clamped.

  >>> t.gamelayer
  <Game layer (60x50)>
  >>> t.gamelayer.select(20,20,5,10)
  <Game layer (5x10)>
  >>> t.gamelayer.select(10,0,20,42)
  <Game layer (20x42)>
  >>> t.gamelayer.select(50,0,15,5)
  <Game layer (10x5)>
  >>> t.gamelayer.select(70,0,15,5)
  <Game layer (1x5)>


Resizing a tilelayer
--------------------

TODO

Not even implemented, change width and height to properties and if changed,
extend or cutoff the content of tilemanager. Select should be usefull.

Saving a map
============

Saving a map to a file is just as easy as reading it. Just call the
:meth:`save <tml.tml.Teemap.save>` method and give it the path where it
should save the file. You can, but do not need to leave ot the ``.map``
fileextension, it will be added automatically.

>>> teemap.save('/home/tee/my_great_map')
