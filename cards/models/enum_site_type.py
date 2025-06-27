
from django.db import models

class EnumSiteType(models.Model):

    class Meta:
        indexes = [models.Index(fields=['code_str'])]
        ordering = ['code_str']
        verbose_name = 'Тип сайта'
        verbose_name_plural = 'Типы сайтов'

    code_str = models.CharField(
        max_length = 20,
        unique = True,
        default = '',
        blank = False,
        verbose_name = 'Код (строковый)')

    repr = models.CharField(
        max_length = 255,
        default = '',
        blank = False,
        verbose_name = 'Тип сайта')

    def __str__(self):
        return self.repr

    def __repr__(self):
        return self.repr
