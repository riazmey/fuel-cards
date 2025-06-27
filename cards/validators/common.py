
from django.core.exceptions import ValidationError

from cards.models import (
    EnumLimitType,
    EnumLimitPeriod,
    EnumItemCategory,
    EnumCardStatus,
    Site,
    Card,
    Item)


def validate_common_site(params: dict):
    site = params.get('site', '')
    if not Site.objects.filter(pk=site).exists():
        message = f'Сайт с идентификатором \'{site}\' не зарегистрирован в системе'
        raise ValidationError(message)

def validate_common_card(params: dict):
    site_obj = Site.objects.get(id=params.get('site', ''))
    number = params.get('card', '')
    if not Card.objects.filter(site=site_obj, number=number).exists():
        message = f'Топливная карта с номером \'{number}\' не зарегистрирована для сайта \'{site_obj}\''
        raise ValidationError(message)

def validate_common_card_status(params: dict):
    status = params.get('status', '')
    if not EnumCardStatus.objects.filter(code_str=status).exists():
        message = f'Не удалось найти статус топливной карты с кодом \'{status}\''
        raise ValidationError(message)

def validate_common_limit_type(params: dict):
    type = params.get('type', '')
    if not EnumLimitType.objects.filter(code_str=type).exists():
        message = f'Не удалось найти тип лимита с кодом \'{type}\''
        raise ValidationError(message)

def validate_common_category(params: dict):
    category = params.get('category', '')
    if not EnumItemCategory.objects.filter(code_str=category).exists():
        message = f'Не удалось найти категорию товаров/услуг с кодом \'{category}\''
        raise ValidationError(message)

def validate_common_item(params: dict):
    item = params.get('item', '')
    if not Item.objects.filter(id_external=item).exists():
        message = f'Не удалось найти товар/услугу с внешним идентификатором \'{item}\''
        raise ValidationError(message)

def validate_common_period(params: dict):
    period = params.get('period', '')
    if not EnumLimitPeriod.objects.filter(code_str=period).exists():
        message = f'Не удалось найти тип периода с кодом \'{period}\''
        raise ValidationError(message)

def validate_common_unit(params: dict):
    available_value = ['383', '112']
    unit = params.get('unit', '')
    if not unit in available_value:
        message = f'Единица измерения допускается только с кодом 383 или 112, однако ' \
            + 'в параметрах передали код \'{unit}\''
        raise ValidationError(message)
