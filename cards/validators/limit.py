
from django.core.exceptions import ValidationError

from cards.models import (
    Site,
    Card,
    Limit)


def validate_limit_id_external(data: dict):
    site = data.get('site')
    number = data.get('card')
    id_external = data.get('id_external')
    site_obj = Site.objects.get(id=site)
    card_obj = Card.objects.get(site=site_obj, number=number)
    if not Limit.objects.filter(site=site_obj, card=card_obj, id_external=id_external).exists():
        message = f'У топливной карты \'{card_obj}\' отсутствует лимит с внешним ID \'{id_external}\''
        raise ValidationError(message)

def validate_limit_deleted(data: dict):
    site = data.get('site')
    number = data.get('card')
    id_external = data.get('id_external')
    site_obj = Site.objects.get(id=site)
    card_obj = Card.objects.get(site=site_obj, number=number)
    limit_obj = Limit.objects.get(site=site_obj, card=card_obj, id_external=id_external)
    if limit_obj.deleted:
        message = f'Лимит \'{limit_obj}\' удален. Нельзя менять удаленый лимит топливной карты.'
        raise ValidationError({'status': message})
