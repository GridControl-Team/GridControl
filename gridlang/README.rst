========
GRIDLANG
========

GridLang is a language created for the GridControl game. It is an
interpreted, procedural, stack-based language at the core having
just integar and float datatypes.

The VM it runs on is also interesting in that it was designed so
that the execution state can be suspended and serialized to be
reanimated at a later time.

EXECUTABLE ENVIRONMENT
======================

GridLang runs in a VM with the following components:

* DataStack (primary data stack) - the stack on which all operations operate
* ExecStack (internal executable stack) - used currently for GOTOs, and
  eventually function calls
* Registry (Key-Value store) - named value store, useful for binding some value
  to a label

================
WRITING GRIDLANG
================

Executing GridLang
==================

::
    
    python gridlang.py somefile.gridlang


GridLang Tutorial
=================

GridLang is stack-based, and most operations are designed to operate from
values on the stack, so instead of writing ``1 + 2`` like most other
languages, in GridLang it looks like this:

::
    
    PUSH 1
    PUSH 2
    PLUS
    PRINT

Execution starts at the top of the code, with an empty stack (``[]``).
``PUSH 1`` pushes a ``1`` on top of the stack (stack is now ``[1]``).
``PUSH 2`` pushes a ``2`` on the stack (stack is now ``[1, 2]``).
``PLUS`` pulls two values off the stack (stack becomes ``[]`` again), adds them
together and pushes the resulting value on the stack (so stack is now ``[3]``).
THe last line takes the top value (``3``) and prints it.

GridLang supports named variables using the registry.  To store a value
in the registry, do the following:

::
    
    PUSH 1
    STORE foo

After this executes, the stack is now empty (``[]``, since the value ``STORE``
stores is popped off the stack).  After registering ``foo``, you can now
``PUSH`` it's value:

::
    
    PUSH foo
    PRINT

This will print ``1``.

Since ``PUSH`` is a very common operation, GridLang supports a simple sugar
using ``<<``.  Any value following ``<<`` is pushed onto the stack before
the operation procedes.  Thus, the following:

::
    
    ADD << 1 1 
    SUB << foo bar

Is exactly equivalent to:

::
    
    PUSH 1
    PUSH 1
    ADD
    PUSH foo
    PUSH bar
    SUB

Note that ``<<`` does not care about the arity of the operation, thus it is
legal to do ``ADD << 1 2 3`` (``ADD`` will add 2 + 3) or ``ADD << 1`` (add will
add 1 + whatever is on top of the stack).


GridLang Operations
===================

Stack Operations
----------------

=======  =====  =====  ======  ================================================
Command  Args   Pops   Pushes  Description
=======  =====  =====  ======  ================================================
PUSH     <VAL>  0      1       PUSH <VAL> on stack
POP      --     1      0       Discard top value from stack
SWAP     --     2      2       Take top two values from stack and swap them
DUP      --     1      2       Take top value of stack and duplicate it
HERE     --     0      1       Returns current location of stack
PEEK     --     1      1       Push value at given location in stack
POKE     --     2      0       Take a, b from stack, and set location a in
                               stack to value b
=======  =====  =====  ======  ================================================

Registry Operations
-------------------

=======  =====  =====  ======  ================================================
Command  Args   Pops   Pushes  Description
=======  =====  =====  ======  ================================================
STORE    <KEY>  1      0       Takes value from stack and stores it in the
                               registry under <KEY>
=======  =====  =====  ======  ================================================

Arithmetic Operations
---------------------

=======  =====  =====  ======  ================================================
Command  Args   Pops   Pushes  Description
=======  =====  =====  ======  ================================================
PLUS     --     2      1       Add two values from stack
MINUS    --     2      1       Subtract two values from stack
MUL      --     2      1       Multiply two values from stack
DIV      --     2      1       Take a, b from stack and push a / b
MIN      --     2      1       Take a, b from stack and push the lesser value
MAX      --     2      1       Take a, b from stack and push the larger value
=======  =====  =====  ======  ================================================

Logical Operations
------------------

=======  =====  =====  ======  ================================================
Command  Args   Pops   Pushes  Description
=======  =====  =====  ======  ================================================
GREATER  --     2      1       Take a, b from stack and push 1 if a > b else 0
LESS     --     2      1       Push 1 if a < b else 0
EQUAL    --     2      1       Push 1 if a == b else 0
=======  =====  =====  ======  ================================================

Control Flow Operations
-----------------------

=======  =====  =====  ======  ================================================
Command  Args   Pops   Pushes  Description
=======  =====  =====  ======  ================================================
GOTO     --     1      0       Take value from stack and jump to that line
IFTGOTO  <LN>   1      0       If value from stack is > 0, jump to <LN>
IFFGOTO  <LN>   1      0       If value from stack is 0, jump to <LN>
=======  =====  =====  ======  ================================================

Debugging Operations
--------------------

=======  =====  =====  ======  ================================================
Command  Args   Pops   Pushes  Description
=======  =====  =====  ======  ================================================
PRINT    --     1      0       Take top value from stack and output it
PANIC    --     0      0       Raise an exception and provide a trace
END      --     0      0       Stop execution
=======  =====  =====  ======  ================================================

