from __future__ import print_function, absolute_import
from alge import (datatype, Case, of, MissingCaseError, LazyCase,
                  _PatternParser, PatternSyntaxError)
import unittest

Color = datatype('Color', ['red', 'green', 'blue'])
Record = datatype('Record', ['color', 'intensity'])


class MyCase(Case):
    @of("Record(Color(r, g, b), intensity)")
    def record(self, r, g, b, intensity):
        return (r + g + b) * intensity

    @of("Color(r, g, _)")
    def red_green(self, r, g):
        return r + g


class ElseCase(Case):
    @of("Record(c, i)")
    def record(self, c, i):
        return c, i

    def otherwise(self, value):
        return ("Bad", value)


class StateCase(Case):
    @of("Record(c, i)")
    def record(self, c, i):
        self.state.value = c + i


Branch = datatype("Branch", ['left', 'right'])
Node = datatype("Node", ["value"])


class SearchTree(LazyCase):
    @of("Branch(a, b)")
    def branch(self, a, b):
        """Search the leftmost subtree first.
        Then, try the right subtree
        """
        print("at", self.value)
        yield self.recurse(a)
        yield self.recurse(b)

    @of("Node(x)")
    def node(self, x):
        print("at", self.value)
        if self.state == x:
            yield x


class TestMyCase(unittest.TestCase):
    def test_nested(self):
        rec = Record(color=Color(red=1, green=2, blue=3), intensity=123)
        got = MyCase(rec)
        expect = ((rec.color.red + rec.color.green + rec.color.blue) *
                  rec.intensity)
        self.assertEqual(got, expect)

    def test_error(self):
        try:
            MyCase(Record(color=321, intensity=123))
        except MissingCaseError:
            pass
        else:
            raise AssertionError("invalid case match")

    def test_simple(self):
        c = Color(red=2, green=3, blue=4)
        got = MyCase(c)
        expect = c.red + c.green
        self.assertEqual(got, expect)


class TestElseCase(unittest.TestCase):
    def test_matching(self):
        r = Record(1, 2)
        got = ElseCase(r)
        expect = r.color, r.intensity
        self.assertEqual(got, expect)

    def test_otherwise(self):
        r = Color(1, 2, 3)
        got = ElseCase(r)
        expect = ("Bad", r)
        self.assertEqual(got, expect)


class TestStateCase(unittest.TestCase):
    def test_matching(self):
        class State(object):
            def __init__(self):
                self.value = 0

        r = Record(1, 2)
        state = State()
        StateCase(r, state=state)
        got = state.value
        expect = r.color + r.intensity
        self.assertEqual(got, expect)


class TestSearchTree(unittest.TestCase):
    def test_matching(self):
        tree = Branch(Branch(Node(1), Branch(Node(2, ), Node(5))),
                      Branch(Node(3), Node(4)))
        print(tree)
        st = SearchTree(tree, state=3)
        self.assertEqual(3, st.force())


class TestParser(unittest.TestCase):
    def parse(self, pat):
        parser = _PatternParser(pat, globals())
        parser.parse()
        return parser.result

    def test_missing_rpar(self):
        import tokenize

        pat = "Record(a,"
        try:
            self.parse(pat)
        except tokenize.TokenError:
            pass
        else:
            self.fail("error expected")

    def test_trailing_comma(self):
        pat = "Record(a,)"
        self.parse(pat)

    def test_num(self):
        pat = "Record(1)"
        try:
            self.parse(pat)
        except PatternSyntaxError:
            pass
        else:
            self.fail("error expected")


if __name__ == '__main__':
    unittest.main()
