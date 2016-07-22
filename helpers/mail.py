# -*- coding: utf-8 -*-
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# TODO: заменить на get_user_model
from django.contrib.auth.models import User
from django.conf import settings


def send_mail_notification(action, subject, context, admin=True, recipient=None, html=False):
    """
    Отправка email
        Шаблоны для администратора должны лежать mail/admin/<action>.<html/txt>
        Шаблоны для пользователя должны лежать mail/user/<action>.<html/txt>

        action - название события
        subject - тема сообщения
        admin - сообщение для админа
        recipient – список получателей
        html - является ли сообщениt html
    """
    if not isinstance(recipient, (list, tuple)):
        recipient = [recipient]
    if admin:
        recipient = User.objects.filter(
            is_superuser=True
        ).values_list('email', flat=True)

    template_name = 'mail/%s/%s.%s' % (
        'admin' if admin else 'user',
        action,
        'html' if html else 'txt'
    )

    msg = EmailMessage(
        subject,
        render_to_string(template_name, context),
        settings.DEFAULT_FROM_EMAIL,
        recipient
    )
    if html:
        msg.content_subtype = 'html'
    msg.send()
