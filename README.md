
PyFlwor - The Python Object Query System
========================================


By Tim Henderson - tim.tadh@hackthology.com

Copyright 2010 Tim Henderson All Rights Reserved.
PyFlwor is available under a BSD style license. See the LICENSE file.


Table of Contents
-----------------

1. Introduction and Installation
2. Motivation
3. Usage Example
4. Writing PyFlwor
5. Formal Language Specification


Introduction
------------

PyFlwor is a query language for querying python object collections. While
Python has many interesting ways of persisting objects, it does not have (to my
knowledge) a query language. This language was inspired in part by OQL (Object
Query Language), XPath2.0, and XQuery. It is still under rapid development so
expect the language to change often. PyFlwor works on any type of Python object.
The only requirement is that the objects returned have to be hashable, as they
are currently returned as a set.

### Installation

To install `pyflwor` using pip first install the dependencies:

    pip install ply nose

nose is only required if you want to run the tests. You can also optionally
install `getline` if you want to use the included repl library:

    pip install -e git+https://github.com/timtadh/getline.git#egg=getline

finally you can directly install `pyflwor` using pip with:

    pip install -e git+https://github.com/timtadh/pyflwor.git#egg=pyflwor

or via clonin the repository and using the setup file:

    git clone https://github.com/timtadh/pyflwor.git
    cd pyflwor
    python setup.py install

to run the tests:

    cd pyflwor
    nosetests

Alternately, one may wish to automate the dependency install via the reqs.txt
file. In this case you should install as follows:
    
    git clone https://github.com/timtadh/pyflwor.git
    cd pyflwor
    IFS=$'\n' ; for req in `cat reqs.txt` ; do echo $req ; pip install $req ; done
    python setup.py install


Motivation
----------

The motivation for this work occured while working on a software system with a
unified namespace to address heterogenous data models. Some of the models were
relational, some were XML, and increasingly some were simply native python
objects. To unify this namespace I am working on this language. However, I
expect that since PyFlwor works on any Python object collection it may be
generally useful to the Python community.


Usage Example
-------------

    import pyflwor

    class Obj(object):
        def __init__(self, attr, attr2):
            self.attr = attr
            self.attr2 = attr2

    q = pyflwor.compile('''
        for obj in <objects>
        where obj.attr > 5
        return 'number':obj.attr, 'string':obj.attr2
    ''')

    objects = [
        Obj(5, 'hello'),
        Obj(12, 'world!'),
        Obj(32, '2^5'),
        Obj(42, 'the answer')
    ]

    print q(locals())

    ---------- results -----------

    (
        {'number': 12, 'string': 'world!'},
        {'number': 32, 'string': '2^5'},
        {'number': 42, 'string': 'the answer'}
    )


Writing PyFlwor
---------------

Like XPath and XQuery there are two ways to write queries in PyFlwor: "path"
expressions and "flwr" expressions. Path expressions have a similar syntax to
XPath. This short guide does not cover all the syntax available in PyFlwor but
should give the reader a good place to start when writing PyFlwor.

### Path Expressions

#### XML Example (for comparison):

    <?xml version="1.0" encoding="ISO-8859-1"?>
    <bookstore>
        <book>
            <title lang="eng">Harry Potter</title>
            <price>29.99</price>
        </book>
        <book>
            <title lang="eng">Learning XML</title>
            <price>39.95</price>
        </book>
    </bookstore>

#### XPath Queries:

1. all books

        /bookstore/book

2. all books with price greater than $30.00

        /bookstore/book[price>30.00]

#### Python Example

    class Book(object):
        def __init__(self, title, language, price):
            self.title = title
            self.language = language
            self.price = price

    class Bookstore(object):
        def __init__(self, name):
            self.name = name
            self.books = list()
        def addbook(self, book):
            self.books.append(book)

    bookstore = Bookstore('Tim\'s Books')
    bookstore.addbook(Book("Harry Potter", "eng", 29.99))
    bookstore.addbook(Book("Learning XML", "eng", 39.95))


#### PyFlwor Queries:

1. all books

        bookstore/books

2. all books with price greater than $30.00

        bookstore/books[self.price > 30.00]

The where condition in Path expression allows you access any object in the
namespace you passed into the query. It also names the current object under
consideration (in the working example the Book) 'self.' You can access any
attribute of self, call functions, and access items in lists and dicts.

#### A Ridiculous Example

    a = 'hello'
    def f(x): return x**2
    def g(f): return f
    m = {"one":1, "two":2, "next":[1,2,3,4,5,6,7,g]}
    true = True
    false = False
    d = locals()
    d.update(__builtins__.__dict__)

    query = 'a[m["next"][7](j)(m["next"][7])(m["next"])[7](f)(m["two"]) == 4]'
    pyflwor.execute(query, locals())
    --------- returns ---------
    OrderedSet(['hello'])

You can use boolean operators as well:

    a = 'hello'
    true = True
    false = False
    pyflwor.execute('a[true and (false or not false)]', locals())
    --------- returns ---------
    OrderedSet(['hello'])

#### Other Where Expression Options

The syntax presented covers the simplest parts of path expressions. The syntax
elements not covered are more complex operators for the where clause. These
elements include:

1. Quantified Expressions

        some x in <path_expr> satisfies (where_clause)
        every x in <path_expr> satisfies (where_clause)

    example:

        a = 'hello'
        l1 = [0,2,4,6,8,10]
        l2 = [1,2,3,4,5,6]
        def mod2(x):
            return x % 2

        pyflwor.execute('a[every x in <l1> satisfies (mod2(x) == 0)]', locals())
        --------- returns ---------
        OrderedSet(['hello'])


        pyflwor.execute('a[every x in <l2> satisfies (mod2(x) == 0)]', locals())
        --------- returns ---------
        OrderedSet()

        pyflwor.execute('a[some x in <l2> satisfies (mod2(x) == 0)]', locals())
        --------- returns ---------
        OrderedSet(['hello'])


2. Set Expressions

        x in <path_expr>
        x not in <path_expr>
        <path_expr1> subset <path_expr2>
        <path_expr1> superset <path_expr2>
        <path_expr1> proper subset <path_expr2>
        <path_expr1> proper superset <path_expr2>
        <path_expr1> is <path_expr2>
        <path_expr1> is not <path_expr2>

3. Passing Sub-Queries to Functions

    Sub-Queries (of either the path expression from or the flower form) can be
    passed to functions:

        def print_query(q):
            for x in q:
                print x
        a = 'hello'
        l1 = [0,2,4,6,8,10]

        pyflwor.execute('a[not print_query(<l1[self < 5]>)]', locals())
        --------- returns ---------
        0
        2
        4
        OrderedSet(['hello'])

### Set Operations on Path Expressions

It is possible to construct higher order set based queries using path
expressions. For instance it is possible to take the interesection, union,
difference, or a combination there of between the results of two path expression.

    l = [0,1,2,3,4,5,6,7,8,9]

    pyflwor.execute('l - l[self < 5]', locals())
    --------- returns ---------
    OrderedSet([5, 6, 7, 8, 9])


### FLWR Expressions

FLWR stands for: "For Let Where Return." These expression are similar to the
XQuery Language.

#### FLWR Expresion Syntax:

    for NAME in PATH [, NAME in PATH]*
    [let NAME = (<path_expr>|{flwr_expr}) [, NAME = (<path_expr>|{flwr_expr})]*]*
    [where WHERE_CLAUSE]*
    return ((VALUE [, VALUE]*)|(STRING:VALUE, [, STRING:VALUE]*))

### For Statement

The for statement takes a cartesian product of the results of the Path
expressions.

#### Cartesian Product Example:

    A = [1,2,3,4]
    B = [5,6,7,8]

    for a in <A>, b in <B>
    return a, b
    --------- returns ---------
    (
        (1, 5),
        (1, 6),
        (1, 7),
        (1, 8),
        (2, 5),
        (2, 6),
        (2, 7),
        (2, 8),
        (3, 5),
        (3, 6),
        (3, 7),
        (3, 8),
        (4, 5),
        (4, 6),
        (4, 7),
        (4, 8)
    )

### Return Statement

The return statment can use either positional outputs or named values. In
the previous example the return statement used positional. Here is the same
example using named return values:

#### Named Return Values

    A = [1,2,3,4]
    B = [5,6,7,8]

    for a in <A>, b in <B>
    return 'a':a, "b":b
    --------- returns ---------
    (
        {'a': 1, 'b': 5},
        {'a': 1, 'b': 6},
        {'a': 1, 'b': 7},
        {'a': 1, 'b': 8},
        {'a': 2, 'b': 5},
        {'a': 2, 'b': 6},
        {'a': 2, 'b': 7},
        {'a': 2, 'b': 8},
        {'a': 3, 'b': 5},
        {'a': 3, 'b': 6},
        {'a': 3, 'b': 7},
        {'a': 3, 'b': 8},
        {'a': 4, 'b': 5},
        {'a': 4, 'b': 6},
        {'a': 4, 'b': 7},
        {'a': 4, 'b': 8}
    )

The return statement is not limited to simple values. It can return anything
which could be used as a value in a Where Clause as described above.

#### Complex Return Values (Simple Example)

    class A(object):
        def __init__(self, a, b):
            self.a = a
            self.b = b
        def __repr__(self):
            return '<A %s, %s>' %(self.a, self.b)

    objs = [A(1, A), A(2, A)]

    for obj in <objs>
    return 'current':obj.a, 'new':obj.b(obj.a, 'created')
    --------- returns ---------
    {'current': 1, 'new': <A 1, created>}
    {'current': 2, 'new': <A 2, created>}


### Aggregates Queries Using the Let Expression

The let statement enables the user to write aggregation queries. For instance
if you have a database of books what is the average price of those books?


### Data Model for a Chain of Bookstores

    class Book(object):
        def __init__(self, title, language, price):
            self.title = title
            self.language = language
            self.price = price

    class Bookstore(object):
        def __init__(self, name):
            self.name = name
            self.books = list()
        def addbook(self, book):
            self.books.append(book)

    bookstore1 = Bookstore('Tim\'s Books')
    bookstore1.addbook(Book("Harry Potter", "eng", 29.99))
    bookstore1.addbook(Book("Learning XML", "eng", 39.95))
    bookstore1.addbook(Book("Introduction to Algorithms", "eng", 78.99))
    bookstore1.addbook(Book("Databases: The Complete Book", "eng", 64.99))

    bookstore2 = Bookstore('Andy\'s Books')
    bookstore2.addbook(Book("Twilight", "eng", 15.99))
    bookstore2.addbook(Book("Learning Django", "eng", 39.95))
    bookstore2.addbook(Book("Catcher in the Rye", "eng", 6.99))
    bookstore2.addbook(Book("Halcyon Digest", "eng", 64.99))

    stores = [bookstore1, bookstore2]

### Select Titles of the Books For Each Bookstore

    for bookstore in <stores>
    let book_names = <bookstore/books/title>
    return 'Bookstore':bookstore.name, 'Titles':book_names
    --------- returns ---------
    (
        {
            'Bookstore': "Tim's Books",
            'Titles':
                OrderedSet([
                    'Harry Potter',
                    'Learning XML',
                    'Introduction to Algorithms',
                    'Databases: The Complete Book'
                ])
        },
        {
            'Bookstore': "Andy's Books",
            'Titles':
                OrderedSet([
                    'Twilight',
                    'Learning Django',
                    'Catcher in the Rye',
                    'Halcyon Digest'
                ])
        }
    )


### Average Price of the Books in Each Bookstore

NB: You must pass an average function (avg) into the namespace for this query
    to function.

    def avg(s): return sum(s)/len(s)

    for bookstore in <stores>
    let prices = <bookstore/books/price>
    return 'Bookstore':bookstore.name, 'Avg Price':avg(prices)
    --------- returns ---------

    {'Bookstore': "Tim's Books", 'Avg Price': 53.480000000000004}
    {'Bookstore': "Andy's Books", 'Avg Price': 31.98}

As a final note: you can have multiple let statements in a single flwr expression.

    for bookstore in <stores>
    let book_names = <bookstore/books/title>
    let prices = <bookstore/books/price>
    return 'Bookstore':bookstore.name, 'Titles':book_names,
        'Avg Price':avg(prices)
    --------- returns ---------
    (
        {
            'Bookstore': "Tim's Books",
            'Avg Price': 53.480000000000004,
            'Titles':
                OrderedSet([
                    'Harry Potter',
                    'Learning XML',
                    'Introduction to Algorithms',
                    'Databases: The Complete Book'
                ])
        },
        {
            'Bookstore': "Andy's Books",
            'Avg Price': 31.98,
            'Titles':
                OrderedSet([
                    'Twilight',
                    'Learning Django',
                    'Catcher in the Rye',
                    'Halcyon Digest'
                ])
        }
    )

### Where Statements

Where statement internally share the same syntax as where clauses share in path
expressions.

### Where Statement

    for bookstore in <stores>
    let book_names = <bookstore/books/title>
    let prices = <bookstore/books/price>
    where avg(prices) < 45
    return 'Bookstore':bookstore.name, 'Titles':book_names,
        'Avg Price':avg(prices)
    --------- returns ---------
    (
        {
            'Bookstore': "Andy's Books",
            'Avg Price': 31.98,
            'Titles':
                OrderedSet([
                    'Twilight',
                    'Learning Django',
                    'Catcher in the Rye',
                    'Halcyon Digest'
                ])
        },
    )


Formal Language Specification
-----------------------------

For Reference Some Named Regular Expresssions:

    D = r'[0-9]'
    L = r'[a-zA-Z_]'
    H = r'[a-fA-F0-9]'
    E = r'[Ee][+-]?(' + D + ')+'

#### Tokens

    'NAME' -> (L)((L)|(D))*
    'NUMBER' -> -?(D)+
              | -?0[xX](H)+
              | -?(D)+(E)
              | -?(D)*\.(D)+(E)?
    'STRING' -> "[^"]*"
              | '[^']*'
    'SLASH' -> /
    'EQEQ' -> ==
    'EQ' -> =
    'NQ' -> !=
    'LE' -> <=
    'GE' -> >=
    'COMMA' -> ,
    'DOT' -> .
    'COLON' -> :
    'LPAREN' -> (
    'RPAREN' -> )
    'LSQUARE' -> [
    'RSQUARE' -> ]
    'LANGLE' -> <
    'RANGLE' -> >
    'LCURLY' -> {
    'RCURLY' -> }
    'UNION' -> |
    'INTERSECTION' -> &
    'DIFFERENCE' -> -

#### Reserved Words

    some, every, in, not satisfies, and, or is, subset, superset, proper,
    for, let, return, where

#### Full Grammar


    Start : Set
    Start : FLWRexpr

    AndExpr : AndExpr AND NotExpr
    AndExpr : NotExpr
    Attr : NAME
    Attr : NAME Call
    AttributeValue : AttributeValue DOT Attr
    AttributeValue : Attr
    BooleanExpr : CmpExpr
    BooleanExpr : QuantifiedExpr
    BooleanExpr : SetExpr
    BooleanExpr : Value
    BooleanExpr : LPAREN Where RPAREN
    Call : Call Call_
    Call : Call_
    Call_ : Fcall
    Call_ : Dcall
    CmpExpr : Value CmpOp Value
    CmpOp : EQEQ
          | NQ
          | LANGLE
          | LE
          | RANGLE
          | GE
    Collection : Query
    Collection : LPAREN Set RPAREN
    Dcall : LSQUARE Value RSQUARE
    Entity : NAME
    Entity : NAME LSQUARE Where RSQUARE
    FLWRexpr : ForExpr ReturnExpr
    FLWRexpr : ForExpr LetExpr ReturnExpr
    FLWRexpr : ForExpr WhereExpr ReturnExpr
    FLWRexpr : ForExpr LetExpr WhereExpr ReturnExpr
    Fcall : LPAREN RPAREN
    Fcall : LPAREN ParameterList RPAREN
    ForDefinition : NAME IN LANGLE Set RANGLE
    ForDefinition : NAME IN LCURLY FLWRexpr RCURLY
    ForExpr : FOR ForList
    ForList : ForList COMMA ForDefinition
    ForList : ForDefinition
    IntersectionExpr : IntersectionExpr INTERSECTION Collection
    IntersectionExpr : Collection
    LetDefinition : NAME EQ LANGLE Set RANGLE
    LetDefinition : NAME EQ LCURLY FLWRexpr RCURLY
    LetExpr : LetExpr LET LetList
    LetExpr : LET LetList
    LetList : LetList COMMA LetDefinition
    LetList : LetDefinition
    NotExpr : NOT BooleanExpr
    NotExpr : BooleanExpr
    OrExpr : OrExpr OR AndExpr
    OrExpr : AndExpr
    OutputDict : OutputDict COMMA STRING COLON OutputValue
    OutputDict : STRING COLON OutputValue
    OutputTuple : OutputTuple COMMA OutputValue
    OutputTuple : OutputValue
    OutputValue : Value
    OutputValue : LANGLE Set RANGLE
    OutputValue : LCURLY FLWRexpr RCURLY
    Parameter : Value
    Parameter : LANGLE Set RANGLE
    Parameter : LCURLY FLWRexpr RCURLY
    ParameterList : ParameterList COMMA Parameter
    ParameterList : Parameter
    QuantifiedExpr : Quantifier NAME IN LANGLE Set RANGLE SATISFIES LPAREN Where RPAREN
    QuantifiedExpr : Quantifier NAME IN LCURLY FLWRexpr RCURLY SATISFIES LPAREN Where RPAREN
    Quantifier : EVERY
    Quantifier : SOME
    Query_ : Query_ SLASH Entity
    Query_ : Entity
    Query : Query_
    ReturnExpr : RETURN OutputTuple
    ReturnExpr : RETURN OutputDict
    Set : Set DIFFERENCE UnionExpr
    Set : UnionExpr
    SetExpr : Value IN LANGLE Set RANGLE
    SetExpr : Value NOT IN LANGLE Set RANGLE
    SetExpr : LANGLE Set RANGLE SUBSET LANGLE Set RANGLE
    SetExpr : LANGLE Set RANGLE SUPERSET LANGLE Set RANGLE
    SetExpr : LANGLE Set RANGLE PROPER SUBSET LANGLE Set RANGLE
    SetExpr : LANGLE Set RANGLE PROPER SUPERSET LANGLE Set RANGLE
    SetExpr : LANGLE Set RANGLE IS LANGLE Set RANGLE
    SetExpr : LANGLE Set RANGLE IS NOT LANGLE Set RANGLE
    UnionExpr : UnionExpr UNION IntersectionExpr
    UnionExpr : IntersectionExpr
    Value : NUMBER
    Value : STRING
    Value : AttributeValue
    Where : OrExpr
    WhereExpr : WHERE Where

Changelog
---------

### Path Expressions

### v1.2

    * added a new query syntax to query in and not in static list

      hello['foo' in ['foo','bar']] 
      hello['foo' not in ['foo','bar']]

### v1.1

    * python3 compatibility
