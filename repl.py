# Copyright Cigital Inc. 2010 All Rights Reserved

import os, sys, termios, fcntl, struct
import subprocess
import cPickle as pickle
from tempfile import mkstemp as tmpfile
import pyquery

EDITOR = os.getenv('EDITOR')
if not EDITOR: EDITOR = 'vi'
assert EDITOR
QUERY_SEP = '------------'

def _transform(s):
	if s[0] == '_': return s[1:]
	return s

def avg(s):
	if not len(s): return 0.0
	return sum(s)/float(len(s))

_formats = ['text', 'csv']

class REPL(object):

	def __init__(self, objects, queries=None):
		if not objects:
			raise Exception, "objects was empty, you must supply a query context (ie. objects to query...)"
		self.objects = objects
		self.queries = dict()
		if queries:
			for name in queries:
				query = queries[name]
				q = pyquery.compile(query)
				self.queries.update({name.strip():(query,q)})
		self.histfile = '.hist'

	def querydict(self):
		d = {'float':float, 'int':int, 'avg':avg, 'len':len}
		d.update(self.objects)
		return self.objects

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
			raise Exception, "Must enter a query into the editor and save the file."
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
					raise Exception, "Must supply both format, file location and a query."
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
					q = pyquery.compile(query)

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
					raise Exception, "Format '%s' not supported" % format
			def _exec(cmds, args):
				'''usage: query exec str
					.    str = Either the query text
					.            or the name of a saved query
					Execute a query, can either be a query text or a
					the name of a saved query.'''
				if args in self.queries:
					q = self.queries[args][1]
				else:
					print args
					q = pyquery.compile(args)
				for r in q(self.querydict()):
					#if hasattr(r, '__iter__'):
						#print tuple(str(item) for item in r)
					#else:
					print r
			def edit(cmds, args):
				'''usage: query edit str
					.    str = name of a saved query
					Edit a saved query using the editor defined in
					the enviroment as $EDITOR'''
				name = args
				if name not in self.queries:
					raise Exception, "Query %s not defined" % s
				query = self.edittext(self.queries[name][0])
				q = pyquery.compile(query)
				self.queries.update({name.strip():(query,q)})
			def rm(cmds, args):
				'''usage: query rm str
					.    str = name of a saved query
					Remove a saved query'''
				name = args
				if name not in self.queries:
					raise Exception, "Query %s not defined" % s
				del self.queries[name]
			def cp(cmds, args):
				'''usage: query cp fromname toname
					.    fromname = name of a saved query
					.    tonane = name of the copied query
					Remove a saved query'''
				if args.count(' ') != 1:
					raise Exception, "Must have the form: queries cp fromname toname"
				fromname, toname = args.split(' ')
				if fromname not in self.queries:
					raise Exception, "Query %s not defined" % s
				self.queries[toname] = self.queries[fromname]
			def add(cmds, args):
				'''usage: query add name
					.    name = name of the query
				Add a query, the text of the query is added through
				an editor session with editor defined in the enviroment
				variable EDITOR.'''
				name = args
				query = self.edittext('')
				q = pyquery.compile(query)
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
					q = pyquery.compile(query)
					self.queries.update({name.strip():(query.strip(),q)})
				f.close()
			def _list(cmds):
				'''usage: query list
				List stored queries.'''
				if not self.queries:
					print 'No stored queries'
				keys = self.queries.keys()
				keys.sort()
				for name in keys:
					print name, ':'
					for line in self.queries[name][0].split('\n'):
						if not line: continue
						print ' '*4, line
			cmds = dict(locals())
			cmds = dict((_transform(var), cmds[var])
					for var in query.func_code.co_varnames
					if var in cmds and type(cmds[var]) == type(query))
			cmds['help'] = _help
			return self.proc_command(cmds, args)
		def objects(cmds):
			'''usage objects
			List all the loaded objects'''
			objs = self.querydict()
			keys = objs.keys()
			keys.sort()
			for obj in keys:
				print obj, objs[obj]
				print
		def formats(cmds):
			'''usage: formats
			Lists the available formats for serialization'''
			for format in _formats:
				print format
		def _dir(cmds, args):
			'''Run dir() on the given arg'''
			o = type('base' , (object,), self.objects)
			for x in args.split('.'):
				if hasattr(o, x):
					o = getattr(o, x)
				else:
					raise Exception, "'%s' could not be resolved" % args
			print dir(o)
		def man(cmds, args):
			'''Get the docs on the given arg'''
			o = type('base' , (object,), self.objects)
			for x in args.split('.'):
				if hasattr(o, x):
					o = getattr(o, x)
				else:
					raise Exception, "'%s' could not be resolved" % args
			help(o)
		def _help(cmds, opt=None):
			'''Prints this message'''
			if opt in cmds:
				v = cmds[opt]
				print opt
				for line in v.__doc__.split('\n'):
					line = line.strip()
					if not line: continue
					print ' '*4, line
				return
			if opt:
				raise Exception, "Command %s not found." % opt
			keys = cmds.keys()
			keys.sort()
			for k in keys:
				v = cmds[k]
				if type(v) != type(_help): continue
				print k
				for line in v.__doc__.split('\n'):
					line = line.strip()
					if not line: continue
					print ' '*4, line
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
			if not cmds.has_key(cmd_name):
				raise Exception, "command '%s' not found." % cmd_name
			cmd = cmds[cmd_name]

			if 'args' in cmd.func_code.co_varnames and args != str():
				return cmd(cmds, args)
			elif 'args' in cmd.func_code.co_varnames and args == str():
				raise Exception, "'%s' requires arguments, but none given" % cmd_name
			elif 'opt' in cmd.func_code.co_varnames and args != str():
				return cmd(cmds, opt=args)
			elif 'args' not in cmd.func_code.co_varnames and args != str():
				raise Exception, "'%s' does not except arguments" % cmd_name
			else:
				return cmd(cmds)
		except Exception, e:
			print '\n-----------ERROR-----------'
			print 'error: ', e
			print 'command: ', cmd_name
			print 'arguments: ', args
			print '-----------ERROR-----------\n'
			#raise

	def loadhist(self):
		try:
			f = open(self.histfile, 'r')
		except:
			return list()
		hist = list()
		for l in f:
			l = list(l[:-1])
			if not l: continue
			hist.append(l)
		f.close()
		if len(hist) > 50: return hist[-50:]
		return hist

	def savehist(self, hist):
		try:
			f = open(self.histfile, 'w')
		except:
			return
		for l in hist:
			if not l: continue
			f.write(''.join(l) + '\n')
		f.close()


	def start(self):
		print 'Welcome to the OFS REPL!'
		print 'type "help" to get started.'
		up = chr(27)+chr(91)+chr(65)
		down = chr(27)+chr(91)+chr(66)
		left = chr(27)+chr(91)+chr(68)
		right = chr(27)+chr(91)+chr(67)
		backspace = left + ' ' + left

		fd = sys.stdin.fileno()

		winsz = fcntl.ioctl(fd, termios.TIOCGWINSZ, "        ")
		rows, cols, xpixel, ypixel = struct.unpack('HHHH', winsz)

		old = termios.tcgetattr(fd)
		new = termios.tcgetattr(fd)
		new[3] = new[3] & ~ termios.ICANON
		new[3] = new[3] & ~ termios.ECHOCTL
		termios.tcsetattr(fd, termios.TCSADRAIN, new)

		curpos = [0, 2, 0]

		def clear_block(top):
			mvcur((top+1, 0))
			for x in xrange(top+1):
				sys.stdout.write(down)
				clear_line()
		def clear_line():
			sys.stdout.flush()

			#for x in xrange(cols - l):
				#sys.stdout.write(right)
			sys.stdout.write(left*cols)
			sys.stdout.write(' '*cols)
			sys.stdout.write(left*cols)
			#print curpos
			sys.stdout.flush()

		def moveleft(curpos, inpt):
			if curpos[2] == 0 and curpos[1] == 0:
				return
			elif curpos[2] > 0  and curpos[1] == 0:
				curpos[1] = cols - 1
				curpos[0] += 1
			elif curpos[1] > 0:
				curpos[1] -= 1
			#curpos[2] = (len(inpt) + 2)/cols
			if curpos[0] > curpos[2]: curpos[0] = curpos[2]

		def moveright(curpos, inpt):
			old2 = curpos[2]
			old1 = curpos[1]
			if (len(inpt) + 2)/cols > curpos[2]:
				curpos[2] = (len(inpt) + 2)/cols
			if curpos[1] < cols - 1:
				curpos[1] += 1
			elif curpos[1] >= cols -1:
				curpos[1] = 0
				if curpos[0] > 0: curpos[0] -= 1
			if old2 != curpos[2] and old1 != cols-1:
				curpos[0] += 1
			if curpos[2] > old2:
				sys.stdout.write('\n')
				clear_line()

		def reset(curpos):
			curpos[0] = 0
			curpos[1] = 2
			curpos[2] = 0

		def setcur(curpos, inpt):
			reset(curpos)
			if len(inpt) < cols-1:
				curpos[1] += len(inpt)
			else:
				curpos[2] = (len(inpt) + 2)/cols
				curpos[1] = (len(inpt) + 2)%cols

		def mvcur(curpos):
			for x in xrange(rows): sys.stdout.write(down)
			for x in xrange(cols): sys.stdout.write(left)
			for x in xrange(curpos[0]): sys.stdout.write(up)
			for x in xrange(curpos[1]): sys.stdout.write(right)
			sys.stdout.flush()

		try:
			history = self.loadhist()
			histpos = -1
			exit = False
			while not exit:
				#prompt = raw_input('> ')
				sys.stdout.write('> ')
				sys.stdout.flush()
				inpt = list()
				inptpos = 0
				reset(curpos)
				x = ''
				while 1:
					try:
						x = os.read(fd, 1)
					except KeyboardInterrupt:
						sys.stdout.write('\n')
						clear_line()
						print 'exit'
						exit = True
						break
					if ord(x) == 127:
						if inpt == list(): continue
						if curpos[2] == curpos[0] and curpos[1] == 2:
							continue
						inptpos -= 1
						del inpt[inptpos]
						moveleft(curpos, inpt)
					elif ord(x) == 27:
						os.read(fd, 1)
						z = os.read(fd, 1)
						if ord(z) == 65: #up
							sys.stdout.write(chr(27)+chr(91)+chr(66))
							if history: inpt = list(history[histpos])
							if histpos == -1: histpos = len(history) - 1
							histpos -= 1
							inptpos = len(inpt)
							setcur(curpos, inpt)
						elif ord(z) == 66: #down
							#sys.stdout.write(chr(27)+chr(91)+chr(65))
							histpos = -1
							inpt = list()
							inptpos = 0
							reset(curpos)
						elif ord(z) == 67: #right
							if inptpos < len(inpt):
								inptpos += 1
								moveright(curpos, inpt)
							else:
								sys.stdout.write(left)
						elif ord(z) == 68: #left
							if inptpos > 0:
								inptpos -= 1
								moveleft(curpos, inpt)
							else:
								sys.stdout.write(right)
					else:
						if x == '\n': break
						inpt.insert(inptpos, x)
						inptpos += 1
						moveright(curpos, inpt)

					clear_block(curpos[2])
					mvcur((curpos[2], 0))
					clear_line()
					sys.stdout.write('> ')
					r = 0
					l = min(cols-2, len(inpt))
					sys.stdout.write(''.join(inpt[r:l]))
					sys.stdout.flush()
					while l < len(inpt):
						sys.stdout.write(down)
						clear_line()
						sys.stdout.flush()
						r = l
						l = min(l+cols, len(inpt))
						sys.stdout.write(''.join(inpt[r:l]))
						sys.stdout.flush()
					if curpos[0] < curpos[2] and curpos[1] == 0:
						sys.stdout.write(down)
						clear_line()
						sys.stdout.flush()
					#sys.stdout.write(''.join(inpt))
					sys.stdout.flush()
					mvcur(curpos)

				if not history or not ''.join(history[-1]) == ''.join(inpt):
					history.append(inpt)
				histpos = -1
				#print prompt
				if not exit: exit = self.exe(''.join(inpt))
				#exit = True
		finally:
			self.savehist(history)
			termios.tcsetattr(fd, termios.TCSADRAIN, old)
