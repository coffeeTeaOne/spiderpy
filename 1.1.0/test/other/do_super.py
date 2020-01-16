
# 单继承
class Father(object):
    def __init__(self,a=2,b=3):
        self.a = a
        self.b = b

    def run(self):
        print(self.a * self.b)


class Son(Father):
    def __init__(self,c):
        super(Son,self).__init__()
        self.c = c
        print(self.a)
        print(self.b)

    def run(self):
        # 使用super表示在父类的该方法下继续加功能，不要super相当于重写父类这个方法
        # super(Son,self).run()
        print(self.c * self.a * self.b )


# 多继承
class Father(object):
    def __init__(self,money):
        self.money = money

    def play(self):
        print("play")

    def func(self):
        print("func")


class Mother(object):
    def __init__(self, faceValue):
        self.faceValue = faceValue

    def eat(self):
        print("eat")

    def func(self):
        print("func2")


class Child(Father,Mother):
    def __init__(self,money,faceValue):
        Father.__init__(self,money) # 继承父类的init属性
        Mother.__init__(self,faceValue) #继承母类的init属性
        # 此时的self指的是当前类的self


# 我们写一个主程序
def main():
    c = Child(300,100)
    print(c.money,c.faceValue)
    c.play()
    c.eat()
    # 注意如果方法名相同，默认调用的是在括号中排前面的父类中的方法
    c.func()

if __name__ == '__main__':
    main()

