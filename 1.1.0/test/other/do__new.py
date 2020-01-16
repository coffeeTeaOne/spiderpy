
"""
通过上面的结果我们可以知道,__new__方法执行在__init__方法之前
1)__new__方法必须有参数cls,cls指的是当前正在实例化的类
2)__new__必须有返回值,返回的是实例,如果是使用当前类构造的实例,可以用object.__new__(cls),也可以用父类名.__new__(cls)
3)__init__方法的参数self其实就是__new__方法返回的实例对象,在这个__init__方法中还可以对这个实例进行其他的操作,比如添加一些属性等
"""
class User(object):
    def __init__(self,a,b,c,*args,**kwargs):
        self.a = a
        self.b = b
        self.c = c
        # print("__init__方法被调用")

    # @staticmethod
    def __new__(cls, a,b,c,*args, **kwargs):
        cls.reslut = super(User,cls).__new__(cls)
        # 添加属性
        cls.i = a + 3
        cls.j = b * 5
        cls.k = c * 6
        # print("__new__方法被调用")
        # 修改属性
        cls.a = a + 3
        cls.b = b * 5
        cls.c = c * 6

        # return cls
        return cls.reslut
        # return object.__new__(cls)


if __name__ == '__main__':
    u1 = User(1,2,3)
    print(u1.a,u1.b,u1.c)
    print(u1.i,u1.j,u1.k)