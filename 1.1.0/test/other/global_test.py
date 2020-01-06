# x = 1
#
# def func():
#     # global x
#     x = 2
#     print(x)
#
# func()
# print(x)

class A:
    def __init__(self):
        self.n = 2

    def add(self, m):
        print('self is {0} @A.add'.format(self))
        self.n += m
        print(self.n)

class B(A):
    def __init__(self):
        # super(B,self).__init__()
        self.n = 3

    def add(self, m):
        print('self is {0} @B.add'.format(self))
        super().add(m)
        self.n += 3
        print(self.n)

b = B()
b.add(2)
print(b.n)
