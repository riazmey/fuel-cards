
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import models

from .enum_limit_type import EnumLimitType
from .enum_limit_period import EnumLimitPeriod
from .enum_item_category import EnumItemCategory

from .site import Site
from .card import Card
from .item import Item


class Limit(models.Model):

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=['card', 'id_external'],
                name='unique_card_id_ext')]

        indexes = [
            models.Index(
                fields=['card'],
                name='limit_card_idx'),
            models.Index(
                fields=['card', 'deleted'],
                name='limit_card_deleted_idx'),
            models.Index(
                fields=['site'],
                name='limit_site_idx'),
            models.Index(
                fields=['site', 'deleted'],
                name='limit_site_deleted_idx'),
            models.Index(
                fields=['site', 'card', 'id_external'],
                name='limit_site_card_id_ext_idx')]

        verbose_name = 'Лимит топливной карты'
        verbose_name_plural = 'Лимиты топливных карт'
        ordering = ['type']

    site = models.ForeignKey(
        Site,
        on_delete = models.PROTECT,
        blank = False,
        verbose_name = 'Сайт')

    card = models.ForeignKey(
        Card,
        on_delete = models.PROTECT,
        related_name = 'card_relate_limit',
        blank = False,
        verbose_name = 'Топливная карта')

    id_external = models.CharField(
        max_length = 100,
        default = '',
        blank = False,
        verbose_name = 'ID (внешний)')

    type = models.ForeignKey(
        EnumLimitType,
        on_delete = models.PROTECT,
        blank = False,
        verbose_name = 'Тип')

    category = models.ForeignKey(
        EnumItemCategory,
        on_delete = models.PROTECT,
        blank = True,
        null = True,
        verbose_name = 'Категория')

    item = models.ForeignKey(
        Item,
        on_delete = models.PROTECT,
        blank = True,
        null = True,
        verbose_name = 'Товар')

    period = models.ForeignKey(
        EnumLimitPeriod,
        on_delete = models.PROTECT,
        blank = False,
        verbose_name = 'Периодичность')

    unit = models.CharField(
        max_length = 4,
        default = '',
        blank = True,
        verbose_name = 'Единица измерения')

    value = models.FloatField(
        default = 0.00,
        blank = True,
        verbose_name = 'Значение')

    balance = models.FloatField(
        default = 0.00,
        blank = True,
        verbose_name = 'Остаток')

    deleted = models.BooleanField(
        default = False,
        blank = False,
        verbose_name = 'Удален')

    @property
    def repr(self) -> str:
        if self.pk:
            return f'{self.card}, ID {self.id_external.strip()}, {self.type}, {self.period}'
        else:
            return 'Лимит топливной карты (новый)'

    def __str__(self):
        return self.repr

    def __repr__(self):
        return self.repr

@receiver(pre_save, sender=Limit)
def update_created(sender, instance: Limit, **kwargs):
    match instance.type.code_str:
        case 'all':
            instance.category = None
            instance.item = None
        case 'category':
            instance.item = None
        case 'item':
            instance.category = None
