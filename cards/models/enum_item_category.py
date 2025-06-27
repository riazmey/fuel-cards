
from django.db import models

class EnumItemCategory(models.Model):

    class Meta:
        indexes = [models.Index(fields=['code_str'])]
        ordering = ['code_str']
        verbose_name = 'Категория товара'
        verbose_name_plural = 'Категории товаров'

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
        verbose_name = 'Категория товара')

    def __str__(self):
        return self.repr

    def __repr__(self):
        return self.repr
