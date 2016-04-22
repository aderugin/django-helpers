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
            raise HttpResponseBadRequest

        result = view_func(request, *args, **kwargs)
        if not isinstance(result, dict):
            raise TypeError("Decorated function mast return dict instance")
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


"""
TODO
- Декоратор, куширующий результат выполнения метода у екземпляра класса
"""
