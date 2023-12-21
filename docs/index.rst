
historicaldate documentation
============================

A small Python package for date handling including support for BC dates and uncertainty.

Github: https://github.com/dh3968mlq/historicaldate/

It is intended for dealing with historical events. It does not support time of day, and at present takes a naive approach to 
the difference between Julian and Gregorian calendars, since this is usually what is needed for the expected application areas.

The package provides a parser for date formats that are often used to indicate uncertain dates, such as

*   circa 1989
*   between 1920 and 1934
*   2003
*   circa 1483 earliest 1483

The parser converts these to a *HDate()* object, which stores the earliest possible, 
latest possible and an approximate midpoint date corresponding to the original string.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   overview
   hdate
   hdateutils

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
