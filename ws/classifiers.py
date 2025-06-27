
import json
import requests
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from typing import Dict, Tuple, List

import logging
logger = logging.getLogger(__name__)

class WSClassifiers:

    class URNs:
        OKV = '/api/v1/okv'
        OKEI = '/api/v1/okei'

    def __init__(self):
        config = settings.WEB_SERVICES.get('classifiers')
        if not config:
            raise ImproperlyConfigured('There is no setting for the WEB_SERVICES.сlassifiers service in the settings file.')
        self.url = config.get('URL')
        self.cache_lifetime = 60 * 5
        self.request_timeout = 30
        self.base_headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'Service Fuel cards'}

    def list_currencies(self) -> List[Tuple[str, str]]:
        result = []
        currencies = self.get_currency()
        for currency_data in currencies:
            code_str = currency_data.get('code_str')
            name = currency_data.get('name')
            result.append((code_str, name))
        return result

    def list_units(self, params: Dict) -> List[Tuple[str, str]]:
        result = []
        units = self.get_unit(params)
        for unit_data in units:
            code_dec = unit_data.get('code_dec')
            name = unit_data.get('name')
            result.append((code_dec, name))
        return result
    
    def get_currency(self, params: Dict = None) -> List[dict]:
        key_cache = self._key_cache_formatted(f'WSClassifiers.get_currency(params={params})')
        return self._get_request(key_cache, self.URNs.OKV, params)

    def get_unit(self, params: Dict = None) -> List[dict]:
        key_cache = self._key_cache_formatted(f'WSClassifiers.get_unit(params={params})')
        return self._get_request(key_cache, self.URNs.OKEI, params)

    def _key_cache_formatted(self, key_cache: str) -> str:
        rules_replace = [
            ('\'', ''),
            (':', ''),
            ('.', '_'),
            (' ', '_'),
            ('(', '_'),
            (')', '')]
        result = key_cache
        for replaced, to_replace in rules_replace:
            result = result.replace(replaced, to_replace)
        return result

    def _get_request(self, key_cache: str, url: str, params: Dict = None) -> List[dict]:
        result = []
        cached_data = None
        try:
            cached_data = cache.get(key_cache)
        except Exception as e:
            message = f'An error occurred while working with the cache: {str(e)}'
            logger.warning(message)
        if cached_data == None:
            result, recieved = self._request(requests.get, url, params)
            if recieved:
                try:
                    cache.set(key_cache, result, self.cache_lifetime)
                except Exception as e:
                    message = f'When trying to write data to the cache, an error occurred: {str(e)}'
                    logger.warning(message)
        else:
            result = cached_data
        return result

    def _request(self, method: requests.Request, urn: str, params: Dict = None) -> Tuple[list, bool]:
        data = []
        result = True
        url = f'{self.url}{urn}'
        headers = self.base_headers.copy()

        try:
            response = method(url, headers=headers, params=params, timeout=self.request_timeout)
            response.raise_for_status()

            data_json = response.json()
            if isinstance(data_json, dict):
                data.append(data_json)
            elif isinstance(data_json, list):
                data += data_json
            else:
                message = f'An unexpected type of received data was obtained after ' + \
                    ' its serialization: {type(data_json)}'
                logger.error(message)
                result = False

        except requests.RequestException as e:
            message = f'API request failed: {str(e)}'
            logger.error(message)
            result = False
        except json.JSONDecodeError as e:
            message = f'Error parsing JSON: {str(e)}'
            logger.error(message)
            result = False

        return data, result
