
# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables -- all in one file.
# -----------------------------------------------------------------------------

from ply import lex
from ply.lex import Token

tokens = ('NUMBER', 'STRING', 'NAME', 'SOME', 'EVERY', 'IN', 'NOT', 'SATISFIES', 'AND', 'OR',
			'SLASH', 'EQ', 'NQ', 'LT', 'LE', 'GT', 'GE', 'COMMA',  'DOT', #'DOLLAR', 'COLON',
			'UNION', 'INTERSECTION', 'DIFFERENCE',
			'LPAREN', 'RPAREN', 'LSQUARE', 'RSQUARE', 'LANGLE', 'RANGLE')
reserved = {'some':'SOME', 'every':'EVERY', 'in':'IN', 'not':'NOT', 'satisfies':'SATISFIES',
			'and':'AND', 'or':'OR'}

D = r'[0-9]'
L = r'[a-zA-Z_]'
H = r'[a-fA-F0-9]'
E = r'[Ee][+-]?(' + D + ')+'

# Tokens

class Lexer(object):

	def __new__(cls, **kwargs):
		self = super(Lexer, cls).__new__(cls, **kwargs)
		self.lexer = lex.lex(object=self, **kwargs)
		return self.lexer

	tokens = tokens

	t_EQ = r'=='
	t_NQ = r'!='
	t_LT = r'<'
	t_LE = r'<='
	t_GT = r'>'
	t_GE = r'>='
	t_DOT = r'\.'
	t_COMMA = r','
	#t_COLON = r'\:'
	t_SLASH = r'/'
	t_UNION = r'\|'
	#t_DOLLAR = r'\$'
	t_LPAREN = r'\('
	t_RPAREN = r'\)'
	t_LANGLE = r'\<'
	t_RANGLE = r'\>'
	t_LSQUARE  = r'\['
	t_RSQUARE  = r'\]'
	t_DIFFERENCE = r'-'
	t_INTERSECTION = r'&'


	string_literal = r'\"[^"]*\"'
	@Token(string_literal)
	def t_STRING_LITERAL(self, token):
		token.type = 'STRING'
		token.value = token.value[1:-1]
		return token;

	name = '(' + L + ')((' + L + ')|(' + D + '))*'
	@Token(name)
	def t_NAME(self, token):
		if token.value in reserved: token.type = reserved[token.value]
		else: token.type = 'NAME'
		return token

	const_hex = '0[xX](' + H + ')+'
	@Token(const_hex)
	def t_CONST_HEX(self, token):
		token.type = 'NUMBER'
		token.value = int(token.value, 16)
		return token

	const_float1 = '(' + D + ')+' + '(' + E + ')' #{D}+{E}{FS}?
	@Token(const_float1)
	def t_CONST_FLOAT1(self, token):
		token.type = 'NUMBER'
		token.value = float(token.value)
		return token

	const_float2 = '(' + D + ')*\.(' + D + ')+(' + E + ')?' #{D}*"."{D}+({E})?{FS}?
	@Token(const_float2)
	def t_CONST_FLOAT2(self, token):
		token.type = 'NUMBER'
		token.value = float(token.value)
		return token

	const_dec_oct = '(' + D + ')+'
	@Token(const_dec_oct)
	def t_CONST_DEC_OCT(self, token):
		token.type = 'NUMBER'
		if len(token.value) > 1 and token.value[0] == '0':
			token.value = int(token.value, 8)
		else:
			token.value = int(token.value, 10)
		return token

	@Token(r'\n+')
	def t_newline(self, t):
		t.lexer.lineno += t.value.count("\n")

	# Ignored characters
	t_ignore = " \t"

	def t_error(self, t):
		raise Exception, "Illegal character '%s'" % t
		t.lexer.skip(1)




if __name__ == '__main__':
	lexer = Lexer()
	print lexer.input('.')
	#print lexer.input('''Finding[Severity == 3.0 and (Catagory == "12" or Catagory == "17")]
						#/
						#Trace
							#[
								#every $node in Trace/Node
								#statisfies $node in Finding[Severity == 3.0]/Trace/Node
							#]''')
	print [x for x in lexer]
	#while 1:
		#try:
			#s = raw_input('calc>>> ')
		#except EOFError:
			#break
		#Parser().parse(s, lexer=Lexer())
