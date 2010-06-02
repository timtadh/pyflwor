
from collections import deque

class Attribute(object):

	def __init__(self, name, callchain=None):
		self.name = name
		self.callchain = callchain
	def __repr__(self): return str(self)
	def __str__(self): return str(self.name) + "[" + str(self.callchain) + "]"

class Call(object):

	def __init__(self, params, lookup=False):
		self.params = params
		self.lookup = lookup
	def __repr__(self): return str(self)
	def __str__(self):
		if self.lookup: return "__getitem__" + str(tuple(self.params))
		return "__call__" + str(tuple(self.params))

def attributeValue(attribute_list, scalar=False, context='locals'):
	def expand(objs, obj, attr, x=None):
		if x == None: x = getattr(obj, attr.name)
		if attr.callchain:
			for call in attr.callchain:
				p = list()
				for param in call.params:
					if isinstance(param, type(value)) and value.func_code == param.func_code:
						p.append(param(objs))
					else:
						p.append(param)
				if call.lookup:
					x = x.__getitem__(p[0])
				else:
					x = x.__call__(*p)
		return x
	def value(objs):
		if scalar: return attribute_list
		if context == 'self': return objs[context]
		attr0 = attribute_list[0]
		obj = expand(objs, objs[context], attr0, objs[context][attr0.name])
		for attr in attribute_list[1:]:
			if hasattr(obj, attr.name):
				obj = expand(objs, obj, attr)
			else:
				raise Exception, "object %s did not have attr %s" % (str(obj), attr.name)
		return obj
	return value

def operator(op):
	if op == '==': return lambda x,y: x == y
	if op == '!=': return lambda x,y: x != y
	if op == '<=': return lambda x,y: x <= y
	if op == '>=': return lambda x,y: x >= y
	if op == '<': return lambda x,y: x < y
	if op == '>': return lambda x,y: x > y
	raise Exception, "operator %s not found" % op

def comparisonValue(value1, op, value2):
	def value(objs):
		return op(value1(objs), value2(objs))
	return value

def queryValue(q):
	attrs = q
	def query(obj, glbls):
		def select(obj, glbls, attrs):
			def add(queue, u, v, i):
				setattr(v, '_objquery__i', i+1)
				queue.appendleft(v)
			queue = deque()
			add(queue, None, type('base', (object,), {attrs[0][0]:obj}), -1)
			while len(queue) > 0:
				u = queue.pop()
				i = getattr(u, '_objquery__i')
				attrname, where = attrs[i]
				if hasattr(u, attrname):
					v = getattr(u, attrname)
					if not isinstance(v, basestring) and hasattr(v, '__iter__'):
						for z in v:
							if where != None:
								if not where(z, glbls): continue
							if i+1 == len(attrs): yield z
							else: add(queue, u, z, i)
					else:
						if where != None:
							if not where(v, glbls): continue
						if i+1 == len(attrs): yield v
						else: add(queue, u, v, i)
		return set(select(obj, glbls, attrs))
	return query

