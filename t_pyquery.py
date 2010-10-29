'''
PyQuery - The Python Object Query System
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: t_parser.py
Purpose: System Tests
'''

import unittest, os, sys, base64, itertools, random, time
from OrderedSet import OrderedSet as oset
import pyquery

exe = pyquery.execute
class TestPyQuery(unittest.TestCase):

	def test_hello(self):
		hello = 'hello world!'
		q = pyquery.compile('hello')
		self.assertEquals(q(locals()), oset([hello]))

	def test_iterdown(self):
		class A(object):
			def __init__(self, q):
				self.q = q
		answer = 'o.x.y'
		o = A('top')
		o.x = [A('asdf'), A('123')]
		o.x[0].y = A(answer)
		d = {'hasattr':hasattr, 'o':o}
		self.assertEquals(exe('o/x[hasattr(self,"y")]/y/q', d), oset([answer]))
		self.assertEquals(exe('o/x', d), oset(o.x))

	def test_cmpops(self):
		class A(object):
			def __init__(self, q):
				self.q = q
		a = A(5)
		self.assertEquals(exe('a[self.q == 5]', locals()), oset([a]))
		self.assertEquals(exe('a[self.q != 5]', locals()), oset([]))
		self.assertEquals(exe('a[self.q >= 5]', locals()), oset([a]))
		self.assertEquals(exe('a[self.q <= 5]', locals()), oset([a]))
		self.assertEquals(exe('a[self.q > 5]', locals()), oset([]))
		self.assertEquals(exe('a[self.q < 5]', locals()), oset([]))
		self.assertEquals(exe('a[self.q == 7]', locals()), oset([]))
		self.assertEquals(exe('a[self.q != 7]', locals()), oset([a]))
		self.assertEquals(exe('a[self.q >= 7]', locals()), oset([]))
		self.assertEquals(exe('a[self.q <= 7]', locals()), oset([a]))
		self.assertEquals(exe('a[self.q > 7]', locals()), oset([]))
		self.assertEquals(exe('a[self.q < 7]', locals()), oset([a]))
		self.assertEquals(exe('a[self.q == 3]', locals()), oset([]))
		self.assertEquals(exe('a[self.q != 3]', locals()), oset([a]))
		self.assertEquals(exe('a[self.q >= 3]', locals()), oset([a]))
		self.assertEquals(exe('a[self.q <= 3]', locals()), oset([]))
		self.assertEquals(exe('a[self.q > 3]', locals()), oset([a]))
		self.assertEquals(exe('a[self.q < 3]', locals()), oset([]))

	def test_smpl_boolean_exprs(self):
		a = 'hello'
		true = True
		false = False
		self.assertEquals(exe('a[true]', locals()), oset([a]))
		self.assertEquals(exe('a[false]', locals()), oset([]))
		self.assertEquals(exe('a[not true]', locals()), oset([]))
		self.assertEquals(exe('a[not false]', locals()), oset([a]))
		self.assertEquals(exe('a[true and true]', locals()), oset([a]))
		self.assertEquals(exe('a[false and true]', locals()), oset([]))
		self.assertEquals(exe('a[not true and true]', locals()), oset([]))
		self.assertEquals(exe('a[not false and true]', locals()), oset([a]))
		self.assertEquals(exe('a[true or false]', locals()), oset([a]))
		self.assertEquals(exe('a[true or true]', locals()), oset([a]))
		self.assertEquals(exe('a[false or true]', locals()), oset([a]))
		self.assertEquals(exe('a[false or false]', locals()), oset([]))
		self.assertEquals(exe('a[not true or true]', locals()), oset([a]))
		self.assertEquals(exe('a[not false or false]', locals()), oset([a]))
		self.assertEquals(exe('a[true and true and true and true]', locals()), oset([a]))
		self.assertEquals(exe('a[true and true and true and false]', locals()), oset([]))

	def test_nested_boolean_exprs(self):
		a = 'hello'
		true = True
		false = False
		self.assertEquals(exe('a[true and (false or true)]', locals()), oset([a]))
		self.assertEquals(exe('a[true and (false and true)]', locals()), oset([]))
		self.assertEquals(exe('a[true and (true and true)]', locals()), oset([a]))
		self.assertEquals(exe('a[true and (true and (not true or false))]', locals()), oset([]))
		self.assertEquals(exe('a[1 and (1 and (not 1 or 0))]', locals()), oset([]))
		self.assertEquals(exe('a[1 and (1 and (not 1 or (1 and 0 or (1 and 1))))]', locals()), oset([a]))

	def test_simple_where_values(self):
		a = 'hello'
		true = True
		false = False
		d = locals()
		d.update(__builtins__.__dict__)
		self.assertEquals(exe('a[1 == 1]', d), oset([a]))
		self.assertEquals(exe('a[-1 == -1]', d), oset([a]))
		self.assertEquals(exe('a[2.2 == 2.2]', d), oset([a]))
		self.assertEquals(exe('a[2.2 == float("2.2")]', d), oset([a]))
		self.assertEquals(exe('a[2 == int(2.2)]', d), oset([a]))
		self.assertEquals(exe('a["hello" == a]', d), oset([a]))
		self.assertEquals(exe('a["hello" == a]', d), oset([a]))

if __name__ == '__main__':
	unittest.main()
