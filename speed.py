from __future__ import print_function
from alge import Case, of, datatype
from timeit import repeat

Op = datatype("Op", ['a', 'b'])

class Do(Case):
	@of("Op(a, b)")
	def op(self, a, b):
		return a + b


class Visitor(object):
	def visit(self, val):
		fn = getattr(self, "visit_%s" % type(val).__name__)
		return fn(val)
	def visit_Op(self, val):
		return val.a + val.b


args = 1, 2
op = Op(*args)
t_alge = min(repeat(lambda: Do(op), repeat=3, number=1000))
t_vis = min(repeat(lambda: Visitor().visit(op), repeat=3, number=1000))
print('t_alge', t_alge)
print('t_vis ', t_vis)

