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

if __name__ == '__main__':
	unittest.main()
