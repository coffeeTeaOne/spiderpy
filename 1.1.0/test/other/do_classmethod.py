from time import time, localtime, sleep
"""
无需实例化，可以通过类直接调用的方法，但是方法的第一个参数接收的一定是类本身
(1).在方法上面添加@classmethod
(2).方法的参数为 cls 也可以是其他名称，但是一般默认为cls
(3).cls 指向 类对象(也就是Goods)
(4).应用场景：当一个方法中只涉及到静态属性的时候可以使用类方法(类方法用来修改类属性)。
(5).使用 可以是 对象名.类方法名。或者是 类名.类方法名
"""



class Clock(object):
    """数字时钟"""

    def __init__(self, hour=0, minute=0, second=0):
        self._hour = hour
        self._minute = minute
        self._second = second

    @classmethod
    def now(cls):
        ctime = localtime(time())
        return cls(ctime.tm_hour, ctime.tm_min, ctime.tm_sec)

    def run(self):
        """走字"""
        self._second += 1
        if self._second == 60:
            self._second = 0
            self._minute += 1
            if self._minute == 60:
                self._minute = 0
                self._hour += 1
                if self._hour == 24:
                    self._hour = 0

    def show(self):
        """显示时间"""
        return '%02d:%02d:%02d' % \
               (self._hour, self._minute, self._second)


def main():
    # 通过类方法创建对象并获取系统时间
    clock = Clock.now()
    while True:
        print(clock.show())
        sleep(1)
        clock.run()


if __name__ == '__main__':
    main()