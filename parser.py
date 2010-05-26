
from ply import yacc
from lexer import tokens

# Parsing rules
class Parser(object):

	def __new__(cls, **kwargs):
		self = super(Parser, cls).__new__(cls, **kwargs)
		self.names = dict()
		self.yacc = yacc.yacc(module=self, **kwargs)
		return self.yacc

	tokens = tokens
	precedence = (('left','PLUS','MINUS'),
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
