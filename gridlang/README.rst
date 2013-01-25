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

This will print ``1``. Keys can be anything that isn't a literal.

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

Constants and Control Flow
--------------------------

Constants are determined at compile time, either introduced to the VM from
an outside source (in the case of running code in GridControl, the game
introduces some constants to represent bot commands and the cardinal
directions), or introduced in code.  A constant is just any label prefixed
with ``@``:

::
    
    @MYCONSTANT

A constant by itself on a line defines the constant. In this case, since
``@MYCONSTANT`` is on line 1 of the code, its value is now set to ``1``, and
any reference to ``@MYCONSTANT`` is replaced at compile time with ``1``. Thus,
the following code:

::
    
    @MYCONSTANT
    PRINT << @MYCONSTANT

compiles to:

::
    
    (empty line)
    PRINT << 1

Compilation does two passes to determine constants, so constants can be used
even if they are defined later in the code.  This makes constants very useful
as labels for ``GOTO`` and other control flow operations:

::
    
    GOTO << @MAIN
    PRINT << 0
    
    @MAIN
    EXIT

In the first pass, ``@MAIN`` is set to 4, and in the second pass, the ``GOTO``
is compiled to ``GOTO << 4`` (technically ``PUSH 4; GOTO``, remember that
``<<`` is sugar).  In this example, no output is actually printed, since
execution jumps to the end of the program right away.

A user defined constant is done by appending a scalar value after the constant
definition.

::
    
    @MY_CONSTANT 10
    
    PRINT << @MY_CONSTANT

Will print out ``10``.


Functions/Macros
----------------

Call them functions or macros, gridlang supports jumps using ``CALL`` and
``RETURN`` operators that can jump to some piece of code and later return
back to where it jumped from. Because gridlang keeps these jump states in
a separate stack (the ExecStack), these calls can be nested as far as the
stack allows.

This enables compartmentalizing or reusing code.  Here is a contrived 
example:

::
    
    @MAIN
    PUSH 1
    CALL << @MYOWNPRINT
    PUSH 2
    CALL << @MYOWNPRINT
    EXIT

    @MYOWNPRINT
    PRINT
    RETURN


Loops
-----

Loops are done using the ``DO`` and ``LOOP`` operators.  ``DO`` takes
two arguments, the limit and the index.  The loop begins at ``DO`` with the
provided index, which is increment when the code approaches ``LOOP``.  If
the index equals the limit, execution continues, else it jumps back to the
``DO``

::
    
    PUSH 1
    DO << 10 0 # do ten times
    MUL << 2 # double number every loop
    LOOP
    PRINT # outputs 1024 (i.e., 2 ^ 10)

Strings
-------

Gridlang has limited support for text.  In general, gridlang supports ascii
by representing each character using their byte value.  ``PRINTSTR`` takes
a length, pops that number of values from the stack, convert to characters
before outputting to console.  Thus, the following is a way to write a
helloworld program:

::
    
    << 72 101 108 108 111 32 87 111 114 108 100 33 12
    PRINTSTR << 13

Gridlang also supports char literals, which in the compiler get replaced
by their byte value.  Thus, this is a read-friendly way to write helloworld:

::
    
    << 'H' 'e' 'l' 'l' 'o' ' ' 'W' 'o' 'r' 'l' 'd' '!'
    PRINTSTR << 13


GridLang Operations
===================

Stack Operations
----------------

=======  =====  =====  ======  ================================================
Command  Args   Pops   Pushes  Description
=======  =====  =====  ======  ================================================
PUSH     <VAL>  0      1       PUSH <VAL> on stack
POP      --     1      0       Discard top value from stack
POPN     --     1+x    0       Take value x from stack, and then discard top x
                               values from stack
SWAP     --     2      2       Take top two values from stack and swap them
DUP      --     1      2       Take top value of stack and duplicate it
DUPN     --     2      ?       Take v, n from stack. Pushes n numbers of v
HERE     --     0      1       Returns current location of stack
PEEK     --     1      1       Push value at given location in stack
POKE     --     2      0       Take x, addr from stack, and set location addr
                               in stack to value x
PEEKN    --     2      1       Take addr, l from stack, and push a slice of
                               data at location addr in stack (with length l)
                               to the top of the stack
POKEN    --     2      0       Take addr, l from stack, then take a slice of
                               data (length l) from top of stack and write it
                               into the stack at location addr
RAND     --     1      1       Take x from stack, and push random integer
                               between (0, x) inclusive
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
MODULO   --     2      1       Take a, b from stack and push a % b
ABS      --     1      1       Take a from stack and push abs(a)
NEG      --     1      1       Take a from stack and push -a
=======  =====  =====  ======  ================================================

Logical Operations
------------------

=======  =====  =====  ======  ================================================
Command  Args   Pops   Pushes  Description
=======  =====  =====  ======  ================================================
GREATER  --     2      1       Take a, b from stack and push 1 if a > b else 0
LESS     --     2      1       Push 1 if a < b else 0
EQUAL    --     2      1       Push 1 if a == b else 0
NEQUAL   --     2      1       Push 1 if a != b else 0
AND      --     2      1       Push 1 if a && b else 0
OR       --     2      1       Push 1 if a || b else 0
=======  =====  =====  ======  ================================================

Bitwise Operations
------------------

All operands must be integers.

=======  =====  =====  ======  ================================================
Command  Args   Pops   Pushes  Description
=======  =====  =====  ======  ================================================
BNOT     --     1      1       Take a from stack and push ~a
BAND     --     2      1       Take a, b from stack and push a & b
BOR      --     2      1       Take a, b from stack and push a | b
BXOR     --     2      1       Take a, b from stack and push a ^ b
=======  =====  =====  ======  ================================================

Control Flow Operations
-----------------------

=======  =====  =====  ======  ================================================
Command  Args   Pops   Pushes  Description
=======  =====  =====  ======  ================================================
GOTO     --     1      0       Take value from stack and jump to that line
IFTGOTO  --     2      0       If v, j from stack. if v > 0, jump to j
IFFGOTO  --     2      0       If v, j from stack, if v <= 0, jump to j
CALL     --     1      0       Take value from stack and call to that line
IFTCALL  --     2      0       If v, j from stack, if v > 0, call j
IFFCALL  --     2      0       If v, j from stack, if v <= 0, call j
RETURN   --     -      -       Pops from the exec stack, returning to where you
                               last ``CALL``-ed from.
DO       --     2      0       Takes limit, index from stack, and beings a loop
LOOP     --     -      -       Increments loop index, if it is less than limit,
                               jump back to matching DO, else continue
                               execution
=======  =====  =====  ======  ================================================

Output Operations
-----------------

========  =====  =====  ======  ===============================================
Command   Args   Pops   Pushes  Description
========  =====  =====  ======  ===============================================
PRINT     --     1      0       Take top value from stack and output it
PRINTSTR  --     1+?    0       Take l from stack, then take top l values from
                                stack and output as string
========  =====  =====  ======  ===============================================

Debugging Operations
--------------------

=======  =====  =====  ======  ================================================
Command  Args   Pops   Pushes  Description
=======  =====  =====  ======  ================================================
PANIC    --     0      0       Raise an exception and provide a trace
END      --     0      0       Stop execution
=======  =====  =====  ======  ================================================

Foreign Function Interface
--------------------------

=======  =====  =====  ======  ================================================
Command  Args   Pops   Pushes  Description
=======  =====  =====  ======  ================================================
CALLFF   --     1+?    0       Take top value from stack as n. Then takes n
                               values from stack and sends that to FFI
=======  =====  =====  ======  ================================================
