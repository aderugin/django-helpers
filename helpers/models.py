# -*- coding: utf-8 -*-
import requests

from datetime import datetime
from django.db import models
from autoslug import AutoSlugField
from django.core.files.base import ContentFile
from .utils import generate_upload_name


class ActivatableQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def activate(self):
        return self.update(active=True)

    def deactivate(self):
        return self.update(active=False)


class ActivatableManager(models.Manager):
    def get_queryset(self):
        return ActivatableQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def activate(self):
        return self.get_queryset().activate()

    def deactivate(self):
        return self.get_queryset().deactivate()


class ActivatableMixin(models.Model):
    """
    Миксин позволяющий активировать / деактивировать сущность
    """
    objects = ActivatableManager()

    active = models.BooleanField(verbose_name='Активность', default=True, db_index=True)

    class Meta:
        abstract = True

    def deactivate(self, commit=True):
        self.active = False
        if commit:
            self.save()


class SortableMixin(models.Model):
    """
    Добавляет сортировку
    """
    sort = models.PositiveSmallIntegerField(verbose_name='Сортировка', default=500,
                                            help_text='Чем меньше - тем выше', db_index=True)

    class Meta:
        ordering = ['sort']
        abstract = True


class SlugTitleMixin(models.Model):
    """
    Добавляет title и slug от него
    """
    title = models.CharField(verbose_name='Название', max_length=255, db_index=True)
    slug = AutoSlugField(populate_from='title', unique=True, editable=True, db_index=True,
                         blank=True, help_text='Если оставить пустым - заполнится автоматом',
                         max_length=255,)

    class Meta:
        abstract = True
        ordering = ['title']

    def __str__(self):
        return self.title


class TitleMixin(models.Model):
    """
    Добавляет title
    """
    title = models.CharField(verbose_name='Название', max_length=255, db_index=True)

    class Meta:
        abstract = True
        ordering = ['title']

    def __str__(self):
        return self.title


class CodeMixin(models.Model):
    """
    Внешний код
    """
    code = models.CharField(verbose_name='Внешний код', max_length=50, db_index=True)

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    """
    Дата создания записи
    """
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class DateMixin(models.Model):
    """
    Поле Дата
    """
    date = models.DateField(verbose_name='Дата')

    class Meta:
        abstract = True


class DatetimeMixin(models.Model):
    """
    Поле Дата + время
    """
    datetime = models.DateTimeField(verbose_name='Дата')

    class Meta:
        abstract = True


class CreatedAtMixin(models.Model):
    """
    Дата создания
    """
    created_at = models.DateTimeField(verbose_name='Дата создания')

    class Meta:
        abstract = True
        ordering = ['created_at']


class LastUpdateMixin(models.Model):
    """
    Последнее обновление, обновляется автоматически
    """
    last_update = models.DateTimeField(verbose_name='Последнее обновление', auto_now=True,
                                       db_index=True)

    class Meta:
        abstract = True


class LastUpdateManualMixin(models.Model):
    """
    Последнее обновление, обновляется вручную
    """
    last_update = models.DateTimeField(verbose_name='Последнее обновление', blank=True,
                                       db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.last_update:
            self.last_update = datetime.now()
        super().save(*args, **kwargs)

    def update_last_update(self, commit=True):
        self.last_update = datetime.now()
        if commit:
            self.save()


class ImageMixin(models.Model):
    """
    Картинка
    """
    image = models.ImageField(verbose_name='Изображение', upload_to=generate_upload_name,
                              max_length=255)

    class Meta:
        abstract = True


class OldPriceMixin(models.Model):
    """
    Старая цена
    """
    old_price = models.DecimalField(verbose_name='Старая цена', max_digits=10, decimal_places=2,
                                    blank=True, null=True, default=None)

    class Meta:
        abstract = True


class PriceMixin(models.Model):
    """
    Цена
    """
    price = models.DecimalField(verbose_name='Цена', max_digits=10, decimal_places=2)

    class Meta:
        abstract = True


class YouTubeMixin(models.Model):
    """
    Добавляет поле для ссылки с youtube и метод, получающи id видео
        При сохранении загружается превью видео
    """
    youtube_link = models.URLField(verbose_name='Ссылка на видео с youtube.com', blank=True,
                                   null=True, default=None)
    youtube_thumbnail = models.ImageField(verbose_name='Изображение',
                                          upload_to=generate_upload_name,
                                          max_length=255, blank=True, null=True,
                                          default=None)

    class Meta:
        abstract = True

    @property
    def youtube_id(self):
        if self.youtube_link and '?v=' in self.youtube_link:
            return self.youtube_link.split('?v=')[1]

    def save(self, *args, **kwargs):
        origin = None
        if self.pk:
            origin = self.__class__.objects.get(pk=self.pk)
        super().save(*args, **kwargs)
        if origin and origin.youtube_link != self.youtube_link:
            self._update_youtube_thumbnail()
        elif not self.youtube_thumbnail and self.youtube_id:
            self._update_youtube_thumbnail()

    def _update_youtube_thumbnail(self):
        image_response = requests.get(
            'http://img.youtube.com/vi/%s/0.jpg' % self.youtube_id)
        if image_response.status_code == 200:
            self.youtube_thumbnail.save(
                '%s.jpg' % self.youtube_id,
                ContentFile(image_response.content)
            )


class TextMixin(models.Model):
    """
    Необязательное текстовое поле
    """
    text = models.TextField(verbose_name='Текст', blank=True, null=True, default=None)

    class Meta:
        abstract = True


class RequiredTextMixin(models.Model):
    """
    Обязательное текстовое поле
    """
    text = models.TextField(verbose_name='Текст')

    class Meta:
        abstract = True


class NameMixin(models.Model):
    """
    Добавляет не обязательное поле "Имя"
    """
    name = models.CharField(verbose_name='Имя', max_length=255, blank=True,
                            null=True, default=None)

    class Meta:
        abstract = True


class RequiredNameMixin(models.Model):
    """
    Добавляет не обязательное поле "Имя"
    """
    name = models.CharField(verbose_name='Имя', max_length=255)

    class Meta:
        abstract = True


try:
    from ckeditor.fields import RichTextField

    class RichTextMixin(models.Model):
        """
        Необязательное текстовое поле с CKEditor
        """
        text = RichTextField(verbose_name='Текст', blank=True, null=True, default=None)

        class Meta:
            abstract = True

    class RichRequiredTextMixin(models.Model):
        """
        Обязательное текстовое поле с CKEditor
        """
        text = RichTextField(verbose_name='Текст')

        class Meta:
            abstract = True

except ImportError:
    pass
