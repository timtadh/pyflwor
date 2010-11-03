
PyQuery - The Python Object Query System
========================================

By Tim Henderson - tim.tadh@hackthology.com

Table of Contents
-----------------

1. Introduction
2. Motivation
3. Usage Example
4. Writing PyQuery
5. Formal Language Specification

Introducton
-----------

PyQuery is an query language for querying python object collections. While
Python has many interesting ways to persisting objects, it does not have (to my
knowledge) a query language. This language was inspired in part by OQL (Object
Query Language), XPath2.0, and XQuery. It is still under rapid development so
expect the language to change often. PyQuery works on any type of Python object.
The only requirement being that the objects returned have to be hashable
(as they are currently returned as set).


Motivation
----------

The motivation for this work occured while working on a software system with a
unified namespace to address hetergenous data models. Some of the models were
relational, some were XML, and increasingly some were simply native python
objects. To unify this namespace I am working on this language. However, I
expect that since PyQuery works on any Python object collection it may be
generally useful to the Python community.

Usage Example
-------------

    import pyquery

    class Obj(object):
        def __init__(self, attr, attr2):
            self.attr = attr
            self.attr2 = attr2

    q = pyquery.compile('''
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


Writing PyQuery
---------------

Like XPath and XQuery there are two ways to write queries in PyQuery: "path"
expressions and "flwr" expressions. Path expressions have a similar syntax to
XPath.

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


#### PyQuery Queries:

1. all books

        bookstore/books

2. all books with price greater than $30.00

        bookstore/books[self.price > 30.00]

The where condition in Path expression allows you access any object in the
namespace you passed into the query. It also names the current object under
consideration (in the working example the Book) 'self.' You can access any
attribute of self, you can even call functions and access items in lists and
dicts.

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
    pyquery.execute(query, locals())
    --------- returns ---------
    OrderedSet(['hello'])

You can use boolean operators as well:

    a = 'hello'
    true = True
    false = False
    pyquery.execute('a[true and (false or not false)]', locals())
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

        pyquery.execute('a[every x in <l1> satisfies (mod2(x) == 0)]', locals())
        --------- returns ---------
        OrderedSet(['hello'])


        pyquery.execute('a[every x in <l2> satisfies (mod2(x) == 0)]', locals())
        --------- returns ---------
        OrderedSet()

        pyquery.execute('a[some x in <l2> satisfies (mod2(x) == 0)]', locals())
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

        pyquery.execute('a[not print_query(<l1[self < 5]>)]', locals())
        --------- returns ---------
        0
        2
        4
        OrderedSet(['hello'])

### FLWR Expressions

FLWR stands for: "For Let Where Return." These expression are similar to the
XQuery Language. The basic syntax looks like this:

    for NAME in PATH
    [let NAME = (<path_expr>|{flwr_expr})]*
    [where WHERE_CLAUSE]*
    return VALUE, ...
