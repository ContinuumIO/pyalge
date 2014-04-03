"""
A simple calculator example that implements addition and subtraction.

Notice how the more specific pattern is matched.
"""

from __future__ import print_function, absolute_import
from alge import datatype, Case, of

Add = datatype("Add", ["lhs", "rhs"])
Sub = datatype("Sub", ["lhs", "rhs"])
Num = datatype("Num", ["val"])


class calc(Case):
    @of("Add(Num(a), Num(b))")
    def add_num(self, a, b):
        print("add_num", self.value)
        return a + b

    @of("Sub(Num(a), Num(b))")
    def sub_num(self, a, b):
        print("sub_num", self.value)
        return a - b

    @of("Add(a, b)")
    def add_expr(self, a, b):
        print("add_expr", self.value)
        return calc(a) + calc(b)

    @of("Sub(a, b)")
    def sub_expr(self, a, b):
        print("sub_expr", self.value)
        return calc(a) - calc(b)

    @of("Num(n)")
    def num(self, n):
        print("num", self.value)
        return n


def main():
    expr = Add(Num(1), Sub(Num(3), Num(2)))
    result = calc(expr)
    print("result =", result)
    assert result == (1 + (3 - 2))


if __name__ == '__main__':
    main()
