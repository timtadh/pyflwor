'''
PyQuery - The Python Object Query System
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: t_parser.py
Purpose: Tests for the Parser
NB: Should test most of the language, as in make sure examples compile. Tests
    for correctness will be quite difficult given the nature of this compiler.
'''

import unittest, os, sys, base64, itertools, random, time
import pyquery


class TestParser(unittest.TestCase):

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

    def test_where_setcmp(self):
        pyquery.compile('hello[a in <as>]')
        pyquery.compile('hello[a not in <as>]')
        pyquery.compile('hello[not a in <as>]')
        pyquery.compile('hello[<a> subset <as>]')
        pyquery.compile('hello[<a> superset <as>]')
        pyquery.compile('hello[<a> proper subset <as>]')
        pyquery.compile('hello[<a> proper superset <as>]')
        pyquery.compile('hello[<a> is <as>]')
        pyquery.compile('hello[<a> is not <as>]')

    def test_setops(self):
        pyquery.compile('asdf - asdf')
        pyquery.compile('asdf & asdf')
        pyquery.compile('asdf | asdf')
        pyquery.compile('(asdf | asdf) & asdf - (asdf & asdf) - (asdf & (afsd | asdf))')
        pyquery.compile('asdf/asdf - asdf/asd[erw]')

    def test_flwr(self):
        pyquery.compile('for x in <asfd> return x')
        pyquery.compile('for x in <asfd>, y in <adsf> return x')
        pyquery.compile('for x in {for x in <asdf> return x} return x')
        pyquery.compile('for x in <asfd> where x == y return x')
        pyquery.compile('for x in <asfd> let y = <x/asdf> return x')
        pyquery.compile('for x in <asfd> let y = {for x in <asdf> return x} return x')
        pyquery.compile('for x in <asfd> let y = <x/asdf>, x = <adf> return x')
        pyquery.compile('for x in <asfd> let y = <x/asdf> let x = <adf> return x')
        pyquery.compile('for x in <asfd>, z in <asdf> let y = <x/asdf> let x = <adf> return x')
        pyquery.compile('''for x in <asfd>, z in <asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q)
            return x''')
        pyquery.compile('''for x in <asfd>, z in <asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q)
            return x,y,z''')
        pyquery.compile('''for x in <asfd>, z in <asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q)
            return x,y.sdf.asd,z''')
        pyquery.compile('''for x in <asfd>, z in <asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q)
            return x,y.sdf.asd,z()()()[asdf][asfd](1,2,3)''')
        pyquery.compile('''for x in <asfd>, z in <asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q)
            return 'asdf':asdf''')
        pyquery.compile('''for x in <asfd>, z in <asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q)
            return 'asdf':asdf, "hello":"hello World!"''')
        pyquery.compile('''for x in <asfd>, z in <asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q == z and (<y> is not <z>))
            return 'asdf':asdf, "one":1, "2.0":2.0''')
        pyquery.compile('''for x in <asfd>, z in <asdf>, y in <asdf/asdf>
            let y = <x/asdf>
            let x = <adf>
            where every x in <y> satisfies (q == z and (<y> is not <z>))
            return 'asdf':asdf, "one":1, "2.0":2.0''')
        pyquery.compile('''for x in <asfd>, z in <asdf>, y in <asdf/asdf>
            let y = <x/asdf>, y1 = <Afd>, y2 = <asdf>, y3 = <asdf>
            let x = <adf>
            where every x in <y> satisfies (q == z and (<y> is not <z>))
            return 'asdf':asdf, "one":1, "2.0":2.0''')

    def test_flwr_attrvalue(self):
        pyquery.compile('''for x in <asfd>, z in <asdf>, y in sdaf.asdf(asdf, asdf)[1]
            let y = <x/asdf>, y1 = <Afd>, y2 = <asdf>, y3 = <asdf>
            let x = <adf>
            where every x in <y> satisfies (q == z and (<y> is not <z>))
            return 'asdf':asdf, "one":1, "2.0":2.0''')
        pyquery.compile('''for x in <asfd>, z in <asdf>, y in sdaf.asdf(asdf, asdf)[1]
            let y = <x/asdf>, y1 = <Afd>, y2 = <asdf>, y3 = <asdf>
            let x = <adf>
            let q = sadf.asdf().asfd[1](1,2,3)
            where every x in <y> satisfies (q == z and (<y> is not <z>))
            return 'asdf':asdf, "one":1, "2.0":2.0''')

    def test_flwr_orderby(self):
        pyquery.compile('for x in <asdf> order by "adsf" desc return "adsf":x')
        pyquery.compile('''for x in <asfd>, z in <asdf>, y in sdaf.asdf(asdf, asdf)[1]
            let y = <x/asdf>, y1 = <Afd>, y2 = <asdf>, y3 = <asdf>
            let x = <adf>
            where every x in <y> satisfies (q == z and (<y> is not <z>))
            order by "asdf" desc
            return 'asdf':asdf, "one":1, "2.0":2.0''')
        pyquery.compile('for x in <asdf> order by 0 ascd return x')
        pyquery.compile('''for x in <asfd>, z in <asdf>, y in sdaf.asdf(asdf, asdf)[1]
            let y = <x/asdf>, y1 = <Afd>, y2 = <asdf>, y3 = <asdf>
            let x = <adf>
            where every x in <y> satisfies (q == z and (<y> is not <z>))
            order by 1 ascd
            return asdf, 1, 2.0''')

if __name__ == '__main__':
    unittest.main()
