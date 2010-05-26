

class Query(object):

    def __init__(self, select):
        self.select = select

def query(obj, q):
    attrs = q.select.split('.')
    print attrs
    def select(obj, attrs, i=1):
        def flatten(l):
            r = list()
            for o in l:
                if hasattr(o, '__iter__'):
                    for x in o: yield x
                else:
                    yield o
        def get(cobj, attr):
            print cobj, attr
            if hasattr(cobj, attr):
                return getattr(cobj, attr)
            else:
                raise Exception, "could not select %s from obj %s. failed at %s, %s" % \
                                    (q.select, str(obj), attr, cobj)
        cobj = obj
        for j, attr in enumerate(attrs[i:]):
            if hasattr(cobj, '__iter__'):
                def gen(cobj, attr):
                    for o in cobj: yield get(o, attr)
                cobj = flatten(gen(cobj, attr))
            else:
                cobj = get(cobj, attr)
        return cobj
    return select(obj, attrs)

if __name__ == '__main__':
    import example
    a = example.A(1)
    print list(query(a, Query('a.b.c.n')))
