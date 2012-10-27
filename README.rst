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


Other Dependencies
==================

The test server can live with python's built-in sqlite for the Django ORM,
but the game itself requires redis, and the integrated dev environment requires
the pound loadbalancer.  So grab redis and pound however you need and run redis
it on the default port (supervisord will take care of pound)

Dev Environment
===============

::
    
    supervisord method:
    $ ./runserver.sh


