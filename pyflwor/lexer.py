'''
PyQuery - The Python Object Query System
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: lexer.py
Purpose: The lexer front end for the Query Compiler.
'''
from __future__ import print_function
from builtins import object

from ply import lex
from ply.lex import Token

tokens = ('NUMBER', 'STRING', 'NAME', 'SOME', 'EVERY', 'IN', 'NOT',
          'SATISFIES', 'AND', 'OR', 'IS',
          'SUBSET', 'SUPERSET', 'PROPER', 'FOR', 'LET', 'RETURN', 'WHERE',
          'FUNCTION', 'IF', 'THEN', 'ELSE', 'FLATTEN', 'COLLECT', 'AS', 'WITH',
          'ORDER', 'BY', 'ASCD', 'DESC', 'STAR', 'DASH', 'PLUS',
          'SLASH', 'EQEQ', 'EQ', 'NQ', 'LE', 'GE', 'COMMA', 'DOT', 'COLON',
          # 'AT',  #'DOLLAR',
          'UNION', 'INTERSECTION',
          'LPAREN', 'RPAREN', 'LSQUARE', 'RSQUARE',
          'LANGLE', 'RANGLE', 'LCURLY', 'RCURLY')

reserved = {'some': 'SOME', 'every': 'EVERY', 'in': 'IN', 'not': 'NOT',
            'satisfies': 'SATISFIES',
            'and': 'AND', 'or': 'OR', 'subset': 'SUBSET',
            'superset': 'SUPERSET',
            'proper': 'PROPER', 'is': 'IS', 'for': 'FOR',
            'let': 'LET', 'return': 'RETURN',
            'where': 'WHERE', 'order': 'ORDER', 'by': 'BY',
            'ascd': 'ASCD', 'desc': 'DESC',
            'function': 'FUNCTION', 'if': 'IF', 'then': 'THEN', 'else': 'ELSE',
            'flatten': 'FLATTEN', 'collect': 'COLLECT',
            'as': 'AS', 'with': 'WITH'}

# Common Regex Parts
D = r'[0-9]'
L = r'[a-zA-Z_]'
H = r'[a-fA-F0-9]'
E = r'[Ee][+-]?(' + D + ')+'


# Normally PLY works at the module level. I perfer having it encapsulated as
# a class. Thus the strange construction of this class in the new method allows
# PLY to do its magic.
class Lexer(object):

    def __new__(cls, **kwargs):
        self = super(Lexer, cls).__new__(cls, **kwargs)
        self.lexer = lex.lex(object=self, debug=False, optimize=True, **kwargs)
        return self.lexer

    tokens = tokens

    # t_AT = r'@'
    t_EQ = r'='
    t_EQEQ = r'=='
    t_NQ = r'!='
    # t_LT = r'<'
    # t_GT = r'>'
    t_GE = r'\>='
    t_LE = r'\<='
    t_DOT = r'\.'
    t_STAR = r'\*'
    t_DASH = r'\-'
    t_PLUS = r'\+'
    t_COMMA = r','
    t_COLON = r'\:'
    t_SLASH = r'/'
    t_UNION = r'\|'
    # t_DOLLAR = r'\$'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LCURLY = r'\{'
    t_RCURLY = r'\}'
    t_LANGLE = r'\<'
    t_RANGLE = r'\>'
    t_LSQUARE = r'\['
    t_RSQUARE = r'\]'
    # t_DIFFERENCE = r'-'
    t_INTERSECTION = r'&'

    string_literal1 = r'\"[^"]*\"'

    @Token(string_literal1)
    def t_STRING_LITERAL1(self, token):
        token.type = 'STRING'
        token.value = token.value[1:-1]
        return token

    string_literal2 = r"\'[^']*\'"

    @Token(string_literal2)
    def t_STRING_LITERAL2(self, token):
        token.type = 'STRING'
        token.value = token.value[1:-1]
        return token

    name = '(' + L + ')((' + L + ')|(' + D + '))*'

    @Token(name)
    def t_NAME(self, token):
        if token.value in reserved:
            token.type = reserved[token.value]
        else:
            token.type = 'NAME'
        return token

    const_hex = '0[xX](' + H + ')+'

    @Token(const_hex)
    def t_CONST_HEX(self, token):
        token.type = 'NUMBER'
        token.value = int(token.value, 16)
        return token

    const_float1 = '(' + D + ')+' + '(' + E + ')'  # {D}+{E}{FS}?

    @Token(const_float1)
    def t_CONST_FLOAT1(self, token):
        token.type = 'NUMBER'
        token.value = float(token.value)
        return token

    const_float2 = '(' + D + ')*\.(' + D + ')+(' + E + ')?'  # {D}*"."{D}+({E})?{FS}?

    @Token(const_float2)
    def t_CONST_FLOAT2(self, token):
        token.type = 'NUMBER'
        token.value = float(token.value)
        return token

    const_dec_oct = '(' + D + ')+'

    @Token(const_dec_oct)
    def t_CONST_DEC_OCT(self, token):
        token.type = 'NUMBER'
        if (len(token.value) > 1 and token.value[0] == '0' or
                (token.value[0] == '-' and token.value[1] == '0')):
            token.value = int(token.value, 8)
        else:
            token.value = int(token.value, 10)
        return token

    @Token(r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)')
    def t_COMMENT(self, token):
        # print token.lexer.lineno, len(token.value.split('\n')), token.value.split('\n')
        lines = len(token.value.split('\n')) - 1
        if lines < 0:
            lines = 0
        token.lexer.lineno += lines

    @Token(r'\n+')
    def t_newline(self, t):
        t.lexer.lineno += t.value.count("\n")

    # Ignored characters
    t_ignore = " \t"

    def t_error(self, t):
        raise Exception("Illegal character '%s'" % t)
        t.lexer.skip(1)

if __name__ == '__main__':
    lexer = Lexer()
    print(lexer.input('.'))
    print([x for x in lexer])
