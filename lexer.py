
# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables -- all in one file.
# -----------------------------------------------------------------------------

from ply import lex
import ply.yacc as yacc
from ply.lex import Token
tokens = (
		'NAME','NUMBER',
		'PLUS','MINUS','TIMES','DIVIDE','EQUALS',
		'LPAREN','RPAREN',
		)


# Tokens

class Lexer(object):
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
    
	def __new__(cls, **kwargs):
		self = super(Lexer, cls).__new__(cls, **kwargs)
		self.lexer = lex.lex(object=self, **kwargs)
		return self.lexer
		

# Parsing rules
class Parser(object):
	tokens = tokens
	precedence = (
		('left','PLUS','MINUS'),
		('left','TIMES','DIVIDE'),
		('right','UMINUS'),
		)

	def p_statement_assign(self, t):
		'statement : NAME EQUALS expression'
		names[t[1]] = t[3]

	def p_statement_expr(self, t):
		'statement : expression'
		print t[1]

	def p_expression_binop(self, t):
		'''expression : expression PLUS expression
					| expression MINUS expression
					| expression TIMES expression
					| expression DIVIDE expression'''
		if t[2] == '+'  : t[0] = t[1] + t[3]
		elif t[2] == '-': t[0] = t[1] - t[3]
		elif t[2] == '*': t[0] = t[1] * t[3]
		elif t[2] == '/': t[0] = t[1] / t[3]

	def p_expression_uminus(self, t):
		'expression : MINUS expression %prec UMINUS'
		t[0] = -t[2]

	def p_expression_group(self, t):
		'expression : LPAREN expression RPAREN'
		t[0] = t[2]

	def p_expression_number(self, t):
		'expression : NUMBER'
		t[0] = t[1]

	def p_expression_name(self, t):
		'expression : NAME'
		try:
			t[0] = names[t[1]]
		except LookupError:
			print "Undefined name '%s'" % t[1]
			t[0] = 0

	def p_error(self, t):
		print "Syntax error at '%s'" % t.value
	
	def __new__(cls, **kwargs):
		self = super(Parser, cls).__new__(cls, **kwargs)
		self.names = dict()
		self.yacc = yacc.yacc(module=self, **kwargs)
		return self.yacc

lexer = Lexer()
print lexer.input('1+\n5')
print [x for x in lexer]
#while 1:
    #try:
        #s = raw_input('calc>>> ')
    #except EOFError:
        #break
    #Parser().parse(s, lexer=Lexer())
