# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import TemplateView

urlpatterns = [
    url(r'^(?P<template_name>.*)/$', TemplateView.as_view())
]
