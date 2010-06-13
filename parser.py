'''
PyQuery - The Python Object Query System
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: parser.py
Purpose: The LALR parser for the query compiler.
'''

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
	precedence = (
		('right', 'RSQUARE'),
	)

	def p_Set1(self, t):
		'Set : Set DIFFERENCE UnionExpr'
		t[0] = symbols.setValue(t[1], symbols.setoperator(t[2]), t[3])

	def p_Set2(self, t):
		'Set : UnionExpr'
		t[0] = t[1]

	def p_UnionExpr1(self, t):
		'UnionExpr : UnionExpr UNION IntersectionExpr'
		t[0] = symbols.setValue(t[1], symbols.setoperator(t[2]), t[3])

	def p_UnionExpr2(self, t):
		'UnionExpr : IntersectionExpr'
		t[0] = t[1]

	def p_IntersectionExpr1(self, t):
		'IntersectionExpr : IntersectionExpr INTERSECTION Collection'
		t[0] = symbols.setValue(t[1], symbols.setoperator(t[2]), t[3])

	def p_IntersectionExpr2(self, t):
		'IntersectionExpr : Collection'
		t[0] = t[1]

	def p_Collection1(self, t):
		'Collection : Query'
		t[0] = t[1]

	def p_Collection2(self, t):
		'Collection : LPAREN Set RPAREN'
		t[0] = t[2]

	def p_QueryStart(self, t):
		'Query : Query_'
		t[0] = symbols.queryValue(t[1])

	def p_Query1(self, t):
		'Query_ : Query_ SLASH Entity'
		t[0] = t[1] + [t[3]]

	def p_Query2(self, t):
		'Query_ : Entity'
		t[0] = [t[1]]

	def p_Entity1(self, t):
		'Entity : NAME'
		t[0] = (t[1], symbols.whereValue(lambda objs: True))

	def p_Entity2(self, t):
		'Entity : NAME LSQUARE Where RSQUARE'
		t[0] = (t[1], symbols.whereValue(t[3]))

	def p_Where(self, t):
		'Where : OrExpr'
		t[0] = t[1]

	def p_OrExpr1(self, t):
		'OrExpr : OrExpr OR AndExpr'
		t[0] = symbols.booleanexprValue(t[1], symbols.booleanOperator(t[2]), t[3])

	def p_OrExpr2(self, t):
		'OrExpr : AndExpr'
		t[0] = t[1]

	def p_AndExpr1(self, t):
		'AndExpr : AndExpr AND NotExpr'
		t[0] = symbols.booleanexprValue(t[1], symbols.booleanOperator(t[2]), t[3])

	def p_AndExpr2(self, t):
		'AndExpr : NotExpr'
		t[0] = t[1]

	def p_NotExpr1(self, t):
		'NotExpr : NOT BooleanExpr'
		t[0] = symbols.unaryexprValue(symbols.unaryOperator(t[1]), t[2])

	def p_NotExpr2(self, t):
		'NotExpr : BooleanExpr'
		t[0] = t[1]

	def p_BooleanExpr1(self, t):
		'BooleanExpr : CmpExpr'
		t[0] = t[1]

	def p_BooleanExpr2(self, t):
		'BooleanExpr : QuantifiedExpr'
		t[0] = t[1]

	def p_BooleanExpr3(self, t):
		'BooleanExpr : SetExpr'
		t[0] = t[1]

	def p_BooleanExpr4(self, t):
		'BooleanExpr : Value'
		t[0] = symbols.booleanValue(t[1])

	def p_BooleanExpr5(self, t):
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

	def p_Value4(self, t):
		'Value : AttributeValue'
		t[0] = symbols.attributeValue(t[1])

	def p_AttributeValue1(self, t):
		'AttributeValue : AttributeValue DOT Attr'
		t[0] = t[1] + [t[3]]

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

	def p_Dcall(self, t):
		'Dcall : LSQUARE Value RSQUARE'
		t[0] = symbols.Call([t[2]], lookup=True)

	def p_QuantifiedExpr(self, t):
		'QuantifiedExpr : Quantifier NAME IN LANGLE Set RANGLE SATISFIES LPAREN Where RPAREN'
		t[0] = symbols.quantifiedValue(t[1], t[2], t[5], t[9])

	def p_Quantifier1(self, t):
		'Quantifier : EVERY'
		t[0] = t[1]

	def p_Quantifier2(self, t):
		'Quantifier : SOME'
		t[0] = t[1]

	def p_SetExpr1(self, t):
		'SetExpr : Value IN LANGLE Set RANGLE'
		t[0] = symbols.setexprValue1(t[1], symbols.setexprOperator1('in'), t[4])

	def p_SetExpr2(self, t):
		'SetExpr : Value NOT IN LANGLE Set RANGLE'
		t[0] = symbols.setexprValue1(t[1], symbols.setexprOperator1('not in'), t[5])

	def p_SetExpr3(self, t):
		'SetExpr : LANGLE Set RANGLE SUBSET LANGLE Set RANGLE'
		t[0] = symbols.setexprValue2(t[2], symbols.setexprOperator2('subset'), t[6])

	def p_SetExpr4(self, t):
		'SetExpr : LANGLE Set RANGLE SUPERSET LANGLE Set RANGLE'
		t[0] = symbols.setexprValue2(t[2], symbols.setexprOperator2('superset'), t[6])

	def p_SetExpr5(self, t):
		'SetExpr : LANGLE Set RANGLE PROPER SUBSET LANGLE Set RANGLE'
		t[0] = symbols.setexprValue2(t[2], symbols.setexprOperat2or('proper subset'), t[7])

	def p_SetExpr6(self, t):
		'SetExpr : LANGLE Set RANGLE PROPER SUPERSET LANGLE Set RANGLE'
		t[0] = symbols.setexprValue2(t[2], symbols.setexprOperator2('proper superset'), t[7])

	def p_SetExpr7(self, t):
		'SetExpr : LANGLE Set RANGLE IS LANGLE Set RANGLE'
		t[0] = symbols.setexprValue2(t[2], symbols.setexprOperator2('is'), t[6])

	def p_SetExpr8(self, t):
		'SetExpr : LANGLE Set RANGLE IS NOT LANGLE Set RANGLE'
		t[0] = symbols.setexprValue2(t[2], symbols.setexprOperator2('is not'), t[7])

	def p_error(self, t):
		raise Exception, "Syntax error at '%s', %s.%s" % (t,t.lineno,t.lexpos)


if __name__ == '__main__':
	#Parser().parse('''a/b[x == y and not (1 == 1 or 1 == 2) and not c == d]/c/d''', lexer=Lexer())
	try:
		#Parser()
		#Parser().parse('''a/b[a==b.as.s and c == e.f.as[1](x, y, z, "hello []12^w234,.23")[2][q(b[5]
		#[6].c).qw.d] and __getitem__(1) == "213" and not f==<g.ae.wse().sd>]/e/f/g''', lexer=Lexer())
		#Parser().parse('a/b[x not in a/b/x - q/w/x | y/x and every y in a/b/c satisfies (y == x)]', lexer=Lexer())
		#query = Parser().parse('''a[not (not self.a()[1](<gx>,self.z.z.b,self.a)[1] == "b attr" and
									#not 1 == 1)]/z/z/z/x[self.__mod__(2)]''', lexer=Lexer())
		query = Parser().parse('''a[self.f or not self.f]/d[self.value.__mod__(2)]/key''', lexer=Lexer())
		class A(object): pass
		a = A()
		a.t = True
		a.f = False
		a.q = [1,3,5]
		a.r = [1,2,5,6]
		a.x = [1,2,3,4,5,6]
		a.d = {'one':1, 'two':2}
		a.y = 'y attr'
		a.z = a
		a.a = lambda : [0, lambda x,y,z: ((x,y,z))]
		a.b = 'b attr'
		print tuple(query({'a':a, 'gx':'gx attr'}))
		print "SUCCESS"
	except Exception, e:
		print e
		print "FAILURE"
		raise
	#Parser().parse('Attr1.SubAttr.SubSubAttr', lexer=Lexer())
