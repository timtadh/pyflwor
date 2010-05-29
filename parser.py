
from ply import yacc
from lexer import tokens, Lexer
import symbols

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
		#print t

	def p_Query2(self, t):
		'Query : Entity'
		#print t

	def p_Entity1(self, t):
		'Entity : NAME'
		#print t

	def p_Entity2(self, t):
		'Entity : NAME LSQUARE Where RSQUARE'
		#print t

	def p_Where(self, t):
		'Where : OrExpr'
		t[0] = t[1]
		class A(object): pass
		a = A()
		a.x = 'x attr'
		a.y = 'y attr'
		a.z = 'z attr'
		a.a = lambda : [0, lambda x,y,z: ((x,y,z))]
		a.b = 'b attr'
		objs = {'locals': dict((x, getattr(a, x)) for x in dir(a)), 'globals':{'gx':'gx global'}}
		print t[0](objs)

	def p_OrExpr1(self, t):
		'OrExpr : OrExpr OR AndExpr'
		def create(x, y):
			def oor(objs):
				return x(objs) or y(objs)
			return oor
		t[0] = create(t[1], t[3])

	def p_OrExpr2(self, t):
		'OrExpr : AndExpr'
		t[0] = t[1]

	def p_AndExpr1(self, t):
		'AndExpr : AndExpr AND NotExpr'
		def create(x, y):
			def annd(objs):
				return x(objs) and y(objs)
			return annd
		t[0] = create(t[1], t[3])

	def p_AndExpr2(self, t):
		'AndExpr : NotExpr'
		t[0] = t[1]

	def p_NotExpr1(self, t):
		'NotExpr : NOT BooleanExpr'
		def create(x):
			def noot(objs):
				return not x(objs)
			return noot
		t[0] = create(t[2])

	def p_NotExpr2(self, t):
		'NotExpr : BooleanExpr'
		t[0] = t[1]

	def p_BooleanExpr1(self, t):
		'BooleanExpr : CmpExpr'
		t[0] = t[1]

	def p_BooleanExpr2(self, t):
		'BooleanExpr : QuantifiedExpr'
		#print t

	def p_BooleanExpr3(self, t):
		'BooleanExpr : SetExpr'
		#print t

	def p_BooleanExpr4(self, t):
		'BooleanExpr : LPAREN Where RPAREN'
		t[0] = t[2]

	def p_CmpExpr(self, t):
		'CmpExpr : Value CmpOp Value'
		t[0] = symbols.comparisonValue(t[1], t[2], t[3])

	def p_CmpOp(self, t):
		'''CmpOp : EQ
				 | NQ
				 | LANGLE
				 | LE
				 | RANGLE
				 | GE'''
		t[0] = symbols.operator(t[1])

	def p_Value1(self, t):
		'Value : NUMBER'
		t[0] = symbols.attributeValue(t[1], scalar=True)

	def p_Value2(self, t):
		'Value : STRING'
		t[0] = symbols.attributeValue(t[1], scalar=True)

	def p_Value3(self, t):
		'Value : LANGLE AttributeValue RANGLE'
		t[0] = symbols.attributeValue(t[2], context='globals')

	def p_Value4(self, t):
		'Value : AttributeValue'
		t[0] = symbols.attributeValue(t[1], context='locals')

	def p_AttributeValue1(self, t):
		'AttributeValue : AttributeValue DOT Attr'
		t[0] = t[1] + [t[2]]

	def p_AttributeValue2(self, t):
		'AttributeValue : Attr'
		t[0] = [t[1]]

	def p_ParameterList1(self, t):
		'ParameterList : ParameterList COMMA Value'
		t[0] = t[1] + [t[3]]

	def p_ParameterList2(self, t):
		'ParameterList : Value'
		t[0] = [t[1]]

	def p_Attr1(self, t):
		'Attr : NAME'
		t[0] = symbols.Attribute(t[1])

	def p_Attr2(self, t):
		'Attr : NAME Call'
		t[0] = symbols.Attribute(t[1], t[2])
		#print t

	def p_Call1(self, t):
		'Call : Call Call_'
		t[0] = t[1] + [t[2]]

	def p_Call2(self, t):
		'Call : Call_'
		t[0] = [t[1]]

	def p_Call_1(self, t):
		'Call_ : Fcall'
		t[0] = t[1]

	def p_Call_2(self, t):
		'Call_ : Dcall'
		t[0] = t[1]

	def p_Fcall1(self, t):
		'Fcall : LPAREN RPAREN'
		t[0] = symbols.Call([])

	def p_Fcall2(self, t):
		'Fcall : LPAREN ParameterList RPAREN'
		t[0] = symbols.Call(t[2])
		#t[0] = symbols.Call(['PLACE HOLDER'])

	def p_Dcall(self, t):
		'Dcall : LSQUARE Value RSQUARE'
		t[0] = symbols.Call([t[2]], lookup=True)

	def p_QuantifiedExpr(self, t):
		'QuantifiedExpr : Quantifier NAME IN Set SATISFIES LPAREN Where RPAREN'
		#print t

	def p_Quantifier1(self, t):
		'Quantifier : EVERY'
		#print t

	def p_Quantifier2(self, t):
		'Quantifier : SOME'
		#print t

	def p_SetExpr1(self, t):
		'SetExpr : Value IN Set'
		#print t

	def p_SetExpr2(self, t):
		'SetExpr : Value NOT IN Set'
		#print t


	def p_Set1(self, t):
		'Set : Set DIFFERENCE UnionExpr'
		#print t

	def p_Set2(self, t):
		'Set : UnionExpr'
		#print t

	def p_UnionExpr1(self, t):
		'UnionExpr : UnionExpr UNION IntersectionExpr'
		#print t

	def p_UnionExpr2(self, t):
		'UnionExpr : IntersectionExpr'
		#print t

	def p_IntersectionExpr1(self, t):
		'IntersectionExpr : IntersectionExpr INTERSECTION Collection'
		#print t

	def p_IntersectionExpr2(self, t):
		'IntersectionExpr : Collection'
		#print t

	def p_Collection1(self, t):
		'Collection : Query'
		#print t

	def p_Collection2(self, t):
		'Collection : LPAREN Set RPAREN'
		#print t

	def p_error(self, t):
		raise Exception, "Syntax error at '%s'" % t


if __name__ == '__main__':
	#Parser().parse('''a/b[x == y and not (1 == 1 or 1 == 2) and not c == d]/c/d''', lexer=Lexer())
	try:
		#Parser()
		#Parser().parse('''a/b[a==b.as.s and c == e.f.as[1](x, y, z, "hello []12^w234,.23")[2][q(b[5][6].c).qw.d] and __getitem__(1) == "213" and not f==<g.ae.wse().sd>]/e/f/g''', lexer=Lexer())
		#Parser().parse('a/b[x not in a/b/x - q/w/x | y/x and every y in a/b/c satisfies (y == x)]', lexer=Lexer())
		Parser().parse('a[not (not a()[1](<gx>,b,z)[1] == "b attr" or not 1 == 1)]', lexer=Lexer())
		print "SUCCESS"
	except Exception, e:
		print e
		print "FAILURE"
		raise
	#Parser().parse('Attr1.SubAttr.SubSubAttr', lexer=Lexer())
