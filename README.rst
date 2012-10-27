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
but the game itself requires redis.  So grab redis however you need and run
it on the default port.

Dev Environment
===============

::
    
    Run dev server:
    $ python manage.py runserver 0.0.0.0:8000

    Run celery:
    $ i forget

    Run tornado:
    $ blah

    (maybe replace this with supervisor?)


