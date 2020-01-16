class Person(object):
    name = ""
    sex = ""

    def __init__(self, name, sex='U'):
        print('Person')
        self.name = name
        self.sex = sex


class Consumer(object):
    def __init__(self,a):
        self.a = a
        print('Consumer')


class Student(Person, Consumer):
    def __init__(self, score, name,a):
        print(Student.__bases__)
        # super(Student, self).__init__(name, sex='F')
        Person.__init__(self,name,sex='aaaa')
        Consumer.__init__(self,a)
        print(self.a)
        self.score = score


s1 = Student(90, 'abc',1000)
print(s1.name, s1.score, s1.sex)