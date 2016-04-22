# -*- coding: utf-8 -*-
import random
import string
import re
import os
from hashlib import md5
from time import time

from django.shortcuts import _get_queryset


def float_convertible(string):
    """
    Проверяет можно ли преобразовать строку во float
    """
    try:
        float(string)
        return True
    except Exception:
        return False


def int_convertible(string):
    """
    Проверяет можно ли преобразовать строку в целое число
    LOL: '100500'.isdigit() оО проверяет содержит ли строка только числа
    """
    try:
        int(string)
        return True
    except Exception:
        return False


def password_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """
    Генератор пароля
    """
    return ''.join(random.choice(chars) for _ in range(size))


def get_object_or_none(model, *args, **kwargs):
    """
    Возвращает instance модели или None
    """
    queryset = _get_queryset(model)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


def replace_text(text, variables):
    """
    Replace some special words in text to variable from dictionary
    @param text: raw text
    @param variables: dictionary of variables for replace
    """
    for name, value in variables.items():
        text = text.replace('#%s#' % name, str(value))
    return text


def normalize_phone(phone):
    """
    Нормализует телефонный номер
    """
    phone = re.sub(r'[\W]', '', phone)
    if len(phone) == 10 and phone.startswith('9'):
        phone = '7' + phone
    if len(phone) == 11 and phone.startswith('8'):
        phone = '7' + phone[1:]
    return phone


def plural_number(num, string):
    """
    Склоняет относительно числа
    товар__товара__товаров
    """
    plurals = string.split('__')
    if len(plurals) < 3:
        raise Exception('It must have three variants')
    if not isinstance(num, int):
        raise Exception('It must be integer')
    if num % 10 == 1:
        return plurals[0]
    if num in [2, 3, 4]:
        return plurals[1]
    return plurals[2]


def generate_upload_name(instance, filename, prefix=None, unique=False):
    """
    Генерация пути загрузки для файлов для полей
        model.FileField
        model.ImageField
    """
    ext = os.path.splitext(filename)[1]
    name = str(instance.pk or '') + filename + (str(time()) if unique else '')
    filename = md5(name.encode('utf8')).hexdigest() + ext
    basedir = os.path.join(instance._meta.app_label, instance._meta.model_name)
    if prefix:
        basedir = os.path.join(basedir, prefix)
    return os.path.join(basedir, filename[:2], filename[2:4], filename)


class Bunch(object):
    """
    Преобразование словаря в экземпляр класса
    TODO: либо реализовать полность, либо добавить
        библиотеку в requirements
    """
    def __init__(self, args):
        for key in args:
            setattr(self, key, args[key])
