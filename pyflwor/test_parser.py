'''
pyflwor - The Python Object Query System
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: t_parser.py
Purpose: Tests for the Parser
NB: Should test most of the language, as in make sure examples compile. Tests
    for correctness will be quite difficult given the nature of this compiler.
'''
from __future__ import absolute_import

import unittest, os, sys, base64, itertools, random, time
from . import pyflwor


class TestParser(unittest.TestCase):

    def test_hello(self):
        pyflwor.compile('hello')
        self.assertRaises(SyntaxError, pyflwor.compile, 'hello hello')

    def test_slash(self):
        pyflwor.compile('hello/hello')
        pyflwor.compile('hello/hello/asdf/wef')
        pyflwor.compile('hello/hello/wewe/wef/waef/awef/weaf')
        pyflwor.compile('hello/hello /wewe/ wef /waef/awef/weaf')
        self.assertRaises(SyntaxError, pyflwor.compile, 'hello/awef/awef hello/awef')

    def test_where_exists(self):
        pyflwor.compile('hello[wheRe]/hello[asdf]')
        pyflwor.compile('hello/hello[asdf]/asdf/wef')
        pyflwor.compile('hello/hello/wewe[asdf]/wef/waef/awef/weaf')
        pyflwor.compile('hello/hello[asdf] /wewe/ wef[asdf] /waef/awef[asdf]/weaf')
        self.assertRaises(SyntaxError, pyflwor.compile, 'hello/aef[asdf] hello[adsf]')

    def test_where_op(self):
        pyflwor.compile('hello[1 == 1]')
        pyflwor.compile('hello[1 != 1]')
        pyflwor.compile('hello[1 < 1]')
        pyflwor.compile('hello[1 <= 1]')
        pyflwor.compile('hello[1 > 1]')
        pyflwor.compile('hello[1 >= 1]')

    def test_where_bool(self):
        pyflwor.compile('hello[a and b]')
        pyflwor.compile('hello[a or b]')
        pyflwor.compile('hello[not a or b]')
        pyflwor.compile('hello[a or not b]')
        pyflwor.compile('hello[not a and b]')
        pyflwor.compile('hello[a and not b]')
        pyflwor.compile('hello[not a or not b]')
        pyflwor.compile('hello[not a and not b]')

    def test_where_parens_bool(self):
        pyflwor.compile('hello[((a and b) and not (a or b) or not (a and b)) and not (not a or b)]')

    def test_where_value(self):
        pyflwor.compile('hello[a]')
        pyflwor.compile("hello[a[0]['hello']]")
        pyflwor.compile("hello[a[0][\"hello\"]]")
        pyflwor.compile("hello[a[0]['hello']()]")
        pyflwor.compile("hello[a[0]['hello'](0)]")
        pyflwor.compile("hello[a[0]['hello']('asdf')]")
        pyflwor.compile("hello[a[0]['hello'](asdf)]")
        pyflwor.compile("hello[a[0]['hello'](0, 'asdf', asdf)()()(1,2)]")
        pyflwor.compile('hello["sadf"]')
        pyflwor.compile('hello[123]')
        pyflwor.compile('hello[123.234]')
        pyflwor.compile('hello[asdf.asfd.asdf]')
        pyflwor.compile('hello[asdf[12].asfd().asdf]')

    def test_where_value_params(self):
        pyflwor.compile('hello[f(1)]')
        pyflwor.compile('hello[f(1,2,3)]')
        pyflwor.compile('hello[f(1,<asdf>,{for x in <asdf> return x})]')
        pyflwor.compile('hello[f(a,b,c)]')
        pyflwor.compile('hello[f(a(),b(),c())]')
        pyflwor.compile('hello[f(a[a],b[b],c[c])]')

    def test_where_quantified(self):
        pyflwor.compile('hello[every x in <asdf> satisfies (x)]')
        self.assertRaises(SyntaxError, pyflwor.compile, 'hello[every x in <asdf> statisfies (x)]')
        self.assertRaises(SyntaxError, pyflwor.compile, 'hello[every x in <asdf> statisfies x]')
        pyflwor.compile('hello[some x in <asdf> satisfies (x)]')
        pyflwor.compile('hello[some x in <self/asdf> satisfies (x)]')
        pyflwor.compile('hello[some x in {for x in <asdf> return x} satisfies (x)]')
        pyflwor.compile('hello[some x in {for x in <asdf> return x} satisfies (x == y)]')
        pyflwor.compile('hello[some x in {for x in <asdf> return x} satisfies (x and not y(1,2))]')

    def test_where_setcmp(self):
        pyflwor.compile('hello[a in <qs>]')
        pyflwor.compile('hello[a not in <qs>]')
        pyflwor.compile('hello[not a in <qs>]')
        pyflwor.compile('hello[<a> subset <qs>]')
        pyflwor.compile('hello[<a> superset <qq>]')
        pyflwor.compile('hello[<a> proper subset <aq>]')
        pyflwor.compile('hello[<a> proper superset <aq>]')
        pyflwor.compile('hello[<a> is <qs>]')
        pyflwor.compile('hello[<a> is not <qs>]')

    def test_setops(self):
        pyflwor.compile('asdf - asdf')
        pyflwor.compile('asdf & asdf')
        pyflwor.compile('asdf | asdf')
        pyflwor.compile('(asdf | asdf) & asdf - (asdf & asdf) - (asdf & (afsd | asdf))')
        pyflwor.compile('asdf/asdf - asdf/asd[erw]')

    def test_flwr(self):
        pyflwor.compile('for x in <asfd> return x')
        pyflwor.compile('for x in <asfd>, y in <adsf> return x')
        pyflwor.compile('for x in {for x in <asdf> return x} return x')
        pyflwor.compile('for x in <asfd> where x == y return x')
        pyflwor.compile('for x in <asfd> let y = <x/asdf> return x')
        pyflwor.compile('for x in <asfd> let y = {for x in <asdf> return x} return x')
        pyflwor.compile('for x in <asfd> let y = <x/asdf>, x = <adf> return x')
        pyflwor.compile('for x in <asfd> let y = <x/asdf> let x = <adf> return x')
        pyflwor.compile('for x in <asfd>, z in <asdf> let y = <x/asdf> let x = <adf> return x')
        pyflwor.compile('''for x in <asfd>, z in <asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q)
            return x''')
        pyflwor.compile('''for x in <asfd>, z in <asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q)
            return x,y,z''')
        pyflwor.compile('''for x in <asfd>, z in <asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q)
            return x,y.sdf.asd,z''')
        pyflwor.compile('''for x in <asfd>, z in <asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q)
            return x,y.sdf.asd,z()()()[asdf][asfd](1,2,3)''')
        pyflwor.compile('''for x in <asfd>, z in <asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q)
            return 'asdf':asdf''')
        pyflwor.compile('''for x in <asfd>, z in <asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q)
            return 'asdf':asdf, "hello":"hello World!"''')
        pyflwor.compile('''for x in <asfd>, z in <asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q == z and (<y> is not <z>))
            return 'asdf':asdf, "one":1, "2.0":2.0''')
        pyflwor.compile('''for x in <asfd>, z in <asdf>, y in <asdf/asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q == z and (<y> is not <z>))
            return 'asdf':asdf, "one":1, "2.0":2.0''')
        pyflwor.compile('''for x in <asfd>, z in <asdf>, y in <asdf/asdf>
            let y = <x/asdf>, y1 = <Afd>, y2 = <asdf>, y3 = <asdf>
            let x = <adf>
            where every x in <y> satisfies (q == z and (<y> is not <z>))
            return 'asdf':asdf, "one":1, "2.0":2.0''')

    def test_flwr_attrvalue(self):
        pyflwor.compile('''for x in <asfd>, z in <asdf>, y in sdaf.asdf(asdf, asdf)[1]
            let y = <x/asdf>, y1 = <Afd>, y2 = <asdf>, y3 = <asdf>
            let x = <adf>
            where every x in <y> satisfies (q == z and (<y> is not <z>))
            return 'asdf':asdf, "one":1, "2.0":2.0''')
        pyflwor.compile('''for x in <asfd>, z in <asdf>, y in sdaf.asdf(asdf, asdf)[1]
            let y = <x/asdf>, y1 = <Afd>, y2 = <asdf>, y3 = <asdf>
            let x = <adf>
            let q = sadf.asdf().asfd[1](1,2,3)
            where every x in <y> satisfies (q == z and (<y> is not <z>))
            return 'asdf':asdf, "one":1, "2.0":2.0''')

    def test_flwr_orderby(self):
        pyflwor.compile('for x in <asdf> order by "adsf" desc return "adsf":x')
        pyflwor.compile('''for x in <asfd>, z in <asdf>, y in sdaf.asdf(asdf, asdf)[1]
            let y = <x/asdf>, y1 = <Afd>, y2 = <asdf>, y3 = <asdf>
            let x = <adf>
            where every x in <y> satisfies (q == z and (<y> is not <z>))
            order by "asdf" desc
            return 'asdf':asdf, "one":1, "2.0":2.0''')
        pyflwor.compile('for x in <asdf> order by 0 ascd return x')
        pyflwor.compile('''for x in <asfd>, z in <asdf>, y in sdaf.asdf(asdf, asdf)[1]
            let y = <x/asdf>, y1 = <Afd>, y2 = <asdf>, y3 = <asdf>
            let x = <adf>
            where every x in <y> satisfies (q == z and (<y> is not <z>))
            order by 1 ascd
            return asdf, 1, 2.0''')

    def test_flwr_function_noargs(self):
        pyflwor.compile('''
          for x in <asdf>
          let f = function() { for y in <asdf> return y }
          return f
          ''')

    def test_flwr_function_args(self):
        pyflwor.compile('''
          for x in <asdf>
          let f = function(q) { for y in q return y }
          return f
          ''')

    def test_if(self):
        pyflwor.compile('''
          for x in <asdf> return if (0) then 1 else 0
          ''')

    def test_reduce(self):
        pyflwor.compile('''
          for x in <asdf>
          collect x.tree as x.attr with function(prev, next) {
            if prev == None then next else prev.combine(next)
          }
          ''')


class TestParser2(unittest.TestCase):
    """Test for the new 'feature': 'bla' in ['list', 'of', 'stuffs']"""

    def test_in_list1(self):
        pyflwor.compile("hello['foo' in ['foo','bar']]")

    def test_in_list2(self):
        pyflwor.compile("hello['bazzz' in ['foo','bar']]")

    def test_not_in_list1(self):
        pyflwor.compile("hello['foo' not in ['foo','bar']]")

    def test_not_in_list2(self):
        pyflwor.compile("hello['bazzz' not in ['foo','bar']]")

    def test_in_list2(self):
        result = pyflwor.execute("res[test_elt in ['foo','bar']]",
                                 {'res': True, 'test_elt': 'foo'})
        self.assertTrue(bool(result))

    def test_in_list3(self):
        result = pyflwor.execute("res[test_elt in ['foo','bar']]",
                                 {'res': True, 'test_elt': 'bazzzz'})
        self.assertFalse(bool(result))

    def test_not_in_list4(self):
        result = pyflwor.execute("res[test_elt not in ['foo','bar']]",
                                 {'res': True, 'test_elt': 'bazzzz'})
        self.assertTrue(bool(result))

    def test_not_in_list5(self):
        result = pyflwor.execute("res[test_elt not in ['foo','bar']]",
                                 {'res': True, 'test_elt': 'foo'})
        self.assertFalse(bool(result))


if __name__ == '__main__':
    unittest.main()
