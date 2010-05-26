
from collections import deque

class Query(object):

	def __init__(self, select):
		self.select = select

def query(obj, q):
	attrs = q
	def select(obj, attrs):
		def add(queue, u, v, i):
			setattr(v, '_objquery__i', i+1)
			queue.appendleft(v)
		queue = deque()
		add(queue, None, type('base', (object,), {attrs[0][0]:obj}), -1)
		while len(queue) > 0:
			u = queue.pop()
			i = getattr(u, '_objquery__i')
			attrname, where = attrs[i]
			print u, attrname, where
			if hasattr(u, attrname):
				v = getattr(u, attrname)
				if not isinstance(v, basestring) and hasattr(v, '__iter__'):
					for z in v:
						if where != None:
							if not where(z): continue
						if i+1 == len(attrs): yield z
						else: add(queue, u, z, i)
				else:
					if where != None:
						if not where(v): continue
					if i+1 == len(attrs): yield v
					else: add(queue, u, v, i)
	return select(obj, attrs)

if __name__ == '__main__':
	import example
	a = example.A(1)
	def acheck(a):
		return a.n == 1
	print list(query(a, [('a', None),('b', acheck),('c', None),('n', None)]))
