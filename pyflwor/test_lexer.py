'''
PyQuery - The Python Object Query System
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: t_lexer.py
Purpose: Tests for the Lexer
'''
from __future__ import print_function
from __future__ import absolute_import
from builtins import next

# import base64
# import itertools
# import os
# import random
# import sys
# import time
import unittest

from contextlib import contextmanager
from ply import lex
from . import lexer

def showcmp(a, b):
    print((a.type == b.type, a.value == b.value,
           a.lexpos == b.lexpos, a.lineno == b.lineno))

def compare(a, b):
    return (a.type == b.type and a.value == b.value and
            a.lexpos == b.lexpos and a.lineno == b.lineno)

def token(typ, value, pos, line):
    t = lex.LexToken()
    t.type = typ
    t.value = value
    t.lexpos = pos
    t.lineno = line
    return t

@contextmanager
def comparable_tokens():
    eq = lex.LexToken.__eq__
    ne = lex.LexToken.__ne__
    setattr(lex.LexToken, "__eq__", compare)
    setattr(lex.LexToken, "__ne__", lambda a, b: not compare(a, b))
    yield
    setattr(lex.LexToken, "__eq__", eq)
    setattr(lex.LexToken, "__ne__", ne)


class TestLexer(unittest.TestCase):

    def test_contextmng(self):
        t1 = token("NAME", 'a', 0, 1)
        t2 = token("NAME", 'a', 0, 1)
        self.assertNotEquals(t1, t2)
        with comparable_tokens():
            self.assertEquals(t1, t2)

    def test_NAME(self):
        clex = lexer.Lexer()
        clex.input('a 9a')
        tokens = [token("NAME", 'a', 0, 1),
                  token("NUMBER", 9, 2, 1),
                  token("NAME", 'a', 3, 1)]
        with comparable_tokens():
            for i, t1 in enumerate(clex):
                # showcmp(t1, tokens[i])
                self.assertEquals(t1, tokens[i])

    def test_STRING(self):
        clex = lexer.Lexer()
        clex.input("'asdf' \"asdf\" '\n'")
        tokens = [token("STRING", 'asdf', 0, 1),
                  token("STRING", 'asdf', 7, 1),
                  token("STRING", '\n', 14, 1), ]
        with comparable_tokens():
            for i, t1 in enumerate(clex):
                self.assertEquals(t1, tokens[i])

    def test_HEX(self):
        clex = lexer.Lexer()
        clex.input("0xab 0xab")
        tokens = [token("NUMBER", 0xab, 0, 1),
                  token("NUMBER", 171, 5, 1)]
        with comparable_tokens():
            for t2 in tokens:
                self.assertEquals(next(clex), t2)

    def test_FLOAT(self):
        clex = lexer.Lexer()
        clex.input("1.2 .2 2.3e4 .2 2.3e4")
        tokens = [token("NUMBER", 1.2, 0, 1), token("NUMBER", .2, 4, 1),
                  token("NUMBER", 2.3e4, 7, 1), token("NUMBER", .2, 13, 1),
                  token("NUMBER", 2.3e4, 16, 1)]
        with comparable_tokens():
            for t2 in tokens:
                self.assertEquals(next(clex), t2)

    def test_OCT(self):
        clex = lexer.Lexer()
        clex.input("073 073 073")
        tokens = [token("NUMBER", 0o73, 0, 1),
                  token("NUMBER", 59, 4, 1),
                  token("NUMBER", 59, 8, 1)]
        with comparable_tokens():
            for t2 in tokens:
                self.assertEquals(next(clex), t2)

    def test_DEC(self):
        clex = lexer.Lexer()
        clex.input("73 730 7")
        tokens = [token("NUMBER", 73, 0, 1),
                  token("NUMBER", 730, 3, 1),
                  token("NUMBER", 7, 7, 1)]
        with comparable_tokens():
            for t2 in tokens:
                self.assertEquals(next(clex), t2)

    def test_KEYWORDS(self):
        for value, typ in list(lexer.reserved.items()):
            clex = lexer.Lexer()
            clex.input(value)
            tokens = [token(typ, value, 0, 1)]
            with comparable_tokens():
                for t2 in tokens:
                    self.assertEquals(next(clex), t2)

    def test_chrs(self):
        for typ, value in [(attr[2:], getattr(lexer.Lexer, attr))
                           for attr in dir(lexer.Lexer)
                           if attr[:2] == 't_' and
                           isinstance(getattr(lexer.Lexer, attr), str) and
                           attr[2:] != 'ignore']:
            if value[0] == '\\':
                value = value[1:]
            clex = lexer.Lexer()
            clex.input(value)
            tokens = [token(typ, value, 0, 1)]
            with comparable_tokens():
                for t2 in tokens:
                    # print(clex.type, clex.value, clex.lexpos, clex.lineno)
                    self.assertEquals(next(clex), t2)


if __name__ == '__main__':
    unittest.main()
