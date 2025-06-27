
import importlib
from django.db.models.signals import post_init
from django.dispatch import receiver
from django.db import models

from .enum_site_type import EnumSiteType


class Site(models.Model):
    
    class Meta:
        
        constraints = [
            models.UniqueConstraint(
                fields=['type', 'url', 'login'],
                name='unique_site_type_url_login')]
        
        indexes = [
            models.Index(
                fields=['type', 'url', 'login'],
                name='site_type_url_login_idx')]
        
        verbose_name = 'Сайт'
        verbose_name_plural = 'Сайты'
        ordering = ['type']

    type = models.ForeignKey(
        EnumSiteType,
        on_delete = models.PROTECT,
        blank = False,
        verbose_name = 'Тип сайта')

    url = models.URLField(
        default = '',
        blank = False,
        verbose_name = 'Адрес (URL)')

    login = models.CharField(
        max_length = 100,
        default = '',
        blank = False,
        verbose_name = 'Логин')

    password = models.CharField(
        max_length = 100,
        default = '',
        blank = False,
        verbose_name = 'Пароль')

    contract_id = models.CharField(
        max_length = 40,
        default = '',
        blank = True,
        verbose_name = 'Идентификатор договора')

    token = models.CharField(
        max_length = 256,
        default = '',
        blank = True,
        verbose_name = 'Ключ безопасности')

    @property
    def repr(self) -> str:
        if self.pk:
            return f'{self.type.repr} ({self.url}; {self.login})'[:255]
        else:
            return 'Сайт (новый)'

    def __str__(self):
        return self.repr

    def __repr__(self):
        return self.repr

@receiver(post_init, sender=Site)
def initialize_ws(sender, instance: Site, **kwargs):
    instance.ws = None
    if not instance.id:
        return
    try:
        name_mixin_class = f'WSSite{instance.type.code_str.title()}'
        ClassMixIn = getattr(importlib.import_module('ws.sites'), name_mixin_class)
        ClassBase = getattr(importlib.import_module('ws.sites'), 'WSSiteBase')
        MetaClass = type(name_mixin_class, (ClassMixIn, ClassBase), {})
        instance.ws = MetaClass(instance)
    except Exception as e:
        print(f"Error initializing the MixIn class: {e}")
