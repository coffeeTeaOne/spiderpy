import random
from retrying import retry


@retry(stop_max_attempt_number=5)
def do_something_unreliable():
    num = random.randint(0, 10)
    if num > 1:
        print('false',num)
        raise IOError("Broken sauce, everything is hosed!!!111one")
    else:
        print('ture',num)
        return "Awesome sauce!"

print(do_something_unreliable())