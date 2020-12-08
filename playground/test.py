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


class A:
    def __init__(self):
        print('A')
        super().__init__()


class B(A):
    def __init__(self):
        print('B')
        super().__init__()


class C(B):
    def __init__(self):
        print('C')
        super().__init__()


C()
