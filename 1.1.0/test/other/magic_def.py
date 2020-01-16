
class One:
    c = 100

    # 类开始的方法
    def __new__(cls,a,b):
        # cls.c = a + b
        # print(cls.c)
        return object.__new__(cls)

    def __init__(self,a,b):
        self.a = a
        self.b = b
        # print(self.a,self.b,self.c)

    @property
    def run(self):
        print(self.a * self.b)
        return self.a * self.b

    def __call__(self):
        print(self.c + self.b)
        return self.c + self.b

    @staticmethod
    def staticm(a,b):
        one = One(a,b)
        print(one.a + one.b + one.c)
        return one.a + one.b + one.c

    @classmethod
    def classm(cls,a,b):
        cls.d = a + b
        return cls

    # 类结束的方法
    def __del__(self):

        print('释放实例！')

if __name__ == '__main__':
    one = One(2,3)
    print(one.run)
    # print(one.a,one.b,one.c)

    # __call__调用
    # one()
    # one.__call__()


    # two = One.staticm(20,30)
    # print(two)


