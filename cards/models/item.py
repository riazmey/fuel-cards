
from django.db import models

from .enum_item_category import EnumItemCategory
from .site import Site


class Item(models.Model):

    class Meta:

        constraints = [
            models.UniqueConstraint(fields=['site', 'id_external'], name='unique_site_id_ext'),
            models.UniqueConstraint(fields=['site', 'name'], name='unique_site_name')]

        indexes = [
            models.Index(fields=['site'], name='item_site_idx'),
            models.Index(fields=['site', 'name'], name='item_site_name_idx'),
            models.Index(fields=['site', 'id_external'], name='item_site_id_ext_idx')]

        verbose_name = 'Товар сайта'
        verbose_name_plural = 'Товары сайтов'
        ordering = ['site', 'name']

    site = models.ForeignKey(
        Site,
        on_delete = models.PROTECT,
        blank = False,
        verbose_name = 'Сайт')

    id_external = models.CharField(
        max_length = 100,
        default = '',
        blank = False,
        verbose_name = 'ID (внешний)')

    category = models.ForeignKey(
        EnumItemCategory,
        on_delete = models.PROTECT,
        blank = False,
        verbose_name = 'Категория')

    name = models.CharField(
        max_length = 150,
        default = '',
        blank = False,
        verbose_name = 'Наименование')

    @property
    def repr(self) -> str:
        if self.pk:
            return f'{self.name} ({self.site})'
        else:
            return 'Товар сайта (новый)'

    def __str__(self):
        return self.repr

    def __repr__(self):
        return self.repr
