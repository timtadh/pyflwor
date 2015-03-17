'''
pyflwor - The Python Object Query System
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: repl.py
Purpose: REPL for pyflwor
'''
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import object
from past.utils import old_div

import os, sys
import subprocess
import pickle as pickle
from tempfile import mkstemp as tmpfile
from getline import Getlines
from . import pyflwor

getline = Getlines('.getline-history').getline

EDITOR = os.getenv('EDITOR')
if not EDITOR: EDITOR = 'vi'
assert EDITOR
QUERY_SEP = '------------'

def _transform(s):
    if s[0] == '_': return s[1:]
    return s

def avg(s):
    if not len(s): return 0.0
    return old_div(sum(s),float(len(s)))

_formats = ['text', 'csv']

class REPL(object):

    def __init__(self, objects, queries=None):
        if not objects:
            raise Exception("objects was empty, you must supply a query context (ie. objects to query...)")
        self.objects = objects
        self.queries = dict()
        if queries:
            for name in queries:
                query = queries[name]
                q = pyflwor.compile(query)
                self.queries.update({name.strip():(query,q)})
        self.histfile = '.hist'

    def querydict(self):
        d = {'float':float, 'int':int, 'avg':avg, 'len':len}
        d.update(__builtins__)
        d.update(self.objects)
        return d

    def edittext(self, text):
        fd, path = tmpfile()
        f = open(path, 'w')
        f.write(text)
        f.close()
        subprocess.check_call([EDITOR, path])
        f = open(path, 'r')
        s = f.read()
        f.close()
        os.unlink(path)
        if not s:
            raise Exception("Must enter a query into the editor and save the file.")
        return s.strip()

    def exe(self, prompt):
        def query(cmds, args):
            '''usage: query cmd [args]
                .    [try: queries help]
                Save, load, edit, execute, ... queries.
                for a list of the commands available type
                query help'''
            def save_exec(cmds, args):
                '''usage: query save_exec format filepath query
                    .    format = The output format.
                    .    filepath = The file to save the query's output in.
                    .               Path is relative to
                    .               $PROJECT_WORKING_DIR/analysis
                    .    query = Either the query text
                    .            or the name of a saved query
                    Save the output of a query to a file.
                    - If using the 'fvdl' or 'ofs' formats query must
                    .    return only objects of type Finding.
                    - The other formats avaliable are 'text', and 'csv'
                    - For a full list of formats type "formats"'''
                if args.count(' ') < 2:
                    raise Exception("Must supply both format, file location and a query.")
                format, path, query = args.split(' ', 2)
                if '_' in format:
                    i = format.index('_')
                    version = format[i+1:]
                    format = format[:i]
                else:
                    version = ''
                if not os.path.isabs(path):
                    path = os.path.join(ANALYSIS_DIR, path)
                if query in self.queries:
                    q = self.queries[query][1]
                    query = self.queries[query][0]
                else:
                    q = pyflwor.compile(query)

                results = q(self.querydict())
                if format in _formats:
                    f = open(path, 'w')
                    if format == 'text':
                        f.write('Query:\n')
                        f.write(query.strip())
                        f.write('\n\n\n')
                        for r in results:
                            if hasattr(r, '__iter__'):
                                s = str(tuple(str(item) for item in r))
                            else:
                                s = str(r)
                            f.write(s)
                            f.write('\n')
                    elif format == 'csv':
                        for r in results:
                            if hasattr(r, '__iter__'):
                                s = ', '.join(tuple(str(item) for item in r))
                            else:
                                s = str(r)
                            f.write(s)
                            f.write('\n')
                    f.close()
                else:
                    raise Exception("Format '%s' not supported" % format)
            def _exec(cmds, args):
                '''usage: query exec str
                    .    str = Either the query text
                    .            or the name of a saved query
                    Execute a query, can either be a query text or a
                    the name of a saved query.'''
                if args in self.queries:
                    q = self.queries[args][1]
                else:
                    print(args)
                    q = pyflwor.compile(args)
                results = q(self.querydict()) 
                for r in results:
                    #if hasattr(r, '__iter__'):
                        #print tuple(str(item) for item in r)
                    #else:
                    if isinstance(results, dict):
                        print(r, results[r])
                    else:
                        print(r)
            def edit(cmds, args):
                '''usage: query edit str
                    .    str = name of a saved query
                    Edit a saved query using the editor defined in
                    the enviroment as $EDITOR'''
                def badquery(query):
                    def bq(*args):
                        return pyflwor.compile(query)(*args)
                    return bq
                name = args
                name = name.strip()
                if name not in self.queries:
                    raise Exception("Query %s not defined" % name)
                query = self.edittext(self.queries[name][0])
                self.queries.update({name:(query,badquery(query))})
                q = pyflwor.compile(query)
                self.queries.update({name:(query,q)})
            def rm(cmds, args):
                '''usage: query rm str
                    .    str = name of a saved query
                    Remove a saved query'''
                name = args
                if name not in self.queries:
                    raise Exception("Query %s not defined" % s)
                del self.queries[name]
            def cp(cmds, args):
                '''usage: query cp fromname toname
                    .    fromname = name of a saved query
                    .    tonane = name of the copied query
                    Remove a saved query'''
                if args.count(' ') != 1:
                    raise Exception("Must have the form: queries cp fromname toname")
                fromname, toname = args.split(' ')
                if fromname not in self.queries:
                    raise Exception("Query %s not defined" % s)
                self.queries[toname] = self.queries[fromname]
            def add(cmds, args):
                '''usage: query add name
                    .    name = name of the query
                Add a query, the text of the query is added through
                an editor session with editor defined in the enviroment
                variable EDITOR.'''
                name = args
                query = self.edittext('')
                q = pyflwor.compile(query)
                self.queries.update({name.strip():(query,q)})
            def clear(cmds):
                '''usage: query clear
                    Remove all save queries'''
                self.queries = dict()
            def save(cmds, args):
                '''usage: query save filepath
                    .    filepath = path to the file relative to the current
                    .               working directory.
                    Save all of the queries to the given file'''
                f = open(args, 'w')
                for q in self.queries:
                    query = self.queries[q][0]
                    f.write('='.join((q,query)) + '\n')
                    f.write(QUERY_SEP + '\n')
                f.close()
            def load(cmds, args):
                '''usage: query load filepath
                    .    filepath = path to the file relative to the current
                    .               working directory.
                    Load queries from a file'''
                f = open(args, 'r')
                s = f.read()
                for line in s.split(QUERY_SEP):
                    line = line.strip()
                    if not line: continue
                    name, query = line.split('=', 1)
                    q = pyflwor.compile(query)
                    self.queries.update({name.strip():(query.strip(),q)})
                f.close()
            def _list(cmds):
                '''usage: query list
                List stored queries.'''
                if not self.queries:
                    print('No stored queries')
                keys = list(self.queries.keys())
                keys.sort()
                for name in keys:
                    print(name, ':')
                    for line in self.queries[name][0].split('\n'):
                        if not line: continue
                        print(' '*4, line)
            cmds = dict(locals())
            cmds = dict((_transform(var), cmds[var])
                    for var in query.__code__.co_varnames
                    if var in cmds and type(cmds[var]) == type(query))
            cmds['help'] = _help
            return self.proc_command(cmds, args)
        def objects(cmds):
            '''usage objects
            List all the loaded objects'''
            objs = self.querydict()
            keys = list(objs.keys())
            keys.sort()
            for obj in keys:
                print(obj, objs[obj])
                print()
        def formats(cmds):
            '''usage: formats
            Lists the available formats for serialization'''
            for format in _formats:
                print(format)
        def _dir(cmds, args):
            '''Run dir() on the given arg'''
            o = type('base' , (object,), self.objects)
            for x in args.split('.'):
                if hasattr(o, x):
                    o = getattr(o, x)
                else:
                    raise Exception("'%s' could not be resolved" % args)
            print(dir(o))
        def man(cmds, args):
            '''Get the docs on the given arg'''
            o = type('base' , (object,), self.objects)
            for x in args.split('.'):
                if hasattr(o, x):
                    o = getattr(o, x)
                else:
                    raise Exception("'%s' could not be resolved" % args)
            help(o)
        def _help(cmds, opt=None):
            '''Prints this message'''
            if opt in cmds:
                v = cmds[opt]
                print(opt)
                for line in v.__doc__.split('\n'):
                    line = line.strip()
                    if not line: continue
                    print(' '*4, line)
                return
            if opt:
                raise Exception("Command %s not found." % opt)
            keys = list(cmds.keys())
            keys.sort()
            for k in keys:
                v = cmds[k]
                if type(v) != type(_help): continue
                print(k)
                for line in v.__doc__.split('\n'):
                    line = line.strip()
                    if not line: continue
                    print(' '*4, line)
        def exit(cmds):
            '''Exits the repl.'''
            return True


        cmds = dict(locals())
        cmds = dict((_transform(i), cmds[i]) for i in cmds if i != '_transform')

        return self.proc_command(cmds, prompt)

    def proc_command(self, cmds, s):
        s = s.strip()
        if ' ' in s:
            i = s.index(' ')
            cmd_name = s[:i]
            args = s[i+1:]
        else:
            cmd_name = s
            args = str()
        try:
            if cmd_name not in cmds:
                raise Exception("command '%s' not found." % cmd_name)
            cmd = cmds[cmd_name]

            if 'args' in cmd.__code__.co_varnames and args != str():
                return cmd(cmds, args)
            elif 'args' in cmd.__code__.co_varnames and args == str():
                raise Exception("'%s' requires arguments, but none given" % cmd_name)
            elif 'opt' in cmd.__code__.co_varnames and args != str():
                return cmd(cmds, opt=args)
            elif 'args' not in cmd.__code__.co_varnames and args != str():
                raise Exception("'%s' does not except arguments" % cmd_name)
            else:
                return cmd(cmds)
        except Exception as e:
            print('\n<----------ERROR---------->')
            print('error: ', e)
            print('command: ', cmd_name)
            print('arguments: ', args)
            print('</---------ERROR---------->\n')
            #raise

    def start(self):
        exit = False
        while not exit:
            line = getline('pyflwor> ')
            if line is None: exit = self.exe('exit')
            else: exit = self.exe(line)
