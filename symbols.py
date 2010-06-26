'''
PyQuery - The Python Object Query System
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: symbols.py
Purpose: Objects and functions representing components of a query.
'''

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

class KeyValuePair(object):
	def __init__(self, key, value):
		self.key = key
		self.value = value
	def __repr__(self): return str(self)
	def __str__(self): return "<key:%s, value:%s>" % (self.key, self.value)

def attributeValue(attribute_list, scalar=False, context='locals'):
	def expand(objs, obj, attr, x=None):
		if x == None: x = getattr(obj, attr.name)
		if attr.callchain:
			for call in attr.callchain:
				p = list()
				for param in call.params:
					if isinstance(param, type(value)) and value.func_code == param.func_code or \
						isinstance(param, type(value)) and hasattr(param, '__objquery__'):
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
		#if context == 'self': return objs[context]
		attr0 = attribute_list[0]
		obj = expand(objs, objs, attr0, objs[attr0.name])
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

def setoperator(op):
	if op == '|': return lambda x,y: x | y
	if op == '&': return lambda x,y: x & y
	if op == '-': return lambda x,y: x - y
	raise Exception, "operator %s not found" % op

def setexprOperator1(op):
	if op == 'in': return lambda x,y: x in y
	if op == 'not in': return lambda x,y: x not in y
	raise Exception, "operator %s not found" % op

def setexprOperator2(op):
	if op == 'is': return lambda x,y: x == y
	if op == 'is not': return lambda x,y: x != y
	if op == 'subset': return lambda x,y: x <= y
	if op == 'superset': return lambda x,y: x >= y
	if op == 'proper subset': return lambda x,y: x < y
	if op == 'proper superset': return lambda x,y: x > y
	raise Exception, "operator %s not found" % op

def booleanOperator(op):
	if op == 'and': return lambda x,y: x and y
	if op == 'or':  return lambda x,y: x or y
	raise Exception, "operator %s not found" % op

def unaryOperator(op):
	if op == 'not': return lambda x: not x
	raise Exception, "operator %s not found" % op

def comparisonValue(value1, op, value2):
	def value(objs):
		return op(value1(objs), value2(objs))
	return value

def setValue(s1, op, s2):
	def query(glbls):
		return op(s1(glbls), s2(glbls))
	object.__setattr__(query, '__objquery__', True)
	return query

def setexprValue1(val, op, s):
	def value(objs):
		return op(val(objs), s(objs))
	return value

def setexprValue2(s1, op, s2):
	def value(objs):
		return op(s1(objs), s2(objs))
	return value

def booleanexprValue(value1, op, value2):
	def value(objs):
		return op(value1(objs), value2(objs))
	return value

def unaryexprValue(op, val):
	def value(objs):
		return op(val(objs))
	return value

def booleanValue(val):
	def value(objs):
		return bool(val(objs))
	return value

def whereValue(where):
	def value(objs):
		return where(objs)
	return value

def queryValue(q):
	attrs = q
	def query(objs):
		def select(objs, attrs):
			def add(queue, u, v, i):
				args = (v, '_objquery__i', i+1)
				try:
					object.__setattr__(*args)
				except TypeError:
					setattr(*args)
				except:
					raise
				queue.appendleft(v)
			queue = deque()
			add(queue, None, type('base', (object,), objs), -1)
			while len(queue) > 0:
				u = queue.pop()
				i = object.__getattribute__(u, '_objquery__i')
				attrname, where = attrs[i]
				if hasattr(u, attrname):
					v = getattr(u, attrname)
					if not isinstance(v, basestring) and hasattr(v, '__iter__'):
						for z in v:
							if isinstance(v, dict):
								next = KeyValuePair(z, v[z])
							else:
								next = z
							if where != None:
								cobjs = dict(objs)
								cobjs.update({'self':next})
								if not where(cobjs): continue
							if i+1 == len(attrs): yield next
							else: add(queue, u, next, i)
					else:
						if where != None:
							cobjs = dict(objs)
							cobjs.update({'self':v})
							if not where(cobjs): continue
						if i+1 == len(attrs): yield v
						else: add(queue, u, v, i)
		return set(select(objs, attrs))
	object.__setattr__(query, '__objquery__', True)
	return query

def quantifiedValue(mode, name, s, where):
	def value(objs):
		nobjs = s(objs)
		if not nobjs: return False
		if mode == 'every':
			r = True
			#import pdb
			#pdb.set_trace()
			for x in nobjs:
				cobjs = dict(objs)
				cobjs.update({name:x})
				if not where(cobjs):
					r = False
			return r
		elif mode == 'some':
			for x in nobjs:
				cobjs = dict(objs)
				cobjs.update({name:x})
				if where(cobjs):
					return True
			return False
		raise Exception, "mode '%s' is not 'every' or 'some'" % mode
	return value
