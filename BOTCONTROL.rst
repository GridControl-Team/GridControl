====================
CONTROLLING YOUR BOT
====================

This document sort of assumes you've been through 
`gridlang <https://github.com/GridControl-Team/GridControl/blob/master/gridlang/README.rst>`_
specifications.  But if you're clever you can probably get by without.

ABOUT CODE
==========

Control of your bot is exposed using gridlang's ``CALLFF`` operation.
``CALLFF`` initially takes one value, the number of arguments to pass to the
foreign function.  Then, that number of arguments are popped off the stack
and passed along.

For GridControl, the first argument passed into the FFI system is the bot
command, and the remaining arguments are arguments for that command.
GridControl automatically injects a number of constants that you will use to
refer to the different bot commands. The constants are:

::
    
    # Action constants
    @LOOK
    @PULL
    @MOVE
    @SCAN
    @PUSH
    @LOCATE
    @IDENTIFY
    @INSPECT
    @PUNCH
    @CHARGEUP
    @PEWPEW
    @SELFDESTRUCT
    
    # Direction constants
    @NORTH
    @SOUTH
    @EAST
    @WEST

    # Identification constants
    @CELL_EMPTY
    @CELL_RESOURCE
    @CELL_ROBOT

    # Attribute constants
    @CHARGE
    @RESOURCES
    @SHIELD
    @CALLSIGN
    @POINTS
    @STATUS

    # Status constants
    @OK
    @DEAD
    @STUNNED

BOT ACTION CONSTANTS
====================

These constants refer to commands that can be called.

``@LOOK`` 1 argument (direction).  It will push a identification constant
onto your stack, depending on what is located within that targeted grid cell.

``@MOVE`` 1 argument (direction).  Move your bot into the direction provided.
Pushes a 1 or 0 onto the stack depending if the move succeeded.

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

``@INSPECT`` 2 arguments (direction, attribute). Pushes onto your stack the
value or constant representing the attribute of target. For example,
``CALLFF << @INSPECT @HERE @CHARGE 3`` will return the charge of your own bot.

``@PUNCH`` 1 argument (direction). Punch a bot in the direction provided. If
the bot is killed, it leaves a resource.

``@CHARGEUP`` 1 argument (val). Deplete your resources by value provided, and
increase the stored charge on your bot by the same amount. You can use
this charge to later fire lasers with ``@PEWPEW``.

::
    
    Notes:
    DO NOT: ``@CHARGEUP`` more than ``10``, or your bot will blow up.
    DO NOT: Have more than ``50`` charge total on your bot, or it will explode
    ``@MOVE`` taken while you have a charge depletes your charge by ``5``
    ``@PUSH`` or ``@PUNCH`` taken with a charge depletes it by ``10``
    You can ``@INSPECT`` your own charge (or other players) using ``@INSPECT``

``@PEWPEW`` 1 argument (direction). Fire a laser in direction. The laser will
traverse the grid 1 cell per 10 units of charge you have stored. (Since the
limit is 50 charge, the laser is limited to 5 cells).

::
    
    Notes:
    Laser goes through targets, so one laser can destroy multiple targets.
    Unlike punching, this does not leave resources.


``@SELFDESTRUCT`` No arguments. Kill your bot.

DIRECTION CONSTANTS
===================

``@NORTH``, ``@SOUTH``, ``@EAST``, and ``@WEST``.

These constants refer to directions, and are used for commands that target
an adjacent cell (like ``@LOOK`` and ``@MOVE``.

IDENTIFICATION CONSTANTS
========================

These constants are returned by ``@LOOK`` and ``@SCAN``:

``@CELL_EMPTY`` is returned for empty cells.

``@CELL_RESOURCE`` is returned for gatherable resources.

``@CELL_ROBOT`` is returned for robots.

================
EXECUTION LIMITS
================

In general, these limits aren't meant to restrict your bot, but more to keep
runaway code from exploding the server. If these limits end up too limiting,
we will consider raising them.

::
    
    # Parse Limits
    Line Limit: 1000 lines of code
    Constant Limit: 500 constants (does not include injected constants by FFI)
    
    # Execution limits
    Data Stack: 500 values
    Reg Stack: 500 variables
    Exe Stack: 500 return jumps

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

