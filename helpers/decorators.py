# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from .views import view_or_basicauth
from .utils import int_convertible


def ajax_view(view_func):
    """
    Если view для ajax, то выводит 400 если обращение не xjr
    """
    def wrapper(request, *args, **kwargs):
        if not request.is_ajax() and not settings.DEBUG:
            return HttpResponseBadRequest()

        result = view_func(request, *args, **kwargs)
        if not isinstance(result, dict):
            raise TypeError('Decorated function must return dict instance')
        return JsonResponse(result)
    return wrapper


def basicauth(view_func):
    """
    Декоратор для view требующей http авторизации
    """
    def wrapper(request, *args, **kwargs):
        return view_or_basicauth(view_func, request, *args, **kwargs)
    return wrapper


def args_to_int(func):
    """
    Декоратор, преобразующий аргументы функции в целые числа
        Например '2' -> 2
    """
    def wrapper(*args):
        return func(*[int(arg) if int_convertible(arg) else arg for arg in args])
    return wrapper


class cached_property(object):
    """
    Декоратор property класса, кеширующий результат
    его выполнения

    class SomeClass:
       @cached_property
       def some_prop(self):
           print('cached')
           return 42

    >>> t = SomeClass()
    >>> t.some_prop
    cached
    42
    >>> t.some_prop
    42
    """
    def __init__(self, method):
        self._method = method

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = self._method(instance)
        setattr(instance, self._method.__name__, value)
        return value
