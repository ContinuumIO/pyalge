"""
PyAlge

(Algae mascot)

Inspired by PyAlgebraicDataTypes for algebraic data types (ADT) and pattern
matching.
However, PyAlgebraicDataTypes is Py3.3 only and I (sklam) think that I can
do pattern matching in a simpler fashion (no metaclasses, eval/exec, ...).

Why?
----

I wrote compilers and functional pattern matching in functional
language is a bless; esp, when one compare to the visitor pattern in Python.
Duck-typing is nice for loosely coupled components.  But compiler IR and its
transformations are high cohesion components.  It is fine or even necessary
for high cohesion components to be coupled in the type-domain so that one can
match/dispatch on type information and type structures.

This library shall allow one to express abstract semantic information in the
type-domain through ADT.  Pattern matching allows code logic to be loosely
attached to types in an extensible manner.  The compiler IR data structure
should not contain logic.  Logic should be defined in the transformations.

The use of ADT and pattern matching adds structure to code.  They enforces
integrity of code.  Use ADT to add semantic information.  Pattern matching
enforces the semantic requirements.

Reference
---------

- https://github.com/benanhalt/PyAlgebraicDataTypes

"""

from __future__ import print_function, absolute_import
from collections import namedtuple
import functools
import tokenize


class MissingCaseError(ValueError):
    pass


class PatternSyntaxError(ValueError):
    pass


class NoMatch(object):
    """Used internally to indicate where a case does not match.
    """
    pass


class Case(object):
    """A case-class is used to describe a pattern matching dispatch logic.
    Each pattern is described as a method with the `of` decorator.

    Details
    -------
    The `__new__` method of Case is overridden to not return an instance of
    Case.  One will use a subclass of Case as a function.
    """

    def __new__(cls, value):
        if not hasattr(cls, "_case_ofs"):
            # First time running.
            # Prepare dispatch table.
            cls.__prepare()
        obj = object.__new__(cls)
        return obj.__process(value)

    @classmethod
    def __prepare(cls):
        """Insert "_case_ofs" attribute to the class
        """
        ofs = []
        for fd in dir(cls):
            if not fd.startswith('_') and fd != 'otherwise':
                fn = getattr(cls, fd)
                firstline = fn._inner.func_code.co_firstlineno
                ofs.append((firstline, fn))
                # Order cases by lineno
        cls._case_ofs = zip(*sorted(ofs))[1]

    def __process(self, value):
        """The actual matching/dispatch.
        Returns the result of the match.
        """
        ofs = self._case_ofs
        for case in ofs:
            res = case(self, value)
            if res is not NoMatch:
                # Matches
                return res
                # Run default
        return self.otherwise(value)

    def otherwise(self, value):
        """Default is to raise MissingCaseError exception with `value` as
        argument.

        Can be overridden.
        """
        raise MissingCaseError(value)


class _TypePattern(namedtuple("_TypePattern", ["name", "body"])):
    def match(self, match, input):
        if type(input).__name__ == self.name:
            if len(self.body) != len(input):
                # Insufficient fields
                return
            # Try to match the fields
            for field, fdvalue in zip(self.body, input):
                m = field.match(_Match(), fdvalue)
                if m is not None:
                    match.bindings.update(m.bindings)
                else:
                    return
            return match


class _Binding(namedtuple("Binding", ["name"])):
    def match(self, match, input):
        assert self.name not in match.bindings, "duplicated binding"
        match.bindings[self.name] = input
        return match


class _Ignored(object):
    def match(self, match, input):
        return match


class _PatternParser(object):
    """Pattern parser

    Overhead of the library will almost likely be in parsing.  Luckily,
    we parse once at class creation.
    """

    def __init__(self, pat):
        self.pat = pat
        self.bindings = set()

        lines = iter(self.pat.split())
        tokens = tokenize.generate_tokens(lambda: next(lines))
        self._nexttoken = lambda: next(tokens)
        self.pbtok = None
        self.result = None

    def get_token(self):
        if self.pbtok:
            token, self.pbtok = self.pbtok, None
        else:
            token = self._nexttoken()
        return token

    def putback(self, token):
        assert self.pbtok is None, "internal error: lookahead(1)"
        self.pbtok = token

    def parse(self):
        typename = self.expect_name()
        self.result = self.parse_typebody(typename)

    def parse_typebody(self, typename):
        if not typename[0].isupper():
            raise PatternSyntaxError("type name must start with uppercase "
                                     "letter")
        self.expect_lparen()
        body = []
        while True:
            body.append(self.expect_type_or_binding())
            if not self.is_comma():
                break
        self.expect_rparen()
        return _TypePattern(typename, body)

    def expect_type_or_binding(self):
        name = self.expect_name()
        if name[0].isupper():
            # is type
            return self.parse_typebody(name)
        else:
            # is binding
            return self.parse_binding(name)

    def parse_binding(self, name):
        ignored = name[0].startswith('_')
        if not name[0].islower() and not ignored:
            raise PatternSyntaxError("binding name must start with lowercase "
                                     "letter")
        if ignored:
            return _Ignored()
        else:
            return _Binding(name)

    def expect_name(self):
        token = self.get_token()
        tokty, tokstr = token[:2]
        if tokty != tokenize.NAME:
            raise PatternSyntaxError("expected name: %r" % tokstr)
        return tokstr

    def expect_lparen(self):
        token = self.get_token()
        tokstr = token[1]
        if tokstr != '(':
            raise PatternSyntaxError("expected '('; got %r" % tokstr)

    def expect_rparen(self):
        token = self.get_token()
        tokstr = token[1]
        if tokstr != ')':
            raise PatternSyntaxError("expected ')'; got %r" % tokstr)

    def is_comma(self):
        token = self.get_token()
        tokstr = token[1]
        if tokstr != ',':
            self.putback(token)
            return False
        else:
            return True


class _Match(object):
    def __init__(self):
        self.bindings = {}


def of(pat):
    """Decorator for methods of Case to describe the pattern.

    Args
    ----
    pat - str

    Patterns are like writing tuples (of tuples (of ...)) for the type
    structure to match against.  Names starting with a lowercase letter are
    used as binding slots that the matcher will capture and used as argument
    to the action function, the function being decorated.  Names that starts
    with a underscore '_' is ignored.  Names starting with a uppercase letter
    are type names.
    """
    parser = _PatternParser(pat)
    parser.parse()
    matcher = parser.result

    def decor(fn):
        @functools.wraps(fn)
        def closure(self, value):
            match = matcher.match(_Match(), value)
            if match is not None:
                self.value = value
                self.match = match
                return fn(self, **match.bindings)
            else:
                return NoMatch

        closure._inner = fn
        return closure

    return decor


class Data(object):
    """Algebraic Data Type
    """
    pass


def datatype(name, fields):
    """Constructor for algebraic data type.
    Used like `collections.namedtuple`.

    Args
    ----
    name - str
        Type name.  Must start with a uppercase letter.
    fields - sequence of str
        Sequence of field names.
    """
    assert name[0].isupper(), "Type name must start with uppercase letter."
    tupcls = namedtuple(name, fields)
    return type(name, (tupcls, Data), {})

