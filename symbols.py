
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

def attributeValue(attribute_list, context='locals'):
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
		attr0 = attribute_list[0]
		obj = expand(objs, objs[context], attr0, objs[context][attr0.name])
		for attr in attribute_list[1:]:
			print attr, obj
			if hasattr(obj, attr.name):
				obj = expand(objs, obj, attr)
			else:
				raise Exception, "object %s did not have attr %s" % (str(obj), attr.name)
		return obj
	return value
