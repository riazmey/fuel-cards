
from django.db import models

from .item import Item
from .transaction import Transaction


class TransactionItem(models.Model):

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=['transaction', 'item'], name='unique_transaction_item')]

        indexes = [
            models.Index(fields=['transaction'], name='transaction_item_idx'),
            models.Index(fields=['transaction', 'item'], name='transaction_item_item_idx')]

        verbose_name = 'Товар транзакции'
        verbose_name_plural = 'Товары транзакций'
        ordering = ['transaction', 'item']

    transaction = models.ForeignKey(
        Transaction,
        on_delete = models.CASCADE,
        related_name = 'transaction_relate_transaction_item',
        blank = True,
        verbose_name = 'Сайт')

    item = models.ForeignKey(
        Item,
        on_delete = models.PROTECT,
        blank = False,
        null = True,
        verbose_name = 'Товар')

    item_description = models.CharField(
        max_length = 256,
        default = '',
        blank = True,
        verbose_name = 'Описание товара')

    quantity = models.FloatField(
        default = 0.00,
        blank = False,
        verbose_name = 'Количество')

    price = models.FloatField(
        default = 0.00,
        blank = False,
        verbose_name = 'Цена')

    price_with_discount = models.FloatField(
        default = 0.00,
        blank = True,
        verbose_name = 'Цена (с учетом скидки)')

    amount = models.FloatField(
        default = 0.00,
        blank = False,
        verbose_name = 'Сумма')

    amount_with_discount = models.FloatField(
        default = 0.00,
        blank = True,
        verbose_name = 'Сумма (с учетом скидки)')

    @property
    def repr(self) -> str:
        if self.pk:
            return f'{self.item.name} ({self.transaction})'
        else:
            return 'Товар транзакции (новый)'

    def __str__(self):
        return self.repr

    def __repr__(self):
        return self.repr
