from math import sqrt


"""
(1).格式：在方法上面添加 @staticmethod
(2).参数：静态方法可以有参数也可以无参数
(3).应用场景：一般用于和类对象以及实例对象无关的代码。
(4).使用方式：  类名.类方法名(或者对象名.类方法名)。
"""
class Triangle(object):

    def __init__(self, a, b, c):
        self._a = a
        self._b = b
        self._c = c

    @staticmethod
    def is_valid(a, b, c):
        return a + b > c and b + c > a and a + c > b

    def perimeter(self):
        return self._a + self._b + self._c

    def area(self):
        half = self.perimeter() / 2
        return sqrt(half * (half - self._a) *
                    (half - self._b) * (half - self._c))

    @classmethod
    def run(cls):
        a,b,c = 3, 4, 5
        if Triangle.is_valid(a,b,c):
            print(cls(a,b,c).perimeter())
            print(cls(a,b,c).area())
        else:
            print('无法构成三角形222.')



def main():
    a, b, c = 3, 4, 5
    # 静态方法和类方法都是通过给类发消息来调用的
    if Triangle.is_valid(a, b, c):
        t = Triangle(a, b, c)
        print(t.perimeter())
        # 也可以通过给类发消息来调用对象方法但是要传入接收消息的对象作为参数
        # print(Triangle.perimeter(t))
        print(t.area())
        # print(Triangle.area(t))
    else:
        print('无法构成三角形.')


if __name__ == '__main__':
    Triangle.run()
    # main()