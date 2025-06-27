
import locale

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.db import models

from .site import Site


class SiteBalance(models.Model):

    class Meta:
        indexes = [models.Index(fields=['site', 'date'], name='balance_site_date_idx')]
        ordering = ['site', 'date']
        verbose_name = 'Остаток ден. средств на сайте'
        verbose_name_plural = 'Остатки ден. средств на сайтах'

    site = models.ForeignKey(
        Site,
        on_delete = models.PROTECT,
        blank = False,
        verbose_name = 'Сайт')

    date = models.DateTimeField(
        default = now,
        blank = False,
        verbose_name = 'Дата')

    balance = models.FloatField(
        default = 0.00,
        blank = True,
        verbose_name = 'Сумма остаток')

    credit = models.FloatField(
        default = 0.00,
        blank = True,
        verbose_name = 'Сумма кредита')

    available = models.FloatField(
        default = 0.00,
        blank = True,
        verbose_name = 'Сумма доступно (остаток + кредит)')

    @property
    def repr(self) -> str:
        if self.pk:
            date_repr = self.date.strftime('%d.%m.%Y %H:%M:%S')
            available_repr = locale.format_string('%.2f', self.available, grouping=True)
            return f'{date_repr}, доступно: {available_repr} ({self.site})'
        else:
            return 'Остатки ден. средств (новый)'

    def __str__(self):
        return self.repr

    def __repr__(self):
        return self.repr

@receiver(pre_save, sender=SiteBalance)
def update_created(sender, instance: SiteBalance, **kwargs):
    instance.available = instance.balance + instance.credit
