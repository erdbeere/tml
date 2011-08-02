.. _examples:

***************
Example scripts
***************

Here is a small collection of snippets using tml. You can find the scripts in
the "examples" directory shipped with tml. Feel free to copy and modify them to
fit your needs!

.. note::

   For portability reasons, this scripts use ``tml.constants.TML_DIR`` to access
   the default maps. You can of course simply pass any path without needing to
   use the ``TML_DIR`` constant.

Count the pickups
=================

Code:

.. literalinclude:: /../examples/count_pickups.py

Output:

.. code-block:: none

    9x armor
    2x shotgun
   10x health
    0x rifle
    1x ninja
    2x grenade

Extract images
==============

Code:

.. literalinclude:: /../examples/extract_images.py

Output: Look into the created "images" directory, you will find all images
saved as png.
