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

==========
ABOUT CODE
==========

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

``@PULL`` action will gather a resource from the direction provided.
If there is a resource, your will gain a point.
