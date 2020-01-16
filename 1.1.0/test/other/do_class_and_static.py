
# coding:utf-8


class Book(object):

    def __init__(self, title):
        self.title = title

    @classmethod
    def create(cls, title):
        book = cls(title=title)
        return book

    def foo(self):
        print(f'foo,{str(self.title)}')

    @classmethod
    def test1(cls,a):
        b = cls(title=a)
        return b.foo()


class FooOne(object):
    X = 4
    Y = 10

    @staticmethod
    def averag(*mixes):
        # print(sum(mixes) / len(mixes))
        return sum(mixes) / len(mixes)

    @staticmethod
    def static_method():
        return Foo.averag(Foo.X, Foo.Y)

    @classmethod
    def class_method(cls):
        return cls.averag(cls.X, cls.Y)
"""
从下面代码可以看出，如果子类继承父类的方法，子类覆盖了父类的静态方法，
子类的实例继承了父类的static_method静态方法，调用该方法，还是调用的父类的方法和类属性。
子类的实例继承了父类的class_method类方法，调用该方法，调用的是子类的方法和子类的类属性。
"""

class Foo(object):
    X = 1
    Y = 2

    @staticmethod
    def averag(*mixes):
        return sum(mixes) / len(mixes)

    @staticmethod
    def static_method():
        return Foo.averag(Foo.X, Foo.Y)

    @classmethod
    def class_method(cls):
        return cls.averag(cls.X, cls.Y)


class Son(Foo):
    X = 3
    Y = 5

    @staticmethod
    def averag(*mixes):
        return sum(mixes) / 3


class Goods1:

    def __init__(self,name,price):
        self.name = name
        self.__price = price
        self.__discount = 1  # 折扣

    @property
    def price(self):
        return self.__price*self.__discount

    # 改变折扣价
    def change_discount(self,new_discount):
        self.__discount = new_discount

class Goods2:
    discount = 1

    def __init__(self,name,price):
        self.name = name
        self.price = price

    @property
    def price_out(self):
        return self.price*self.discount

    # 改变折扣价
    @classmethod
    def change_discount(cls,new_discount):
        cls.discount = new_discount
        return cls


if __name__ == '__main__':
    # Book.test1('skdfskhdfddddddd')

    # foo = Foo()
    # print(foo.static_method())
    # print(foo.class_method())

    # p = Son()
    # print(p.static_method())
    # print(p.class_method())

    # 苹果8折
    # apple = Goods1('苹果',10)
    # apple.change_discount(0.8)
    # print(apple.price)
    # # 香蕉7折
    # banana = Goods1('香蕉',20)
    # banana.change_discount(0.7)
    # print(banana.price)

    good = Goods2.change_discount(0.8)
    apple = good('苹果',10)
    print(apple.price_out)

    # banana = Goods2('香蕉', 20)
    # print(banana.price)
