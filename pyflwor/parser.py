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

## The parser does not build an abstract syntax tree nor does it build
## intermediate code, instead it composes functions and objects together. These
## functions are defined in symbols.py file. The composed function returned
## computes the query based on the object dictionary passed into it. This
## dictionary (objs) is passed down through the functions (sometimes with
## modification).

## If you are confused about the syntax in this file I recommend reading the
## documentation on the PLY website to see how this compiler compiler's syntax
## works.
class Parser(object):

    def __new__(cls, **kwargs):
        ## Does magic to allow PLY to do its thing.
        self = super(Parser, cls).__new__(cls, **kwargs)
        self.names = dict()
        self.yacc = yacc.yacc(module=self, **kwargs)
        return self.yacc

    tokens = tokens
    precedence = (
        ('right', 'RSQUARE'),
    )

    def p_Start1(self, t):
        'Start : Set'
        t[0] = t[1]

    def p_Start2(self, t):
        'Start : FLWRexpr'
        t[0] = t[1]

    def p_FLWRexpr1(self, t):
        'FLWRexpr : ForExpr ReturnExpr'
        t[0] = symbols.flwrSequence(t[2][0], for_expr=t[1], flatten=t[2][1], reduce_return=t[2][2])

    def p_FLWRexpr2(self, t):
        'FLWRexpr : ForExpr LetExpr ReturnExpr'
        t[0] = symbols.flwrSequence(t[3][0], for_expr=t[1], flatten=t[3][1], reduce_return=t[3][2], let_expr=t[2])

    def p_FLWRexpr3(self, t):
        'FLWRexpr : ForExpr WhereExpr ReturnExpr'
        t[0] = symbols.flwrSequence(t[3][0], for_expr=t[1], flatten=t[3][1], reduce_return=t[3][2], where_expr=t[2])

    def p_FLWRexpr4(self, t):
        'FLWRexpr : ForExpr LetExpr WhereExpr ReturnExpr'
        t[0] = symbols.flwrSequence(t[4][0], for_expr=t[1], flatten=t[4][1], reduce_return=t[4][2], let_expr=t[2], where_expr=t[3])

    def p_FLWRexpr5(self, t):
        'FLWRexpr : ForExpr OrderByExpr ReturnExpr'
        t[0] = symbols.flwrSequence(t[3][0], for_expr=t[1], flatten=t[3][1], reduce_return=t[3][2], order_expr=t[2])

    def p_FLWRexpr6(self, t):
        'FLWRexpr : ForExpr LetExpr OrderByExpr ReturnExpr'
        t[0] = symbols.flwrSequence(t[4][0], for_expr=t[1], flatten=t[4][1], reduce_return=t[4][2], let_expr=t[2], order_expr=t[3])

    def p_FLWRexpr7(self, t):
        'FLWRexpr : ForExpr WhereExpr OrderByExpr ReturnExpr'
        t[0] = symbols.flwrSequence(t[4][0], for_expr=t[1], flatten=t[4][1], reduce_return=t[4][2], where_expr=t[2], order_expr=t[3])

    def p_FLWRexpr8(self, t):
        'FLWRexpr : ForExpr LetExpr WhereExpr OrderByExpr ReturnExpr'
        t[0] = symbols.flwrSequence(t[5][0], for_expr=t[1], flatten=t[5][1], reduce_return=t[5][2], let_expr=t[2], where_expr=t[3], order_expr=t[4])

    def p_FLWRexpr9(self, t):
        'FLWRexpr : ReturnExpr'
        t[0] = symbols.flwrSequence(t[1][0], flatten=t[1][1], reduce_return=t[1][2])

    def p_FLWRexpr10(self, t):
        'FLWRexpr : LetExpr ReturnExpr'
        t[0] = symbols.flwrSequence(t[2][0], flatten=t[2][1], reduce_return=t[2][2], let_expr=t[1])

    def p_ForExpr(self, t):
        'ForExpr : FOR ForList'
        t[0] = t[2]

    def p_ForList1(self, t):
        'ForList : ForList COMMA ForDefinition'
        t[0] = t[1] + [t[3]]

    def p_ForList2(self, t):
        'ForList : ForDefinition'
        t[0] = [t[1]]

    def p_ForDefinition1(self, t):
        'ForDefinition : NAME IN LANGLE Set RANGLE'
        t[0] = (t[1], t[4])

    def p_ForDefinition2(self, t):
        'ForDefinition : NAME IN LCURLY FLWRexpr RCURLY'
        t[0] = (t[1], t[4])

    def p_ForDefinition3(self, t):
        'ForDefinition : NAME IN Value'
        t[0] = (t[1], t[3])

    def p_LetExpr1(self, t):
        'LetExpr : LetExpr LET LetList'
        t[0] = t[1] + t[3]

    def p_LetExpr2(self, t):
        'LetExpr : LET LetList'
        t[0] = t[2]

    def p_LetList1(self, t):
        'LetList : LetList COMMA LetDefinition'
        t[0] = t[1] + [t[3]]

    def p_LetList2(self, t):
        'LetList : LetDefinition'
        t[0] = [t[1]]

    def p_LetDefinition1(self, t):
        'LetDefinition : NAME EQ LANGLE Set RANGLE'
        t[0] = (t[1], t[4])

    def p_LetDefinition2(self, t):
        'LetDefinition : NAME EQ LCURLY FLWRexpr RCURLY'
        t[0] = (t[1], t[4])

    def p_LetDefinition3(self, t):
        'LetDefinition : NAME EQ AttributeValue'
        t[0] = (t[1], symbols.attributeValue(t[3]))

    def p_LetDefinition4(self, t):
        'LetDefinition : NAME EQ Function'
        t[0] = (t[1], symbols.functionDefinition(*t[3]))

    def p_Function1(self, t):
        'Function : FUNCTION LPAREN RPAREN LCURLY FBody RCURLY'
        t[0] = (tuple(), t[5])

    def p_Function2(self, t):
        'Function : FUNCTION LPAREN FParams RPAREN LCURLY FBody RCURLY'
        t[0] = (tuple(t[3]), t[6])

    def p_FParams1(self, t):
        'FParams : FParams COMMA NAME'
        t[0] = t[1] + [t[3]]

    def p_FParams2(self, t):
        'FParams : NAME'
        t[0] = [t[1]]

    def p_Fbody1(self, t):
        'FBody : FLWRexpr'
        t[0] = t[1]

    def p_Fbody3(self, t):
        'FBody : Value'
        t[0] = t[1]

    def p_WhereExpr(self, t):
        'WhereExpr : WHERE Where'
        t[0] = t[2]

    def p_OrderByExpr1(self, t):
        'OrderByExpr : ORDER BY NUMBER OrderDirection'
        t[0] = (t[3], t[4])

    def p_OrderByExpr2(self, t):
        'OrderByExpr : ORDER BY STRING OrderDirection'
        t[0] = (t[3], t[4])

    def p_OrderDirection1(self, t):
        'OrderDirection : ASCD'
        t[0] = 'ASCD'

    def p_OrderDirection2(self, t):
        'OrderDirection : DESC'
        t[0] = 'DESC'

    def p_ReturnExpr1(self, t):
        'ReturnExpr : RETURN OutputTuple'
        t[0] = (t[2], False, False)

    def p_ReturnExpr2(self, t):
        'ReturnExpr : RETURN OutputDict'
        t[0] = (t[2], False, False)

    def p_ReturnExpr3(self, t):
        'ReturnExpr : RETURN FLATTEN OutputValue'
        t[0] = ([t[3]], True, False)

    def p_ReturnExpr4(self, t):
        'ReturnExpr : REDUCE OutputTuple AS Value WITH ReduceFunction'
        t[0] = ({'value':t[2], 'as':t[4], 'with':t[6]}, False, True)

    def p_ReturnExpr5(self, t):
        'ReturnExpr : REDUCE OutputDict AS Value WITH ReduceFunction'
        t[0] = ({'value':t[2], 'as':t[4], 'with':t[6]}, False, True)

    def p_ReduceFunction1(self, t):
        'ReduceFunction : AttributeValue'
        t[0] = symbols.attributeValue(t[1])

    def p_ReduceFunction2(self, t):
        'ReduceFunction : Function'
        t[0] = symbols.functionDefinition(*t[1])

    def p_OutputTuple1(self, t):
        'OutputTuple : OutputTuple COMMA OutputValue'
        t[0] = t[1] + [t[3]]

    def p_OutputTuple2(self, t):
        'OutputTuple : OutputValue'
        t[0] = [t[1]]

    def p_OutputDict1(self, t):
        'OutputDict : OutputDict COMMA STRING COLON OutputValue'
        t[0] = t[1] + [(t[3], t[5])]

    def p_OutputDict2(self, t):
        'OutputDict : STRING COLON OutputValue'
        t[0] = [(t[1], t[3])]

    def p_OutputValue1(self, t):
        'OutputValue : Value'
        t[0] = t[1]

    def p_OutputValue2(self, t):
        'OutputValue : LANGLE Set RANGLE'
        t[0] = t[2]

    def p_OutputValue3(self, t):
        'OutputValue : LCURLY FLWRexpr RCURLY'
        t[0] = t[2]

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
        '''CmpOp : EQEQ
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
        'Value : IF Where THEN IfBody ELSE IfBody'
        t[0] = symbols.ifExpr(t[2], t[4], t[6])

    def p_Value4(self, t):
        'Value : AttributeValue'
        t[0] = symbols.attributeValue(t[1])

    def p_Value5(self, t):
        'Value : LCURLY NameValPairs RCURLY'
        t[0] = symbols.dictValue(t[2])

    def p_NameValPairs1(self, t):
        'NameValPairs : NameValPairs COMMA NameValPair'
        t[0] = t[1] + [t[3]]

    def p_NameValPairs2(self, t):
        'NameValPairs : NameValPair'
        t[0] = [t[1]]

    def p_NameValPair(self, t):
        'NameValPair : Value COLON Value'
        t[0] = (t[1], t[3])

    def p_IfBody1(self, t):
        'IfBody : Value'
        t[0] = t[1]

    def p_IfBody2(self, t):
        'IfBody : LANGLE Set RANGLE'
        t[0] = t[2]

    def p_IfBody3(self, t):
        'IfBody : LCURLY FLWRexpr RCURLY'
        t[0] = t[2]

    def p_AttributeValue1(self, t):
        'AttributeValue : AttributeValue DOT Attr'
        t[0] = t[1] + [t[3]]

    def p_AttributeValue2(self, t):
        'AttributeValue : Attr'
        t[0] = [t[1]]

    def p_ParameterList1(self, t):
        'ParameterList : ParameterList COMMA Parameter'
        t[0] = t[1] + [t[3]]

    def p_ParameterList2(self, t):
        'ParameterList : Parameter'
        t[0] = [t[1]]

    def p_Parameter1(self, t):
        'Parameter : Value'
        t[0] = t[1]

    def p_Parameter2(self, t):
        'Parameter : LANGLE Set RANGLE'
        t[0] = t[2]

    def p_Parameter3(self, t):
        'Parameter : LCURLY FLWRexpr RCURLY'
        t[0] = t[2]

    def p_Attr1(self, t):
        'Attr : NAME'
        t[0] = symbols.Attribute(t[1])

    def p_Attr2(self, t):
        'Attr : NAME Call'
        t[0] = symbols.Attribute(t[1], t[2])

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

    def p_QuantifiedExpr1(self, t):
        'QuantifiedExpr : Quantifier NAME IN LANGLE Set RANGLE SATISFIES LPAREN Where RPAREN'
        t[0] = symbols.quantifiedValue(t[1], t[2], t[5], t[9])

    def p_QuantifiedExpr2(self, t):
        'QuantifiedExpr : Quantifier NAME IN LCURLY FLWRexpr RCURLY SATISFIES LPAREN Where RPAREN'
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
        t[0] = symbols.setexprValue2(t[2], symbols.setexprOperator2('proper subset'), t[7])

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
        raise SyntaxError, "Syntax error at '%s', %s.%s" % (t,t.lineno,t.lexpos)


if __name__ == '__main__':
    #Parser().parse('''a/b[x == y and not (1 == 1 or 1 == 2) and not c == d]/c/d''', lexer=Lexer())
    try:
        #Parser()
        #Parser().parse('''a/b[a==b.as.s and c == e.f.as[1](x, y, z, "hello []12^w234,.23")[2][q(b[5]
        #[6].c).qw.d] and __getitem__(1) == "213" and not f==<g.ae.wse().sd>]/e/f/g''', lexer=Lexer())
        #Parser().parse('a/b[x not in a/b/x - q/w/x | y/x and every y in a/b/c satisfies (y == x)]', lexer=Lexer())
        #query = Parser().parse('''a[not (not self.a()[1](<gx>,self.z.z.b,self.a)[1] == "b attr" and
                                    #not 1 == 1)]/z/z/z/x[self.__mod__(2)]''', lexer=Lexer())

        query = Parser().parse('''
                                    for r in <a/r>
                                    let tuple = {
                                                    for y in <a/x>
                                                    where r > y
                                                    return y
                                                }
                                    return "r":r, "tuple":tuple
                                ''', lexer=Lexer())
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
        print tuple(query({'a':a, 'gx':'gx attr', 'sum':sum, 'tuple':tuple}))
        print "SUCCESS"
    except Exception, e:
        print e
        print "FAILURE"
        raise
    #Parser().parse('Attr1.SubAttr.SubSubAttr', lexer=Lexer())
