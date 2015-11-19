'''
PyQuery - The Python Object Query System
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: pyflwor.py
Purpose: The public API for PyFlwor.
'''
from __future__ import absolute_import
from __future__ import unicode_literals
from builtins import str, bytes

try:
    from .parser import Parser
    from .lexer import Lexer

except SystemError:
    from parser import Parser
    from lexer import Lexer

import re

def compile(query):
    '''
    Compiles a query string into a python function that takes one parameter, the execution namespace.
    The compiled function is re-usable. For information on the grammar see X.
    '''
    return Parser().parse(bytes(query, 'utf-8').decode('unicode_escape'), lexer=Lexer())

def execute(query, namespace):
    '''
    Compiles the query string and executes it with the suppied namespace. If you want to execute a
    particular query many times, use compile to get a query function.
    '''
    return compile(query)(namespace)
