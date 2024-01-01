
historicaldate documentation
============================

A small Python package for date handling including support for BC dates and uncertainty.

Install::
   pip install historicaldate

Github: https://github.com/dh3968mlq/historicaldate/

PyPI: https://pypi.org/project/historicaldate/

The package provides a parser for date formats that are often used to indicate uncertain dates, such as

*   circa 1989
*   between 1920 and 1934
*   2003
*   circa 1483 earliest 1483

The parser converts these to a *HDate()* object, which stores the earliest, 
latest and a midpoint date corresponding to the original string.

.. code-block:: python
   
   >>> import historicaldate as hdt
   >>> hd1 = hdt.HDate("Dec 1066")
   >>> (hd1.pdates["early"], hd1.pdates["mid"],hd1.pdates["late"])
   (datetime.date(1066, 12, 1), datetime.date(1066, 12, 15), datetime.date(1066, 12, 31))
   >>>

It is intended for dealing with historical events. It does not support time of day, and at present takes a naive approach to 
the difference between Julian and Gregorian calendars, since this is usually what is needed for the expected application areas.

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
