'''
PyQuery - The Python Object Query System
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: t_lexer.py
Purpose: Tests for the Lexer
'''

import unittest, os, sys, base64, itertools, random, time
import pyquery


class TestLexer(unittest.TestCase):

	def test_hello(self):
		pyquery.compile('hello')
		self.assertRaises(SyntaxError, pyquery.compile, 'hello hello')

	def test_slash(self):
		pyquery.compile('hello/hello')
		pyquery.compile('hello/hello/asdf/wef')
		pyquery.compile('hello/hello/wewe/wef/waef/awef/weaf')
		pyquery.compile('hello/hello /wewe/ wef /waef/awef/weaf')
		self.assertRaises(SyntaxError, pyquery.compile, 'hello/awef/awef hello/awef')

	def test_where_exists(self):
		pyquery.compile('hello[wheRe]/hello[asdf]')
		pyquery.compile('hello/hello[asdf]/asdf/wef')
		pyquery.compile('hello/hello/wewe[asdf]/wef/waef/awef/weaf')
		pyquery.compile('hello/hello[asdf] /wewe/ wef[asdf] /waef/awef[asdf]/weaf')
		self.assertRaises(SyntaxError, pyquery.compile, 'hello/aef[asdf] hello[adsf]')

	def test_where_op(self):
		pyquery.compile('hello[1 == 1]')
		pyquery.compile('hello[1 != 1]')
		pyquery.compile('hello[1 < 1]')
		pyquery.compile('hello[1 <= 1]')
		pyquery.compile('hello[1 > 1]')
		pyquery.compile('hello[1 >= 1]')

	def test_where_bool(self):
		pyquery.compile('hello[a and b]')
		pyquery.compile('hello[a or b]')
		pyquery.compile('hello[not a or b]')
		pyquery.compile('hello[a or not b]')
		pyquery.compile('hello[not a and b]')
		pyquery.compile('hello[a and not b]')
		pyquery.compile('hello[not a or not b]')
		pyquery.compile('hello[not a and not b]')

	def test_where_parens_bool(self):
		pyquery.compile('hello[((a and b) and not (a or b) or not (a and b)) and not (not a or b)]')

	def test_where_value(self):
		pyquery.compile('hello[a]')
		pyquery.compile("hello[a[0]['hello']]")
		pyquery.compile("hello[a[0][\"hello\"]]")
		pyquery.compile("hello[a[0]['hello']()]")
		pyquery.compile("hello[a[0]['hello'](0)]")
		pyquery.compile("hello[a[0]['hello']('asdf')]")
		pyquery.compile("hello[a[0]['hello'](asdf)]")
		pyquery.compile("hello[a[0]['hello'](0, 'asdf', asdf)()()(1,2)]")
		pyquery.compile('hello["sadf"]')
		pyquery.compile('hello[123]')
		pyquery.compile('hello[123.234]')
		pyquery.compile('hello[asdf.asfd.asdf]')
		pyquery.compile('hello[asdf[12].asfd().asdf]')

	def test_where_value_params(self):
		pyquery.compile('hello[f(1)]')
		pyquery.compile('hello[f(1,2,3)]')
		pyquery.compile('hello[f(1,<asdf>,{for x in <asdf> return x})]')
		pyquery.compile('hello[f(a,b,c)]')
		pyquery.compile('hello[f(a(),b(),c())]')
		pyquery.compile('hello[f(a[a],b[b],c[c])]')

	def test_where_quantified(self):
		pyquery.compile('hello[every x in <asdf> satisfies (x)]')
		self.assertRaises(SyntaxError, pyquery.compile, 'hello[every x in <asdf> statisfies (x)]')
		self.assertRaises(SyntaxError, pyquery.compile, 'hello[every x in <asdf> statisfies x]')
		pyquery.compile('hello[some x in <asdf> satisfies (x)]')
		pyquery.compile('hello[some x in <self/asdf> satisfies (x)]')
		pyquery.compile('hello[some x in {for x in <asdf> return x} satisfies (x)]')
		pyquery.compile('hello[some x in {for x in <asdf> return x} satisfies (x == y)]')
		pyquery.compile('hello[some x in {for x in <asdf> return x} satisfies (x and not y(1,2))]')

if __name__ == '__main__':
	unittest.main()
