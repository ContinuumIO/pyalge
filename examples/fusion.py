"""
Function fusion example.

Fusing map operations together.
"""
from __future__ import print_function, absolute_import
from alge import datatype, Case, of

Map = datatype("Map", ["func", "value"])
Fuse = datatype("Fuse", ["first", "second"])
Func = datatype("Func", ["name"])
Var = datatype("Var", ["name"])


class fuse(Case):
    @of("Map(fa, Map(fb, val))")
    def fuse_map(self, fa, fb, val):
        print("fusing", self.value)
        return fuse(Map(Fuse(fb, fa), fuse(val)))

    def otherwise(self, value):
        return value


def main():
    expr = Map(Func("mul"), Map(Func("sub"), Map(Func("add"), Var("x"))))
    print("original", expr)
    fused = fuse(expr)
    print("fused", fused)
    expect = Map(Fuse(Func("add"), Fuse(Func("sub"), Func("mul"))), Var("x"))
    assert expect == fused


if __name__ == '__main__':
    main()
