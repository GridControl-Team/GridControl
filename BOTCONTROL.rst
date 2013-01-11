====================
CONTROLLING YOUR BOT
====================

This document sort of assumes you've been through 
`gridlang <https://github.com/GridControl-Team/GridControl/blob/master/gridlang/README.rst>`_
specifications.  But if you're clever you can probably get by without.

===========
SAMPLE CODE
===========

::
    
    # This bot will continually travel south
    # pulling from the east or west if it
    # finds resources there
    @LOOPSTART
    CALLFF << @LOOK @EAST 2
    IFTGOTO << @PULLEAST
    CALLFF << @LOOK @WEST 2
    IFTGOTO << @PULLWEST
     
    CALLFF << @MOVE @SOUTH 2
    GOTO << @LOOPEND
     
    @PULLEAST
    CALLFF << @PULL @EAST 2
    GOTO << @LOOPEND
     
    @PULLWEST
    CALLFF << @PULL @WEST 2
    GOTO << @LOOPEND
     
    @LOOPEND
    GOTO << @LOOPSTART

ABOUT CODE
==========

As you can see, control of your bot is exposed using gridlang's
``CALLFF`` operation.  ``CALLFF`` initially takes one value, the
number of arguments to pass to the foreign function.  Then,
that number of arguments are popped off the stack and passed along.

The first argument is the bot command, and the remaining arguments
are arguments for that command.  GridControl automatically injects
a number of constants that you will use to refer to the different
bot commands. The constants are:

::
    
    # Action constants
    @LOOK
    @PULL
    @MOVE
    @SCAN
    @PUSH
    @LOCATE
    @IDENTIFY
    
    # Direction constants
    @NORTH
    @SOUTH
    @EAST
    @WEST

    # Identification constants
    @CELL_EMPTY
    @CELL_RESOURCE
    @CELL_ROBOT

``@LOOK`` 1 argument (direction).  It will push a identification constant
onto your stack, depending on what is located within that targeted grid cell.

``@MOVE`` 1 argument (direction).  Move your bot into the direction provided.
Pushes a 1 onto the stack for now (moves atm always succeed)

``@PULL`` 1 argument (direction).  Gather a resource from the direction provided.
Pushes a 1 onto the stack for now (pulls atm always succeed)
If there is a resource, your will gain a point.

``@SCAN`` 2 arguments (deltax, deltay). Like look, but peers in the grid cell
relative to current bot position (e.g., [1, 0] will look east). Pushes an 
identification constant onto your stack, depending on what is located at targeted
cell.

``@PUSH`` 1 argument (direction). Push a bot in a certain direction. You and that
bot both move in direction given. If targeted cell has no bot, or bot's destination
has an obstacle, ``@PUSH`` will fail.

``@LOCATE`` No arguments. Pushes values x, y onto your stack, where x, y are
the coordinates where you bot lives at.  Useful to tell if someone did a ``@PUSH``
on you.

``@IDENTIFY`` 1 argument (direction). Push onto your stack the user_id of bot
that exists in the direction provided. Pushes ``0`` if no bot is there.

``@NORTH``, ``@SOUTH``, ``@EAST``, and ``@WEST`` represent the cardinal directions.
Useful for ``@LOOK`` and ``@MOVE`` commands.

``@CELL_EMPTY`` is returned from ``@LOOK`` and ``@SCAN`` when it finds an empty cell.

``@CELL_RESOURCE`` is returned from ``@LOOK`` and ``@SCAN`` when it finds a cell
with a gatherable resource in it.  You'll want to ``@PULL`` it!

``@CELL_ROBOT`` is returned from ``@LOOK`` and ``@SCAN`` when it finds a cell with
a robot in it. Avoid!

