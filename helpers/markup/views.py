# -*- coding: utf-8 -*-
from django.views.generic import View
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
from django.template.loader import get_template


class TemplateView(View):
    """
    Выводить сырой шаблон
        по url соответствующему иерархии папок
    """
    def get_template_name(self):
        try:
            template_name = '%s.html' % self.kwargs['template_name']
            get_template(template_name)
            return template_name
        except TemplateDoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        return render_to_response(self.get_template_name())
