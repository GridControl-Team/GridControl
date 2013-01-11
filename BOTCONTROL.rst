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
    
    # Direction constants
    @NORTH
    @SOUTH
    @EAST
    @WEST

``@LOOK`` 1 argument (direction).  It will push either a 1 or
a 0 onto your stack, depending if the grid cell in the direction provided has a
resource or not.

``@MOVE`` 1 argument (direction).  Move your bot into the direction provided.
Pushes a 1 onto the stack for now (moves atm always succeed)

``@PULL`` 1 argument (direction).  Gather a resource from the direction provided.
Pushes a 1 onto the stack for now (pulls atm always succeed)
If there is a resource, your will gain a point.

``@SCAN`` 2 arguments (deltax, deltay). Like look, but peers in the grid cell
relative to current bot position (e.g., [1, 0] will look east). Pushes a 1 or
0 onto stack, depending if targeted cell has resource or not.

==================
THIS IS DEPRECATED
==================

Please use the newer ``CALLFF`` methods above. ``FFI`` will be deprecated soon
and any code that uses it will stop working!

OLD SAMPLE CODE
===============

::
    
    # This bot will continually travel south
    # pulling from the east or west if it
    # finds resources there
    @LOOPSTART
    FFI << @LOOK @EAST
    testtgoto @PULLEAST
    FFI << @LOOK @WEST
    testtgoto @PULLWEST
     
    FFI << @MOVE @SOUTH
    goto << @LOOPEND
     
    @PULLEAST
    FFI << @PULL @EAST
    goto << @LOOPEND
     
    @PULLWEST
    FFI << @PULL @WEST
    goto << @LOOPEND
     
    @LOOPEND
    goto << @LOOPSTART

OLD ABOUT CODE
==============

As you can see, control of your bot is exposed using gridlang's
FFI operation.  GridControl automatically injects a number of
constants necessary to manipulate your bot. The constants are:

::
    
    # Action constants
    @LOOK
    @PULL
    @MOVE
    
    # Direction constants
    @NORTH
    @SOUTH
    @EAST
    @WEST

``@LOOK`` action will push either a 1 or a 0 onto your stack,
depending if the grid cell in the direction provided has a
resource or not.

``@MOVE`` action will move your bot into the direction provided.
Pushes a 1 onto the stack for now (moves atm always succeed)

``@PULL`` action will gather a resource from the direction provided.
Pushes a 1 onto the stack for now (pulls atm always succeed)
If there is a resource, your will gain a point.
