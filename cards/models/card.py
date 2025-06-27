
from django.db import models

from .enum_card_status import EnumCardStatus
from .site import Site


class Card(models.Model):

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=['site', 'number'],
                name='unique_card_site_number')]

        indexes = [
            models.Index(
                fields=['site', 'number'],
                name='card_site_num_idx'),
            models.Index(
                fields=['site', 'relevant'],
                name='card_site_relev_idx'),
            models.Index(
                fields=['site', 'number', 'relevant'],
                name='card_site_num_relev_idx'),
            models.Index(
                fields=['site', 'status', 'relevant'],
                name='card_site_stat_relev_idx'),
            models.Index(
                fields=['site', 'number', 'status', 'relevant'],
                name='card_site_num_stat_relev_idx')]

        verbose_name = 'Топливная карта'
        verbose_name_plural = 'Топливные карты'
        ordering = ['site', 'number']

    site = models.ForeignKey(
        Site,
        on_delete = models.PROTECT,
        blank = False,
        verbose_name = 'Сайт')

    number = models.CharField(
        max_length = 40,
        default = '',
        blank = False,
        verbose_name = 'Номер карты')

    status = models.ForeignKey(
        EnumCardStatus,
        on_delete = models.PROTECT,
        blank = False,
        verbose_name = 'Статус')

    relevant = models.BooleanField(
        default = True,
        blank = False,
        verbose_name = 'Актуальна')

    @property
    def repr(self) -> str:
        if self.pk:
            self.number = self.number.strip().replace(' ', '')
            len_number = len(self.number)

            match len_number:
                case 19:
                    len_section = 4
                    num_section = 5
                case 16:
                    len_section = 4
                    num_section = 4
                case 12:
                    len_section = 4
                    num_section = 3
                case 10:
                    len_section = 3
                    num_section = 3
                case _:
                    len_section = 0
                    num_section = 0

            if len_section:
                sections = []
                for i in range(0, len_number, len_section):
                    num_section = num_section - 1
                    if num_section:
                        sections.append(self.number[i:i + len_section])
                    else:
                        sections.append(self.number[i:])
                        break
                return ' '.join(sections)
            else:
                return self.number
        else:
            return 'Топливная карта (новая)'

    def __str__(self):
        return self.repr

    def __repr__(self):
        return self.repr
