# -*- coding: utf-8 -*-
from django import template
from .tools import int_convertible, plural_number as _plural_number

register = template.Library()


@register.filter
def plural_number(string, num):
    """
    Склоняет относительно числа
    товар__товара__товаров
    {{ "товар__товара__товаров"|plural_number:number }}
    """
    return _plural_number(num, string)


@register.filter
def GET_without_params(request, params):
    """
    Возвращает строку GET без определенных параметров
    {{ request|GET_without_params:"param1,param2" }}
    """
    get_dict = request.GET.copy()
    for param in params.split(','):
        try:
            get_dict.pop(param)
        except KeyError:
            pass
    return '?%s' % get_dict.urlencode()


@register.filter
def wrap_1000(value, tag='span'):
    """
    Обертывание в <tag>
    <tag>12</tag>345
    """
    if int_convertible(value) and len(value) > 3:
        first_part = value[:-3]
        last_part = value[-3:]
        return '<%(tag)s>%(first_part)s</%(tag)s>%(last_part)s' % {
            'tag': tag,
            'first_part': first_part,
            'last_part': last_part
        }
    else:
        return value


@register.filter
def get_querylist(querydict, key):
    """
    Работает с объектом QueryDict, выполняет метод getlist
    """
    return querydict.getlist(key)
