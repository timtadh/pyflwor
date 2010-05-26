
# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables -- all in one file.
# -----------------------------------------------------------------------------

from ply import lex
from ply.lex import Token

tokens = (
		'NAME','NUMBER',
		'PLUS','MINUS','TIMES','DIVIDE','EQUALS',
		'LPAREN','RPAREN',
		)


# Tokens

class Lexer(object):

	def __new__(cls, **kwargs):
		self = super(Lexer, cls).__new__(cls, **kwargs)
		self.lexer = lex.lex(object=self, **kwargs)
		return self.lexer

	tokens = tokens

	t_PLUS    = r'\+'
	t_MINUS   = r'-'
	t_TIMES   = r'\*'
	t_DIVIDE  = r'/'
	t_EQUALS  = r'='
	t_LPAREN  = r'\('
	t_RPAREN  = r'\)'
	t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'

	@Token(r'\d+')
	def t_NUMBER(self, t):
		try:
			t.value = int(t.value)
		except ValueError:
			print "Integer value too large", t.value
			t.value = 0
		return t

	@Token(r'\n+')
	def t_newline(self, t):
		t.lexer.lineno += t.value.count("\n")

	# Ignored characters
	t_ignore = " \t"

	def t_error(self, t):
		print "Illegal character '%s'" % t.value[0]
		t.lexer.skip(1)





lexer = Lexer()
print lexer.input('1+\n5')
print [x for x in lexer]
#while 1:
    #try:
        #s = raw_input('calc>>> ')
    #except EOFError:
        #break
    #Parser().parse(s, lexer=Lexer())
