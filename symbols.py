
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

def attributeValue(attribute_list):
	def value(objs):
		attr0 = attribute_list[0]
		obj = None
		for o in objs:
			if hasattr(o, attr0.name):
				obj = o
				break;
		if not obj:
			raise Exception, "no object in %s had attribute %s" % (str(objs), attr0.name)
		for attr in attribute_list:
			if hasattr(obj, attr.name):
				x = getattr(obj, attr.name)
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
				obj = x
			else:
				raise Exception, "object %s did not have attr %s" % (str(obj), attr.name)
		return obj
	return value
