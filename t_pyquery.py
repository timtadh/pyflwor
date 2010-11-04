'''
PyQuery - The Python Object Query System
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: t_parser.py
Purpose: System Tests
NB: More tests need to be written, this is just the start.
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
        self.assertEquals(exe('a["HELLO" == a.upper()]', d), oset([a]))

    def test_func_where_values(self):
        a = 'hello'
        def f(): return 'hello'
        def g(x,y,z): return x + y + z
        def h(f,x): return f(x)
        def i(x): return x**2
        def j(f): return f
        true = True
        false = False
        d = locals()
        d.update(__builtins__.__dict__)
        self.assertEquals(exe('a[f()]', d), oset([a]))
        self.assertEquals(exe('a[f() == "hello"]', d), oset([a]))
        self.assertEquals(exe('a[g(1,2,3) == 6]', d), oset([a]))
        self.assertEquals(exe('a[h(i,3) == 9]', d), oset([a]))
        self.assertEquals(exe('a[i(j(j)(j)(j)(h)(i,3)) == 81]', d), oset([a]))

    def test_list_where_values(self):
        a = 'hello'
        l = [1,2,3,4,5,6,7,[1,2,3,4,5,6,7,[1,2,3,4,5,6,7,8]]]
        d = locals()
        d.update(__builtins__.__dict__)
        self.assertEquals(exe('a[l[0] == 1]', d), oset([a]))
        self.assertEquals(exe('a[l[1] == 2]', d), oset([a]))
        self.assertEquals(exe('a[l[7][0] == 1]', d), oset([a]))
        self.assertEquals(exe('a[l[7][1] == 2]', d), oset([a]))
        self.assertEquals(exe('a[l[7][7][0] == 1]', d), oset([a]))
        self.assertEquals(exe('a[l[7][7][1] == 2]', d), oset([a]))
        self.assertEquals(exe('a[l[7][7][7] == 8]', d), oset([a]))

    def test_dict_where_values(self):
        a = 'hello'
        l = {"one":1, "two":2, "next":{"one":1, "two":2, "next":{"one":1, "two":2}}}
        d = locals()
        d.update(__builtins__.__dict__)
        self.assertEquals(exe('a[l["one"] == 1]', d), oset([a]))
        self.assertEquals(exe('a[l["two"] == 2]', d), oset([a]))
        self.assertEquals(exe('a[l["next"]["one"] == 1]', d), oset([a]))
        self.assertEquals(exe('a[l["next"]["two"] == 2]', d), oset([a]))
        self.assertEquals(exe('a[l["next"]["next"]["one"] == 1]', d), oset([a]))
        self.assertEquals(exe('a[l["next"]["next"]["two"] == 2]', d), oset([a]))

    def test_callable_where_values(self):
        a = 'hello'
        def f(): return 'hello'
        def g(x,y,z): return x + y + z
        def h(f,x): return f(x)
        def i(x): return x**2
        def j(f): return f
        m = {"one":1, "two":2, "next":[1,2,3,4,5,6,7,j]}
        true = True
        false = False
        d = locals()
        d.update(__builtins__.__dict__)
        self.assertEquals(exe('a[m["next"][7](j)(m["next"][7])(m["next"])[7](i)(m["two"]) == 4]', d), oset([a]))

if __name__ == '__main__':
    unittest.main()
