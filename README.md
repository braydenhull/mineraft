Mineraft
========

Travelling through the sea of inadequacy that is the Minecraft Tools forum, in hopes of turning rivers of garbage into gold.

A program designed for the layman, who hopes to construct a functional CraftBukkit server.

Purpose
-------

For those who frequent the Minecraft Tools section (specifically sorting by new threads) you would be horrified.
Whilst there are plenty of great projects on there which fortunately receive plenty of well earned attention (MultiMC),
there are others which crop up every day trying to fill a need and they often do a terrible job.

This program hopes to fill a gap since there is a market for these types of programs but there are often poor bad
implementations. For instance the author might choose to have it so the program extracts baked in plugins, or they might
provide the links by hand rather than actually having a system where the program can determine the appropriate URL which
would mean the program would require constant maintenance to keep up with new releases of plugins, etc.

Features
--------

- (WIP) Comprehensive list of plugins which are natively supported
- Support for getting any DevBukkit plugins dynamically
- Can install many versions of CraftBukkit from their release streams (Release, Beta, Dev) via utilisation of their API
- The program can generate a working startup script for the Bukkit instance given some information from the user
- The program can run on Linux (after installing a few dependencies) and Windows (compiled binary), maybe even OSX!
- It uses PyQt to drive the interface so that the experience is consistent across all platforms. (Linux, Windows, OSX)
- It can query remote servers if they have enabled query in their server.properties, it shows connected players and
installed plugins at the moment.

Requirements
------------

- Python 2.7.x (previous versions untested, won't work with 3.x)
- BeautifulSoup
- psutil (0.6.x or greater, Ubuntu apt repo only supplies 0.4.x which is not sufficient, use pip to install latest)
- Feedparser
- PyQt

Refer to imports to see what core modules are required. (These should be built into your Python environment by default)

Credits
-------

These fantastic developers with all their help are what has made this program possible
* The Qt Project and Riverbank Computing Limitd for making PyQt
* Leonard Richardson who created Beautifulsoup, which is a core component of the DevBukkit parsing functions
* Dinnerbone, who created a great Minecraft Query class
* adewale and kurtmckee (listed owners on Google Code) of the Feedparser project, an excellent module for RSS parsing!
* The developers of psutil (there are too many to mention)
* Thanks to the contributiosn to Stackoverflow, many of thsoe contributions have been inserted into this program to make
certain things possible. I've added attributions to various parts but I might've missed some (sorry!)
* Lastly the developers of Python and its core modules. Thanks to their hard work, great documentation and excellent
programming skills, this project in its current state wasn't particularly hard to make.