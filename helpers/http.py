# -*- coding: utf-8 -*-
import pickle
import os
import random
import requests

from django.conf import settings


class HttpClient(object):
    """
    Обертка над requests использующая куки
    """
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:31.0) Gecko/20100101 Firefox/31.0'
    COOKIE_PATH = settings.PROJECT_DIR + '/cache/http_client_cookies.txt'

    def __init__(self):
        if not os.path.exists(os.path.dirname(self.COOKIE_PATH)):
            os.makedirs(os.path.dirname(self.COOKIE_PATH))
        self.ip = self._get_ip()

    def get(self, url):
        if self._get_cookies():
            response = requests.get(
                url, cookies=self._get_cookies(), stream=True, headers={
                    'User-Agent': self.USER_AGENT,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en,ru-ru;q=0.8,ru;q=0.5,en-us;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Referer': 'http://market.yandex.ru/',
                    'X-Forwarded-For': self.ip
                }
            )
        else:
            response = requests.get(
                url, stream=True, headers={
                    'User-Agent': self.USER_AGENT,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en,ru-ru;q=0.8,ru;q=0.5,en-us;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Referer': 'http://market.yandex.ru/',
                    'X-Forwarded-For': self.ip
                }
            )

        if response.status_code == 200:
            self._set_cookies(response.cookies)
            return response.text

    def _get_cookies(self):
        if os.path.isfile(self.COOKIE_PATH):
            with open(self.COOKIE_PATH, 'rb') as f:
                return pickle.load(f)
        return False

    def _set_cookies(self, cookies):
        with open(self.COOKIE_PATH, 'wb') as f:
            pickle.dump(cookies, f, 0)

    def _get_ip(self):
        return '192.168.' + str(random.randint(10, 240)) + '.' + str(random.randint(10, 240))
