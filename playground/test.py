# class Example(object):
#     itsProblem = "problem"
#
#
# theExample = Example()
# print(theExample.itsProblem)
# print(Example.itsProblem)
#
# print(theExample.itsProblem is Example.itsProblem)
# theExample.itsProblem = 'a'
# print(theExample.itsProblem is Example.itsProblem)
#
# print(theExample.itsProblem)
# print(Example.itsProblem)


from PyQt5.QtCore import QObject, pyqtSignal


class A(QObject):
    num = 0
    signal = pyqtSignal()

    def __init__(self):
        super(A, self).__init__()
        print(self.num is A.num)
        print(self.signal is A.signal)


a = A()
print()


class First(object):
    def __init__(self):
        print("first")


class Second(object):
    def __init__(self):
        print("second")


class Third(First, Second):
    def __init__(self):
        super(Third, self).__init__()
        print("that's it")


Third()
