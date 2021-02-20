"""
    Hadar Shahar

"""
import functools


def catch_exception(func):
    """
       decorator that executes a function, catches any exception that is raised
       inside the function and prints it.
       :return: the value that the given function returns,
                or None if an exception is raised.
       """

    @functools.wraps(func)  # preserves information about the original function
    def wrapper_catch_exception(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # func.__name__ = the function name
            # func.__qualname__ = a dotted path leading to
            #                     the function from the module top-level
            # !r = calls the __repr__ function
            print(f'Exception at {func.__qualname__!r}: {e}')

    return wrapper_catch_exception


from flask import request
from functools import wraps


def assert_params_exist(*params):
    def wrapper(f):
        @wraps(f)
        def wrapped(self, *f_args):
            missing = [p for p in params if p not in request.get_json()]
            if missing:
                return 'Missing required params: ' + ', '.join(missing)
            return f(self, params)
        return wrapped
    return wrapper

# with callback (isn't working for self.method)
# def catch_exception(callback=None):
#     """
#     decorator that executes a function, catches any exception that is raised
#     inside the function and prints it.
#     :param callback: (optional) function to execute when an exception is raised
#     :return: the value that the given function returns,
#              or None if an exception is raised.
#     """
#     def decorator_catch_exception(func):
#         @functools.wraps(func)  # preserves information about the original function
#         def wrapper_catch_exception(*args, **kwargs):
#             try:
#                 return func(*args, **kwargs)
#             except Exception as e:
#                 # func.__name__ = the function name
#                 # func.__qualname__ = a dotted path leading to
#                 #                     the function from the module top-level
#                 # !r = calls the __repr__ function
#                 print(f'Exception at {func.__qualname__!r}: {e}')
#                 if callback:
#                     callback()
#
#         return wrapper_catch_exception
#     return decorator_catch_exception
#
#
# def callback_func():
#     print('exception!')


class Test(object):
    @catch_exception
    def __init__(self):
        self.n = 0 / 0


if __name__ == '__main__':
    t = Test()
