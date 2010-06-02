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
			Customer('Harry', 'Columbus', 0.0), Customer('Steve', 'Cincinnati', 0.2)]

agents = [Agent('Aho', 'Stanford', .25), Agent('Lam', 'Baltimore', .15),
			Agent('Sethi', 'Cleveland', .15), Agent('Ullman', 'New York', .35)]

products = [Product('Coca-Cola', 'Atlanta', 1000000, 1.0), Product('Koss Porta-Pro', 'Columbus', 500, 44.99),
			Product('Altec Speakers', 'Cleveland', 10000, 59.99), Product('Pilot G-2', 'New York', 1000, .50)]

orders = list(Order(customers[t[0]], agents[t[1]], products[t[2]], randint(0,100)) for t in itertools.product(range(4), repeat=3))

orders += list(Order(customers[t[0]], agents[t[1]], products[t[2]], randint(0,100)) for t in itertools.permutations(range(4), 3))

orders += list(Order(customers[t[0]], agents[t[1]], products[t[2]], randint(0,100)) for t in itertools.product(range(4), repeat=3))

if __name__ == '__main__':
	from parser import Parser
	from lexer import Lexer
	print "Orders where customer.name = Steve and agent.name = Ullman"
	q = Parser().parse('o[self.customer.name == "Steve" and self.agent.name == "Ullman"]', lexer=Lexer())
	for x in q(orders, dict()):
		print x

