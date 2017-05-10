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
from __future__ import division
from __future__ import absolute_import
from past.utils import old_div
from builtins import object

import unittest, os, sys, base64, itertools, random, time


try:
    from .OrderedSet import OrderedSet as oset
    from . import pyflwor
    from . import symbols
except SystemError:
    from OrderedSet import OrderedSet as oset
    import pyflwor
    import symbols

exe = pyflwor.execute
class TestPyQuery(unittest.TestCase):

    def test_hello(self):
        hello = 'hello world!'
        q = pyflwor.compile('hello')
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
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
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
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        self.assertEquals(exe('a[f()]', d), oset([a]))
        self.assertEquals(exe('a[f() == "hello"]', d), oset([a]))
        self.assertEquals(exe('a[g(1,2,3) == 6]', d), oset([a]))
        self.assertEquals(exe('a[h(i,3) == 9]', d), oset([a]))
        self.assertEquals(exe('a[i(j(j)(j)(j)(h)(i,3)) == 81]', d), oset([a]))

    def test_list_where_values(self):
        a = 'hello'
        l = [1,2,3,4,5,6,7,[1,2,3,4,5,6,7,[1,2,3,4,5,6,7,8]]]
        d = locals()
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
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
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
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
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        self.assertEquals(exe('a[m["next"][7](j)(m["next"][7])(m["next"])[7](i)(m["two"]) == 4]', d), oset([a]))

    def test_flwr_attrvalue(self):
        def f(): return (1,2,3)
        d = locals()
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        self.assertEquals(exe('for x in f() return x', d), (1,2,3))
        self.assertEquals(exe('for x in f() let y = f() return x, y', d), ((1,(1,2,3)), (2, (1,2,3)), (3, (1,2,3))))

    def test_flwr_orderby(self):
        def f(): return [1,3,2]
        d = locals()
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        self.assertRaises(SyntaxError, exe, 'for x in f() order by "asdf" ascd return x', d)
        self.assertRaises(SyntaxError, exe, 'for x in f() order by 0 ascd return "asdf":x', d)
        self.assertEquals(exe('for x in f() order by 0 ascd return x', d), (1,2,3))
        self.assertEquals(exe('for x in f() order by 0 desc return x', d), (3,2,1))

    def test_function_def(self):
        a = 'hello'
        l = [1,2,3,4,5,6,7,[1,2,3,4,5,6,7,[1,2,3,4,5,6,7,8]]]
        d = locals()
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        self.assertEquals(exe('''
          for i in l
          let f = function() { 125 }
          return f()
        ''', d), (125, 125, 125, 125, 125, 125, 125, 125))
        self.assertEquals(exe('''
          for i in l
            let f = function(q) {
              for _ in <a>
              where isinstance(q, list)
              return {
                for j in q
                return f(j)
              }
            }
          return f(i)
        ''', d),
          ((), (), (), (), (), (), (),
            (((), (), (), (), (), (), (),
              (((), (), (), (), (), (), (), ()),)
            ),
          ))
        )


    def test_ifExpr(self):
        a = 'hello'
        l = [1,2,3,4,5,6,7,[1,2,3,4,5,6,7,[1,2,3,4,5,6,7,8]]]
        q = True
        d = locals()
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        self.assertEquals(exe('''
          for x in <a> return if (q) then 1 else 0
          ''', d), oset([int(q)]))

    def test_ifExpr_short_circuit(self):
        a = 'hello'
        l = [1,2,3,4,5,6,7,[1,2,3,4,5,6,7,[1,2,3,4,5,6,7,8]]]
        true = True
        false = False
        d = locals()
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        self.assertEquals(exe('''
          for x in <a> return if (true or X) then 1 else 0
          ''', d), (1,))
        self.assertEquals(exe('''
          for x in <a> return if (false and false.x) then 1 else 0
          ''', d), (0,))

    def test_flattened_return(self):
        a = 'hello'
        l = [1,2,3,4,5,6,7,[1,2,3,4,5,6,7,[1,2,3,4,5,6,7,8]]]
        true = True
        false = False
        d = locals()
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        self.assertEquals(exe('''
            for i in l
            let f = function(l) {
              if (isinstance(l, list))
              then {for j in l return f(j)}
              else l
            }
            return flatten f(i)
          ''', d), (1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 8))
        self.assertEquals(exe('''
            for i in l
            let f = function(l) {
              if (isinstance(l, list))
              then {for j in l return f(j)}
              else {a:l}
            }
            return flatten f(i)
          ''', d), tuple({a:i}
            for i in (1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 8)))

    def test_None(self):
        a = 'hello'
        l = [1,2,3,4,5,6,7,[1,2,3,4,5,6,7,[1,2,3,4,5,6,7,8]]]
        q = None
        d = locals()
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        self.assertEquals(exe('''
          for x in l
          return None
          ''', d), oset([None]))

    def test_construct_class(self):
        class A(object): pass
        l = [1,2,3,4,5,6,7,[1,2,3,4,5,6,7,[1,2,3,4,5,6,7,8]]]
        q = None
        d = locals()
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        self.assertTrue(exe('''
          for x in <q>
          return A()
          ''', d))

    def test_no_for(self):
        a = 'hello'
        l = [1,2,3,4,5,6,7,[1,2,3,4,5,6,7,[1,2,3,4,5,6,7,8]]]
        q = None
        d = locals()
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        flwr = symbols.flwrSequence([symbols.attributeValue('hello', scalar=True)])
        self.assertEquals(flwr(d), ('hello',))
        self.assertEquals(exe('''
            return l
          ''', d), (l,))
        self.assertEquals(exe('''
            let f = function(l) {
              if (isinstance(l, list))
              then {for j in l return f(j)}
              else l
            }
            return flatten f(l)
          ''', d), (1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 8))

    def test_count(self):
        l = [1,2,3,4,5,6,7,3,4,5,6,7,3,4]
        d = locals()
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        self.assertEquals(exe('''
            for n in l
            collect n as n with function(prev, next) {
                if prev == None then 1 else prev + 1
            }
          ''', d), {1:1,2:1,3:3,4:3,5:2,6:2,7:2})

    def test_list_literal(self):
        d = locals()
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        self.assertEquals(exe('''
            for n in [1,2,3,4,5,6,7,3,4,5,6,7,3,4]
            collect n as n with function(prev, next) {
                if prev == None then 1 else prev + 1
            }
          ''', d), {1:1,2:1,3:3,4:3,5:2,6:2,7:2})

    def test_arithmetic(self):
        d = locals()
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        self.assertEquals(exe('''
            for n in [
                4.0*3.0/2.0,
                4.0/3.0*2.0,
                (3.0+9.0)*4.0/8.0,
                ((9.0-3.0)+(5.0-3.0))/2.0 + 2.0,
                5.0 * 4.0 / 2.0 - 10.0 + 5.0 - 2.0 + 3.0,
                5.0 / 4.0 * 2.0 + 10.0 - 5.0 * 2.0 / 3.0
            ]
            return n
          ''', d), (
                4.0*3.0/2.0,
                4.0/3.0*2.0,
                (3.0+9.0)*4.0/8.0,
                old_div(((9.0-3.0)+(5.0-3.0)),2.0) + 2.0,
                5.0 * 4.0 / 2.0 - 10.0 + 5.0 - 2.0 + 3.0,
                5.0 / 4.0 * 2.0 + 10.0 - 5.0 * 2.0 / 3.0
          ))

    def test_innotin(self):
        l = [1,2,3,4,5,6,7,3,4,5,6,7,3,4]
        d = locals()
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        self.assertEquals(exe('''
            for n in l
            where 1 in l and 12 not in l
            collect n as n with function(prev, next) {
                if prev == None then 1 else prev + 1
            }
          ''', d), {1:1,2:1,3:3,4:3,5:2,6:2,7:2})

    def test_multi_collect(self):
        l = [1,2,3,4,5,6,7,3,4,5,6,7,3,4]
        d = locals()
        try: d.update(__builtins__.__dict__)
        except AttributeError: d.update(__builtins__)
        self.assertEquals(exe('''
            for n in l
            let counter = function(prev, next) {
                if prev == None then 1 else prev + 1
            }
            where 1 in l and 12 not in l
            collect n as n with counter
            collect n as (int(n)/int(2)) with counter
          ''', d), (
            {1: 1, 2: 1, 3: 3, 4: 3, 5: 2, 6: 2, 7: 2},
            {0: 1, 1: 4, 2: 5, 3: 4}))


if __name__ == '__main__':
    unittest.main()
