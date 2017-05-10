'''
pyflwor - The Python Object Query System
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: examples.py
Purpose: Example queries for pyflwor.
'''
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import object

import itertools
from random import seed, randint
seed('Example CAP Database')

#Consider the Customers-Agents-Products (CAP) database with schema below.
#CUSTOMERS (cid, cname, city, discnt)
#AGENTS (aid, aname, city, percent)
#PRODUCTS (pid, pname, city, quantity, price)
#ORDERS (ordno, month, cid, aid, pid, qty, dollars)

class Customer(object):
    def __init__(self, name, city, discnt):
        self.name = name
        self.city = city
        self.discnt = discnt
    def __repr__(self): return str(self)
    def __str__(self): return str((self.name, self.city, self.discnt))

class Agent(object):
    def __init__(self, name, city, commision):
        self.name = name
        self.city = city
        self.commision = commision
    def __repr__(self): return str(self)
    def __str__(self): return str((self.name, self.city, self.commision))

class Product(object):
    def __init__(self, name, city, quantity, price):
        self.name = name
        self.city = city
        self.quantity = quantity
        self.price = price
    def __repr__(self): return str(self)
    def __str__(self): return str((self.name, self.city, self.quantity, self.price))

class Order(object):
    def __init__(self, customer, agent, product, quantity):
        self.customer = customer
        self.agent = agent
        self.product = product
        self.quantity = quantity
    def __repr__(self): return str(self)
    def __str__(self): return str((self.customer, self.agent, self.product, self.quantity))

customers = [Customer('Joe', 'Cleveland', 0.1), Customer('Charlie', 'DC', 0.05),
            Customer('Harry', 'Columbus', 0.0), Customer('Steve', 'Cincinnati', 0.2),
            Customer('Tealc', 'Cleveland', 0.1), Customer('Jack', 'Cleveland', 0.1)]

agents = [Agent('Aho', 'Stanford', .25), Agent('Lam', 'Baltimore', .15),
            Agent('Sethi', 'Cleveland', .15), Agent('Ullman', 'New York', .35)]

products = [Product('Coca-Cola', 'Atlanta', 1000000, 1.0), Product('Koss Porta-Pro', 'Columbus', 500, 44.99),
            Product('Altec Speakers', 'Cleveland', 10000, 59.99), Product('Pilot G-2', 'New York', 1000, .50)]

#orders = list(Order(customers[t[0]], agents[t[1]], products[t[2]], randint(0,100)) for t in itertools.product(range(4), repeat=3))

#orders += list(Order(customers[t[0]], agents[t[1]], products[t[2]], randint(0,100)) for t in itertools.permutations(range(4), 3))

#orders += list(Order(customers[t[0]], agents[t[1]], products[t[2]], randint(0,100)) for t in itertools.product(range(4), repeat=3))

orders = [
        Order(customers[0], agents[0], products[0], randint(0,100)),
        Order(customers[0], agents[1], products[0], randint(0,100)),
        Order(customers[0], agents[2], products[0], randint(0,100)),
        Order(customers[1], agents[3], products[1], randint(0,100)),
        Order(customers[2], agents[0], products[3], randint(0,100)),
        Order(customers[3], agents[1], products[2], randint(0,100)),
        Order(customers[3], agents[2], products[1], randint(0,100)),
        Order(customers[1], agents[3], products[2], randint(0,100)),
        Order(customers[3], agents[3], products[2], randint(0,100)),
        Order(customers[0], agents[3], products[2], randint(0,100)),
        Order(customers[4], agents[3], products[2], randint(0,100)),
        Order(customers[5], agents[3], products[2], randint(0,100)),
        Order(customers[4], agents[1], products[1], randint(0,100)),
        Order(customers[2], agents[1], products[1], randint(0,100)),
    ]

if __name__ == '__main__':
    from . import pyflwor
    print("all orders")
    for x in orders:
        print(x)
    print()
    print()
    print()


    print("Orders where customer.name = Steve and agent.name = Ullman")
    q = pyflwor.compile('orders[self.customer.name == "Steve" and self.agent.name == "Ullman"]')
    for x in q(locals()):
        print(x)
    print()
    print()
    print()

    print("1. Get names of products that are ordered by at least one customer three different times.")
    q = pyflwor.compile('''
            products
            [
                some o1 in <orders> satisfies
                (
                    some o2 in <orders> satisfies
                    (
                        some o3 in <orders> satisfies
                        (
                            self == o1.product and self == o2.product and self == o3.product and
                            o1 != o2 and o2 != o3 and o3 != o1 and
                            o1.customer == o2.customer and o2.customer == o3.customer and
                            o3.customer == o1.customer
                        )
                    )
                )
            ]
            /name
        ''')
    t = q(locals())
    for x in t:
        print(x)
    print()
    print()
    print()

    print("2. Get product names that are ordered by at least three customers in the same city.")
    q = pyflwor.compile('''
            products
            [
                some o1 in <orders> satisfies
                (
                    some o2 in <orders[self != o1]> satisfies
                    (
                        some o3 in <orders[self != o1 and self != o2]> satisfies
                        (
                            self == o1.product and self == o2.product and self == o3.product and
                            o1.customer != o2.customer and o2.customer != o3.customer and
                            o3.customer != o1.customer and
                            o1.customer.city == o2.customer.city and
                            o2.customer.city == o3.customer.city and
                            o3.customer.city == o1.customer.city
                        )
                    )
                )
            ]
            /name
        ''')
    for x in q(locals()):
        print(x)
    print()
    print()
    print()

    print('''3. Get product names that are ordered by at least one customer in each and every customer city listed in the database (universal quantification).''')
    q = pyflwor.compile('''
            products
            [
                every c1 in <customers> satisfies
                (
                    some c2 in <customers> satisfies
                    (
                        some o in <orders> satisfies
                        (
                            c1.city == c2.city and c2 == o.customer and self == o.product
                        )
                    )
                )
            ]
            /name
        ''')
    for x in q(locals()):
        print(x)
    print()
    print()
    print()

