========
OVERVIEW
========

GridControl Game! Readme not done yet!

=====
SETUP
=====

Source Code
===========

To download source and set up environment:

::
    
    Grab source from git:
    $ git clone git@github.com:GridControl-Team/GridControl.git

    Install other requirements:
    $ pip install -r requirements.txt

    Create local settings:
    $ cp gridcontrol/settings.py.sample gridcontrol/settings.py

    Edit that settings file and add the secrets you need:
    $ vim gridcontrol/settings.py


Other Dependencies
==================

The test server can live with python's built-in sqlite for the Django ORM,
but the game itself requires redis.  So grab redis however you need and
run it on the default port.

Dev Environment
===============

::
    
    supervisord method:
    $ ./runserver.sh


