# -*- coding: utf-8 -*-
import re
from django.db.models import Q


def get_search_query(query_string, search_fields=None):
    """
    Функция возвращает комбинацию из Q объяектов для поиска
    фразы
        query_string - сырая поисковая строка
        search_fields - список полей модели

    Использование:
        SomeModel.objects.filter(
            get_search_query('поисковый запрос', ['title', 'brand__title']))
    """
    if search_fields is None:
        search_fields = ['title']

    query = None
    for term in normalize_query(query_string):
        or_query = None

        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query

    return query


def normalize_query(query_string):
    """
    Функция нормализации поискового запроса
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    """
    findterms = re.compile(r'"([^"]+)"|(\S+)').findall
    normspace = re.compile(r'\s{2,}').sub
    return [normspace(' ', (t[0] or t[1]).strip()).lower() for t in findterms(query_string)]
