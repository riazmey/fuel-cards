
"""
    To execute this script run:
        python manage.py shell
        from cards.tasks import *
        from datetime import timedelta
        import_balance()
        import_items()
        import_cards()
        import_limits()
        import_transactions(weeks=84)
        exit()
"""

from typing import Tuple
from datetime import timedelta

from celery import shared_task
from cards.models import Site
from django.utils import timezone


def import_from_sites(name_function: str) -> Tuple[list, bool]:
    result = []
    success = True
    sites = Site.objects.all()
    for site in sites:
        function = getattr(site.ws, name_function)
        data, success = function()
        if not success:
            break
        if isinstance(data, list):
            total_data = len(data)
            result += data
            print(f'    Сайт {site}. Загружено/обновлено записей: {total_data}')
        else:
            result.append(data)
    return result, success


@shared_task(name='Загрузка остатков на лицевых счетах (по всем сайтам)')
def import_balance():
    name_function = 'import_balance'
    print('Импорт остатков на лицевых счетах сайтов...')
    data, success = import_from_sites(name_function)
    return success


@shared_task(name='Загрузка товаров (по всем сайтам)')
def import_items():
    name_function = 'import_items'
    print('Импорт товаров сайтов...')
    data, success = import_from_sites(name_function)
    return success


@shared_task(name='Загрузка топливных карт (по всем сайтам)')
def import_cards():
    name_function = 'import_cards'
    print('Импорт топливных карт сайтов...')
    data, success = import_from_sites(name_function)
    return success


@shared_task(name='Загрузка лимитов топливных карт (по всем сайтам)')
def import_limits():
    name_function = 'import_limits'
    print('Импорт лимитов топливных карт...')
    data, success = import_from_sites(name_function)
    return success


@shared_task(name='Загрузка транзакций (за прошедший период: параметры timedelta) (по всем сайтам)')
def import_transactions(**kwargs):
    success = True
    sites = Site.objects.all()
    end = timezone.now()
    begin = end - timedelta(**kwargs)
    params = {'begin': begin, 'end': end}
    print(f'Импорт транзакций (с {begin} по {end})...')
    for site in sites:
        data, success = site.ws.import_transactions(**params)
        if not success:
            break
        total_data = len(data)
        print(f'    Сайт {site}. Загружено/обновлено записей: {total_data}')
    return success