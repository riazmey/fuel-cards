
import os
import json
import importlib

from django.db import transaction


@transaction.atomic
def filling_enumerate(name_model: str, file_name: str):
    ModelClass = getattr(importlib.import_module('cards.models'), name_model)

    print(f'Заполняет таблицу модели {name_model}')
    path_file = f'{os.getcwd()}/cards/filling/{file_name}'
    with open(path_file, 'r') as file:
        json_data = json.load(file)
        for item_data in json_data:
            code_str = item_data.get('code_str', '')
            comment = item_data.get('_comment', '')
            if comment:
                continue
            defaults = {'repr': item_data.get('repr', '')}
            data_object, created = ModelClass.objects.update_or_create(
                code_str=code_str, defaults=defaults)
            if created == True:
                print(f' Новый объект: {data_object.repr}')
            else:
                print(f' Обновление: {data_object.repr}')
        print('')


def filling_all():
    filling_enumerate('EnumCardStatus', 'enum_card_status.json')
    filling_enumerate('EnumItemCategory', 'enum_item_category.json')
    filling_enumerate('EnumLimitPeriod', 'enum_limit_period.json')
    filling_enumerate('EnumLimitType', 'enum_limit_type.json')
    filling_enumerate('EnumSiteType', 'enum_site_type.json')
    filling_enumerate('EnumTransactionType', 'enum_transaction_type.json')
