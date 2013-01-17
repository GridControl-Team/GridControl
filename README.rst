========
OVERVIEW
========

.. image:: http://i.imgur.com/Fnm9Y.png?1
   :scale: 50 %
   :alt: Awesome GridControl Logo
   :align: right

GridControl is a Free-to-play In-browser Social Massive-Multiplayer-Online
Game, where you control your bot using a specialized stack-based language
(called gridlang) and your github account.  Your bot can roam the grid,
gather resources, and attack/avoid other bots.  The best code wins!

GridControl Game! GridControl is a originally a project started during
`GitHub's Game Off 2012 <https://github.com/github/game-off-2012>`_.
It was not even in an alpha state by the end of the gameoff, but the vision
has continues.

HOW TO PLAY
===========

Log in with your github account at the `test server <http://gridcontrol.freelancedreams.com/>`_.

`Learn how to gridlang <https://github.com/GridControl-Team/GridControl/blob/master/gridlang/README.rst>`_

`Learn how to control your bot <https://github.com/GridControl-Team/GridControl/blob/master/BOTCONTROL.rst>`_

Add a `gist on github <https://gist.github.com>`_ with the file extension ``.gridlang``

WIN


===========
LATEST NEWS
===========

Lasers were implemented. They're pretty awesome.

Players with a passion for c-syntax can use ``.gridc`` from `gridc <https://github.com/lessandro/gridc>`_,
a c-like language that compiles to gridlang.


=============================
SETTING UP GRIDCONTROL SERVER
=============================

Source Code
===========

To download source and set up environment:

::
    
    Grab source from git:
    $ git clone git@github.com:GridControl-Team/GridControl.git

    Make a virtualenv or else
    $ mkvirtualenv gridcontrol

    Install other requirements:
    $ pip install -r requirements.txt

    Create local settings:
    $ cp gridcontrol/settings.py.sample gridcontrol/settings.py

    Edit that settings file and add the secrets you need:
    $ vim gridcontrol/settings.py

    Do djangoy setup
    $ python manage.py syncdb
    $ python manage.py migrate


Other Dependencies
==================

The test server can live with python's built-in sqlite for the Django ORM,
but the game itself requires redis.  So grab redis however you need and
run it on the default port.

GridControl Parts
=================

GridControl: Public facing Django site that users see

GridLang: gridlang language vm and parser code

GridStream: tornado server using socket.io to stream realtime bot status


Run Dev Environment
===================

::
    
    supervisord method:
    $ ./runserver.sh

Supervisord is configured to automatically start the celery and tornado
servers.  The django site can be started with either ``start gridcontrol_gunicorn``
for production machines, or ``start gridcontrol_runserver`` for local
development.

Or look inside of the supervisor conf to see the commands to run the separate
services.
