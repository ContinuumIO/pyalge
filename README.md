PyAlge
======


PyAlge is inspired by PyAlgebraicDataTypes for algebraic data types (ADT) and
pattern matching.  However, PyAlgebraicDataTypes is Py3.3 only and the
implementation is very complicated.  Pattern matching can be done without
metaclasses magic and dynamic code generation.

Why?
----

We write compilers (e.g. Numba).  Compiler code has a lot of deep
if-else clauses and visitors.  They are not pretty and quite fragile.
One of the features that make writing compiler in functional languages
easier is pattern matching.  PyAlge provides similar pattern matching in
Python.

Other use of pattern matching and ADTs is the ability to
decouple type and logic.  There are many situations where attaching logic as
method to types is awkward because the logic depends on knowledge about other
types.  ADTs and pattern matching also allow logic to apply on a certain
combination of types.

Lastly, pattern matching adds structures and, thus, improves integrity.
Compiler code needs to be reliable.  Adding more structure to code helps
avoiding bugs.  Testing allow cannot discover all bugs.  Many software has
infinite number of possible input.  For compilers, it is impossible to
test every possible code path.

How?
----

Write a Case class for pattern matching logic.  It contains "actions" to
perform.  Each "action" is associated with a pattern.  Each action is tried
one-by-one in the other of in which they are defined.

```python
class MyCase(Case):
    @of("Record(Color(r, g, b), intensity)")
    def record(self, r, g, b, intensity):
        return (r + g + b) * intensity

    @of("Color(r, g, _)")
    def red_green(self, r, g):
        return r + g
```

Pattern String
--------------

The pattern is a string.  It looks like a Python tuple.  However,
names are case sensitive.  Type names start with uppercase letter.
Names start with lowercase letter is a capturing slots.  All captured values
are used as arguments to the "action" method.  Names starting with "_" are
ignored.

References
----------

- https://github.com/benanhalt/PyAlgebraicDataTypes


We need a algae mascot =)
