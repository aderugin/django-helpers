# -*- coding: utf-8 -*-
import base64
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.contrib.auth import authenticate
from django.core.paginator import Paginator, EmptyPage
from django.template.loader import render_to_string
from django.template import RequestContext


class OrderedObjectListMixin(object):
    """
    Миксин добавляющий возможность сортировки объектов
        order_by = (
            ('default', 'По названию'),
            ('price', 'Сначала дешевые'),
            ('-price', 'Сначала дорогие'),
        )
    """
    order_by = None

    def get_queryset(self):
        return self.get_ordered_queryset(super().get_queryset())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.order_by
        context['current_order_by'] = self.get_current_order_by()
        return context

    def get_ordered_queryset(self, queryset):
        ordering = self.request.GET.get('order_by')
        asc = True
        if ordering and ordering in dict(self.order_by):
            asc = not ordering.startswith('-')
            if not asc:
                ordering = ordering.replace('-', '')
            if ordering == 'default' and asc:
                return queryset.order_by(*self.model._meta.ordering)
            if ordering == 'default' and not asc:
                return queryset.order_by(*self.model._meta.ordering).reverse()
            queryset = queryset.order_by('{0}{1}'.format('-' if not asc else '', ordering))
        return queryset

    def get_current_order_by(self):
        """
        Возвращает текущее значение из списка self.order_by
        """
        for value, name in self.order_by:
            if value == self.request.GET.get('order_by'):
                return (value, name)
        return self.order_by[0]


class AjaxObjectListMixin(object):
    """
    Миксин добавляющий возможность получить JSON
    с отрандеренным списком объектов, если в GET
    параметрах есть ajax_page

    Используется для подгрузки объектов в списке

        object_list_template_name - шаблон списка объектов
        paginator_template_name – шаблон паджинатора, если не
            задан, то не выводится в контекст
        _context_object_name - для жесткого переопределения
            названия переменной в шаблоне
    """
    object_list_template_name = None
    paginator_template_name = None
    _context_object_name = None

    def get_ajax_object_list_context_data(self, queryset=None):
        """
        Возвращающий определенную страницу паджинатора
        """
        queryset = queryset or self.get_queryset()
        page = self.request.GET.get('ajax_page')
        paginator = Paginator(queryset, self.paginate_by)
        context_object_name = self._context_object_name or \
            self.get_context_object_name(queryset)

        try:
            object_list = paginator.page(page)
        except EmptyPage:
            object_list = paginator.page(paginator.num_pages)

        context = {
            'state_last': not object_list.has_next(),
            'object_list': render_to_string(
                self.object_list_template_name,
                {context_object_name: object_list},
                context_instance=RequestContext(self.request)
            )
        }
        if self.paginator_template_name:
            context['paginator'] = render_to_string(
                self.paginator_template_name,
                {'paginator': paginator, 'page_obj': object_list},
                context_instance=RequestContext(self.request)
            )
        return context

    def get(self, request, *args, **kwargs):
        if request.is_ajax() and 'ajax_page':
            return JsonResponse(self.get_ajax_object_list_context_data())
        return super().get(request, *args, **kwargs)


class AjaxFormViewMixin(object):
    """
    Миксин для формы, обработка которой происходит через ajax
    Response возвращает JSON объект со статусом валидности,
    url удачного заполнения и списком ошибок
    """
    success_url = None
    form = None
    context_form_name = 'form'

    def get_success_url(self):
        return self.success_url

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            form = self.get_form(request.POST)
            context = {
                'success': False,
                'success_url': self.get_success_url(),
                'error_keys': list(form.errors.keys())
            }
            if form.is_valid():
                self.form_valid(form)
                context['success'] = True
            return JsonResponse(context)
        return HttpResponseBadRequest()

    def form_valid(self, form):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.context_form_name] = self.get_form()
        return context

    def get_form(self, *args, **kwargs):
        return self.form(*args, **kwargs)


# TODO: Обобщить хлебные крошки
class BreadcrumbsMixin(object):
    """
    TODO
    """
    def get_breadcrumbs(self):
        raise NotImplementedError()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.request.breadcrumbs = self.get_breadcrumbs()
        return context


def view_or_basicauth(view, request, *args, **kwargs):
    """
    Авторизует пользователя через HTTP
    """
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).decode('utf8').split(':')
                user = authenticate(username=uname, password=passwd)
                if user is not None and user.is_active and user.is_staff:
                    return view(request, *args, **kwargs)

    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="Access denied"'
    return response
