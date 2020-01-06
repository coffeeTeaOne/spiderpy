import datetime,time

def string2timestamp(strValue):
    try:
        d = datetime.datetime.strptime(strValue, "%Y-%m-%d %H:%M:%S.%f")
        t = d.timetuple()
        timeStamp = int(time.mktime(t))
        timeStamp = float(str(timeStamp) + str("%06d" % d.microsecond)) / 1000000
        print(timeStamp)
    except ValueError as e:
        pass

to = datetime.datetime(2019, 11, 12, 4, 8, 42, 105000)
print(to)
string2timestamp(str(to))