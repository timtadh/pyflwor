'''
PyQuery - The Python Object Query System
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: symbols.py
Purpose: Objects and functions representing components of a query.
'''
from __future__ import division
from __future__ import absolute_import
from builtins import zip
from builtins import str
from builtins import range
from past.utils import old_div
from builtins import object

import collections
from collections import deque
from itertools import product

try:
    from .OrderedSet import OrderedSet
except SystemError:
    from OrderedSet import OrderedSet

class Attribute(object):
    '''
    Represents an attribute. An attribute consists of a name and a
    "callchain." The callchain represent one or more function or index lookups
    being performed on the attribute.

    eg.
        x(1,2,3)[1]()

    translates to:
        self.name = 'x'
        self.callchain = [Call([1,2,3]), Call([1], True), Call([])]
    '''
    def __init__(self, name, callchain=None):
        self.name = name
        self.callchain = callchain
    def __repr__(self): return str(self)
    def __str__(self): return str(self.name) + "[" + str(self.callchain) + "]"

class Call(object):
    '''
    Represent a 'Call' (for context see the documentation on the Attribute
    class). A call consists of the parameters passed into the call (themselves
    functions which takes the namespace (objs)) and whether not this is an item
    lookup rather than a function call.
    '''
    def __init__(self, params, lookup=False):
        self.params = params
        self.lookup = lookup
    def __repr__(self): return str(self)
    def __str__(self):
        if self.lookup: return "__getitem__" + str(tuple(self.params))
        return "__call__" + str(tuple(self.params))

class KeyValuePair(object):
    '''
    Represents a key,value pair for use while iterating over a dictionary.
    '''
    def __init__(self, key, value):
        self.key = key
        self.value = value
    def __repr__(self): return str(self)
    def __str__(self): return "<key:%s, value:%s>" % (self.key, self.value)

def attributeValue(attribute_list, scalar=False, context='locals'):
    '''
    Transforms a AttributeValue into its actual value.

    eg.
        x.y.z().q[1].r
        attribute_list = [Attribute('x'), Attribute('y'),
            Attribute('z',[Call([])]),  Attribute('q', [Call([1], True)]),
            Attribute('r')]

    translates into the attribute lookups, function calls, and __getitem__ calls
    necessary to produce a value.

    if scalar == True:
        it simply returns the value stored in attribute_list

    context is no longer used and should be removed.
    '''

    def expand(objs, obj, attr, x):
        '''
        Expands the the value of one attribute by looking the name up in the
        objs dict and then performing and function calls and dictionary lookups
        specified in the callchain.
        '''
        if attr.callchain:
            for call in attr.callchain:
                p = list()
                for param in call.params:
                    if isinstance(param, type(value)) and value.__code__ == param.__code__ or \
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
        '''
        The computation function returned the user. Computes the actual value
        of the the attribute expression when @objs is passed in.
        '''
        if scalar: return attribute_list
        #if context == 'self': return objs[context]
        attr0 = attribute_list[0]
        obj = expand(objs, objs, attr0, objs[attr0.name])
        for attr in attribute_list[1:]:
            if hasattr(obj, attr.name):
                obj = expand(objs, obj, attr, getattr(obj, attr.name))
            else:
                raise Exception("object %s did not have attr %s" % (str(obj), attr.name))
        return obj

    return value

def operator(op):
    '''
    Returns a function which performs comparision operations
    '''
    if op == '==': return lambda x,y: x == y
    if op == '!=': return lambda x,y: x != y
    if op == '<=': return lambda x,y: x <= y
    if op == '>=': return lambda x,y: x >= y
    if op == '<': return lambda x,y: x < y
    if op == '>': return lambda x,y: x > y
    raise Exception("operator %s not found" % op)

def arith_operator(op):
    '''
    Returns a function which performs arithmetic operations
    '''
    if op == '+': return lambda x,y: x + y
    if op == '-': return lambda x,y: x - y
    if op == '*': return lambda x,y: x * y
    if op == '/': return lambda x,y: old_div(x, y)
    raise Exception("operator %s not found" % op)

def setoperator(op):
    '''
    Returns a function which performs set operations
    '''
    if op == '|': return lambda x,y: x | y
    if op == '&': return lambda x,y: x & y
    if op == '-': return lambda x,y: x - y
    raise Exception("operator %s not found" % op)

def setexprOperator1(op):
    '''
    Returns a function which performs scalar in set operations
    '''
    if op == 'in': return lambda x,y: x in y
    if op == 'not in': return lambda x,y: x not in y
    raise Exception("operator %s not found" % op)

def setexprOperator2(op):
    '''
    Returns a function which performs set to set comparison operations
    '''
    if op == 'is': return lambda x,y: x == y
    if op == 'is not': return lambda x,y: x != y
    if op == 'subset': return lambda x,y: x <= y
    if op == 'superset': return lambda x,y: x >= y
    if op == 'proper subset': return lambda x,y: x < y
    if op == 'proper superset': return lambda x,y: x > y
    raise Exception("operator %s not found" % op)

def booleanOperator(op):
    '''
    Returns a function which performs basic boolean (and, or) operations
    '''
    if op == 'and': return lambda x,y,objs: x(objs) and y(objs)
    if op == 'or':  return lambda x,y,objs: x(objs) or y(objs)
    raise Exception("operator %s not found" % op)

def unaryOperator(op):
    '''
    Returns a function which performs unary (not) operation
    '''
    if op == 'not': return lambda x: not x
    raise Exception("operator %s not found" % op)

def comparisonValue(value1, op, value2):
    '''
    Returns a function which will calculate a where expression for a basic
    comparison operation.
    '''
    def where(objs):
        return op(value1(objs), value2(objs))
    object.__setattr__(where, '__objquery__', True)
    return where

def arithValue(value1, op, value2):
    '''
    Returns a function which will calculate a where expression for a basic
    arithmetic operation.
    '''
    def arith_value(objs):
        return op(value1(objs), value2(objs))
    object.__setattr__(arith_value, '__objquery__', True)
    return arith_value

def setValue(s1, op, s2):
    '''
    Returns a Query function for the result of set operations (difference, union
    etc..)
    '''
    def query(glbls):
        return op(s1(glbls), s2(glbls))
    object.__setattr__(query, '__objquery__', True)
    return query

def setexprValue1(val, op, s):
    '''
    Returns a where function which returns the result of a value in set
    operation
    '''
    def where(objs):
        return op(val(objs), s(objs))
    object.__setattr__(where, '__objquery__', True)
    return where

def setexprValue2(s1, op, s2):
    '''
    Returns a where function which returns the result of a set op set operation
    '''
    def where(objs):
        return op(s1(objs), s2(objs))
    object.__setattr__(where, '__objquery__', True)
    return where

def booleanexprValue(value1, op, value2):
    '''
    returns the function which computes the result of boolean (and or) operation
    '''
    def where(objs):
        return op(value1, value2, objs)
    object.__setattr__(where, '__objquery__', True)
    return where

def unaryexprValue(op, val):
    '''
    returns the function which computes the result of boolean not operation
    '''
    def where(objs):
        return op(val(objs))
    object.__setattr__(where, '__objquery__', True)
    return where

def booleanValue(val):
    '''
    returns the function which booleanizes the result of the Value function
    '''
    def where(objs):
        return bool(val(objs))
    object.__setattr__(where, '__objquery__', True)
    return where

def whereValue(val):
    '''
    returns the results of a Value function.
    '''
    def where(objs):
        return val(objs)
    object.__setattr__(where, '__objquery__', True)
    return where

def dictValue(pairs):
    '''
    creates a dictionary from the passed pairs after evaluation.
    '''
    def dictval(objs):
        return dict((name(objs), value(objs)) for name, value in pairs)
    object.__setattr__(dictval, '__objquery__', True)
    return dictval

def listValue(values):
    '''
    creates a list from the pass objs after evaluation.
    '''
    def listval(objs):
        return list(value(objs) for value in values)
    object.__setattr__(listval, '__objquery__', True)
    return listval

# note this function was written well before I wrote any other pare of the code
# as a technology demo. I need to refactor some parts of it...
def queryValue(q):
    '''
    Computes a path expression. The query (@q) is a list of attribute names and
    associated where expressions. The function returned computes the result when
    called.
    '''
    attrs = q
    def query(objs):
        def select(objs, attrs):
            '''a generator which computes the actual results'''
            def add(queue, u, v, i):
                '''adds the object v to the queue. It looks like u
                isn't necessary anymore. I should fix that...'''
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
                if hasattr(u, attrname): # the current object has the attr
                    v = getattr(u, attrname)
                    #it is iterable
                    if not isinstance(v, str) and hasattr(v, '__iter__'):
                        for z in v:
                            # add each child into the processing queue
                            if isinstance(v, dict):
                                next = KeyValuePair(z, v[z])
                            else:
                                next = z
                            # but only if its where condition is satisfied
                            if where != None:
                                cobjs = dict(objs)
                                cobjs.update({'self':next})
                                if not where(cobjs): continue
                            # if this is the last attribute yield the obj
                            if i+1 == len(attrs): yield next
                            else: add(queue, u, next, i) # otherwise add to the queue
                    else: #it is not iterable
                        if where != None:
                            cobjs = dict(objs)
                            cobjs.update({'self':v})
                            if not where(cobjs): continue
                        # if this is the last attribute yield the obj
                        if i+1 == len(attrs): yield v
                        else: add(queue, u, v, i) # otherwise add to the queue
        return OrderedSet(select(objs, attrs))
    object.__setattr__(query, '__objquery__', True)
    return query

def quantifiedValue(mode, name, s, satisfies):
    '''
    Processes the quantified expressions (some x in <> satisfie...) returns
    the where function.
    '''
    def where(objs):
        nobjs = s(objs) # runs the first part of the query (eg. the <path> expression)
        if not nobjs: return False # if returns and empty set then return false
        if mode == 'every':
            r = True
            for x in nobjs:
                cobjs = dict(objs) # we have to copy the objects to not squash
                                   # the upper namespace
                cobjs.update({name:x})
                if not satisfies(cobjs):
                    r = False
            return r
        elif mode == 'some':
            for x in nobjs:
                cobjs = dict(objs)
                cobjs.update({name:x})
                if satisfies(cobjs):
                    return True
            return False
        raise Exception("mode '%s' is not 'every' or 'some'" % mode)
    return where

def flwrSequence(return_expr, for_expr=None, let_expr=None, where_expr=None, order_expr=None, flatten=False, collecting=False):
    '''
    Returns the function to caculate the results of a flwr expression
    '''
    #print order_expr
    if flatten:
        assert len(return_expr) == 1 and not isinstance(return_expr[0], tuple)
        assert not collecting
    #if collecting:
        #target = return_expr['as']
        #reduce_function = return_expr['with']
        #return_expr = return_expr['value']
    def sequence(objs):
        def _flatten_func(tup):
            if not isinstance(tup, tuple):
                yield tup
            else:
                for i in tup:
                    if isinstance(i, tuple):
                        for j in _flatten_func(i):
                            yield j
                    else:
                        yield i
        def _build_yield(cobjs):
            def _build_return(obj):
                if len(obj) == 1 and not isinstance(obj[0], tuple):
                    return obj[0](cobjs)
                elif isinstance(obj[0], tuple): # it has named return values
                    return dict((name, f(cobjs)) for name,f in obj)
                else: # multiple positional return values
                    return tuple(f(cobjs) for f in obj)
            if not collecting:
                return _build_return(return_expr)
            collectors = list()
            for collector in return_expr:
                collectors.append({
                  'value':_build_return(collector['value']),
                  'as':collector['as'](cobjs),
                  'with':collector['with'](cobjs)
                })
            return collectors
        def inner(objs):
            ## take the cartesian product of the for expression
            ## note you cannot do this:
            ##   for x in <path>, y in <x>
            ##   :sadface: some day I will fix this.
            ##   however I will only do that when I implement and optimizer
            ##   for PyQuery otherwise it just isn't worth it.
            if for_expr is not None:
                obs = [
                    [(seqs[0], obj) for obj in seqs[1](objs)]
                    for seqs in for_expr]
            else:
                ## The goal is to get the for loop to run once. this syntax does
                ## it. We may not have a for_expr but we want everything else
                ## to execute normally.
                obs = [[None]]
            for items in product(*obs):
                cobjs = dict(objs)
                if for_expr is not None:  ## we can only execute this if we
                                          ## actually have a for_expr though.
                    for name, item in items:
                        cobjs.update({name:item})
                if let_expr:
                    for name, let in let_expr:
                        cobjs.update({name:let(cobjs)}) # calculate the let expr
                if where_expr and not where_expr(cobjs):
                    continue # skip if the where fails
                if not flatten:
                    yield _build_yield(cobjs) # single unamed return
                else:
                    for i in _flatten_func(return_expr[0](cobjs)):
                        yield i
        if collecting:
            rets = tuple(dict() for _ in range(len(return_expr)))
            for collectors in inner(objs):
                for i, collector in enumerate(collectors):
                    _as = collector['as']
                    _rf = collector['with']
                    _value = collector['value']
                    rets[i][_as] = _rf(rets[i].get(_as, None), _value)
            if len(rets) == 1: return rets[0]
            return rets
        else:
            r = list(inner(objs))
            if not r:
                return tuple(r)
            elif order_expr:
                attr, direction = order_expr
                if isinstance(attr, str):
                    if not isinstance(return_expr[0], tuple):
                        raise SyntaxError("Using a name in the order by clause when not using named return values.")
                else:
                    if isinstance(return_expr[0], tuple):
                        raise SyntaxError("Using a number in the order by clause when not using positional return values.")
                if len(return_expr) == 1 and not isinstance(return_expr[0], tuple):
                    keyfunc = lambda x: x
                else:
                    keyfunc = lambda x: x[attr]
                if direction == 'ASCD': r = sorted(r, key=keyfunc)
                else: r = sorted(r, key=keyfunc, reverse=True)
            return tuple(r)
    object.__setattr__(sequence, '__objquery__', True)
    return sequence

def functionDefinition(params, query):
    def flwr_function(objs):
        def function(*args):
            if len(args) != len(params):
                raise RuntimeError("Got wrong number of params expected %d got %d" % (len(params), len(args)))
            namespace = dict(objs)
            namespace.update(list(zip(params, args)))
            return query(namespace)
        return function
    return flwr_function

def ifExpr(condition, then, otherwise):
    def if_expr(objs):
        if condition(objs): return then(objs)
        else: return otherwise(objs)
    return if_expr
