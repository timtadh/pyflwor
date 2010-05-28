
from ply import yacc
from lexer import tokens, Lexer

# Parsing rules
class Parser(object):

	def __new__(cls, **kwargs):
		self = super(Parser, cls).__new__(cls, **kwargs)
		self.names = dict()
		self.yacc = yacc.yacc(module=self, **kwargs)
		return self.yacc

	tokens = tokens
	precedence = tuple()

	def p_Query1(self, t):
		'Query : Query SLASH Entity'
		print t

	def p_Query2(self, t):
		'Query : Entity'
		print t

	def p_Entity1(self, t):
		'Entity : NAME'
		print t

	def p_Entity2(self, t):
		'Entity : NAME LSQUARE Where RSQUARE'
		print t

	def p_Where(self, t):
		'Where : OrExpr'
		print t

	def p_OrExpr1(self, t):
		'OrExpr : OrExpr OR AndExpr'
		print t

	def p_OrExpr2(self, t):
		'OrExpr : AndExpr'
		print t

	def p_AndExpr1(self, t):
		'AndExpr : AndExpr AND NotExpr'
		print t

	def p_AndExpr2(self, t):
		'AndExpr : NotExpr'
		print t

	def p_NotExpr1(self, t):
		'NotExpr : NOT BooleanExpr'
		print t

	def p_NotExpr2(self, t):
		'NotExpr : BooleanExpr'
		print t

	def p_BooleanExpr1(self, t):
		'BooleanExpr : CmpExpr'
		print t

	def p_BooleanExpr4(self, t):
		'BooleanExpr : LPAREN Where RPAREN'
		print t

	def p_CmpExpr(self, t):
		'CmpExpr : Value CmpOp Value'
		print t

	def p_CmpOp(self, t):
		'''CmpOp : EQ
				 | NQ
				 | LT
				 | LE
				 | GT
				 | GE'''
		print t

	def p_Value1(self, t):
		'Value : NUMBER'
		print t

	def p_Value2(self, t):
		'Value : STRING'
		print t

	def p_Value3(self, t):
		'Value : LANGLE AttributeValue RANGLE'
		print t

	def p_Value4(self, t):
		'Value : AttributeValue'
		print t

	def p_AttributeValue1(self, t):
		'AttributeValue : AttributeValue DOT Attr'
		print t

	def p_AttributeValue2(self, t):
		'AttributeValue : Attr'
		print t

	def p_ParameterList1(self, t):
		'ParameterList : ParameterList COMMA Value'
		print t

	def p_ParameterList2(self, t):
		'ParameterList : Value'
		print t

	def p_Attr1(self, t):
		'Attr : NAME'
		print t

	def p_Attr2(self, t):
		'Attr : NAME Call'
		print t

	def p_Call1(self, t):
		'Call : Call Call_'
		print t

	def p_Call2(self, t):
		'Call : Call_'
		print t

	def p_Call_1(self, t):
		'Call_ : Fcall'
		print t

	def p_Call_2(self, t):
		'Call_ : Dcall'
		print t

	def p_Fcall1(self, t):
		'Fcall : LPAREN RPAREN'
		print t

	def p_Fcall2(self, t):
		'Fcall : LPAREN ParameterList RPAREN'
		print t

	def p_Dcall(self, t):
		'Dcall : LSQUARE Value RSQUARE'
		print t

	def p_error(self, t):
		raise Exception, "Syntax error at '%s'" % t


if __name__ == '__main__':
	#Parser().parse('''a/b[x == y and not (1 == 1 or 1 == 2) and not c == d]/c/d''', lexer=Lexer())
	try:
		Parser().parse('''a/b[a==b.as.s and c == e.f.as[1](x, y, z, "hello []12^w234,.23")[2][q(b[5][6].c).qw.d] and __getitem__(1) == "213" and not f==<g.ae.wse().sd>]/e/f/g''', lexer=Lexer())
		print "SUCCESS"
	except Exception, e:
		print e
		print "FAILURE"
	#Parser().parse('Attr1.SubAttr.SubSubAttr', lexer=Lexer())
