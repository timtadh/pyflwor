

#for x in [X1...Xn]
#where x[a == 1 and b == 2]/y/z[c == 4]
#return x/y


class up(object):
    def __repr__(self): return str(self)
    def __str__(self):
        return self.__class__.__name__ + str(self.n)

class A(up):
    def __init__(self, n):
        self.n = n
        self.b = list()
        self.b.append(B(1))
        self.b.append(B(2))
        self.b.append(B(3))
        self.b.append(B(4))

class B(up):
    def __init__(self, n):
        self.n = n
        self.c = list()
        self.c.append(C(1))
        self.c.append(C(2))
        self.c.append(C(3))
        self.c.append(C(4))

class C(up):
    def __init__(self, n):
        self.n = n

a = A(1)
print a
print a.b
print [b.c for b in a.b]

