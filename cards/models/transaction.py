
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.db import models

from .enum_transaction_type import EnumTransactionType

from .site import Site
from .card import Card


class Transaction(models.Model):

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=['card', 'type', 'id_external'],
                name='unique_card_type_id_ext')]

        indexes = [
            models.Index(
                fields=['site', 'date'],
                name='transaction_site_date_idx'),
            models.Index(
                fields=['card', 'date'],
                name='transaction_card_date_idx'),
            models.Index(
                fields=['card', 'id_external'],
                name='transaction_card_id_ext_idx')]

        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ['date']

    site = models.ForeignKey(
        Site,
        on_delete = models.PROTECT,
        blank = False,
        verbose_name = 'Сайт')

    card = models.ForeignKey(
        Card,
        on_delete = models.PROTECT,
        blank = False,
        verbose_name = 'Топливная карта')

    date = models.DateTimeField(
        default = now,
        blank = False,
        verbose_name = 'Дата')

    id_external = models.CharField(
        max_length = 100,
        default = '',
        blank = False,
        verbose_name = 'ID (внешний)')

    type = models.ForeignKey(
        EnumTransactionType,
        on_delete = models.PROTECT,
        blank = False,
        verbose_name = 'Тип')

    details = models.CharField(
        max_length = 1024,
        default = '',
        blank = True,
        verbose_name = 'Описание')

    amount = models.FloatField(
        default = 0.00,
        blank = False,
        verbose_name = 'Сумма')

    discount = models.FloatField(
        default = 0.00,
        blank = True,
        verbose_name = 'Сумма скидки')

    @property
    def repr(self) -> str:
        if self.pk:
            date_repr = self.date.strftime('%d.%m.%Y %H:%M:%S')
            return f'{self.type} по карте {self.card}, от {date_repr}, ID {self.id_external}'
        else:
            return 'Транзакция (новая)'

    def __str__(self):
        return self.repr

    def __repr__(self):
        return self.repr

@receiver(pre_save, sender=Transaction)
def update_created(sender, instance: Transaction, **kwargs):
    instance.id_external = instance.id_external.strip()
