
import pytz
import json
import requests
from datetime import datetime, timedelta
from dateutil import parser
from typing import Any, Dict, Tuple, List
from django.core.exceptions import RequestAborted

from multithreading import MultithreadedDataProcessing

from .common import (
    WSDataSiteBalance,
    WSDataCard,
    WSDataItem,
    WSDataCardLimits,
    WSDataLimit,
    WSDataTransaction,
    WSDataTransactionItem)

import logging

logger = logging.getLogger(__name__)

class WSSiteRosneft:

    class URNs:
        balance_by_contract_get = '/api/emv/v1/GetContractBalance'
        items_by_contract_get = '/api/emv/v1/GetGoodsList'
        cards_by_contract_get = '/api/emv/v1/GetCardsByContract'
        card_status_active = '/api/emv/v1/UnblockingCard'
        card_status_block = '/api/emv/v1/BlockingCard'
        limits_by_card_get = '/api/emv/v2/GetCardLimits'
        limits_by_contract_get = '/api/emv/v2/GetAllLimiters'
        limit_add = '/api/emv/v1/CreateCardLimit'
        limit_update = '/api/emv/v1/EditCardLimit'
        limit_delete = '/api/emv/v1/DeleteCardLimit'
        transactions_by_contract_get = '/api/emv/v2/GetOperByContract'

    def __init__(self, market):

        super().__init__(market)

        self.max_period_transaction = timedelta(days=30)

        self.base_headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}

        self.base_params = {
            'u': self.login,
            'p': self.password,
            'contract': self.contract_id,
            'type': 'JSON'}

    def balance_get_ws(self) -> Tuple[WSDataSiteBalance | str, bool]:
        result = WSDataSiteBalance()
        data, received = self._request(requests.get, self.URNs.balance_by_contract_get)
        if received:
            result.balance = data.get('Balance', 0.00)
            result.credit = data.get('CreditLimit', 0.00)
        else:
            result = str(data)
        return result, received

    def items_get_ws(self) -> Tuple[list[WSDataItem] | str, bool]:
        result = []
        data, received = self._request(requests.get, self.URNs.items_by_contract_get)
        if received:
            for data_item in data:
                result.append(
                    WSDataItem(
                        id = data_item.get('Code', ''),
                        name = data_item.get('Name', ''),
                        category = self._convert_data_ws_item_category(data_item)
                    )
                )
        else:
            result = str(data)
        return result, received

    def cards_get_ws(self) -> Tuple[list[WSDataCard] | str, bool]:
        result = []
        data, received = self._request(requests.get, self.URNs.cards_by_contract_get)
        if received:
            for data_card in data:
                result.append(
                    WSDataCard(
                        number = data_card.get('Num', ''),
                        status = self._convert_data_ws_card_status(data_card)
                    )
                )
        else:
            result = str(data)
        return result, received

    def card_status_update_ws(self, card_number: str, status:str) -> Tuple[str, bool]:
        match status:
            case 'active':
                urn = self.URNs.card_status_active
            case 'block':
                urn = self.URNs.card_status_block
            case _:
                return False
        data, success = self._request(
            method = requests.post,
            urn = urn,
            params = {'card': card_number})
        return str(data), success

    def limits_get_ws(self, card_numbers: List[str] = None) -> Tuple[list[WSDataCardLimits] | str, bool]:
        result = []
        if card_numbers:
            data, received = MultithreadedDataProcessing(
                ws = self,
                data = card_numbers,
                handler = handler_limits_get_by_card_numbers).processing()
        else:
            data, received = self._request(
                method = requests.get,
                urn = self.URNs.limits_by_contract_get,
                params = {
                    'flagLimits': 'Y',
                    'flagGoodsRestrictions': 'N',
                    'flagRegionRestrictions': 'N',
                    'flagContract': 'Y'
                }
            )
        if received:
            for card_limits in data:
                result.append(self._convert_data_ws_card_limits(card_limits))
        else:
            result = str(data)
        return result, received

    def limit_add_ws(self, data_limit: WSDataLimit) -> Tuple[str, bool]:
        data, received = self._request(
            method = requests.post,
            urn = self.URNs.limit_add,
            params = {
                'Card': data_limit.card_number,
                'GFlag': self._convert_limit_type_data_ws(data_limit.type),
                'GCode': self._convert_item_data_ws(data_limit.type, data_limit.category, data_limit.item),
                'Prd': self._convert_period_data_ws(data_limit.period),
                'Currency': self._convert_unit_data_ws(data_limit.unit),
                'Val': data_limit.value,
                'request_id': ''})
        if received:
            data_limit.id_external = data.get('LimitCode', '')
        return str(data), received
    
    def limit_update_ws(self, data_limit: WSDataLimit) -> Tuple[str, bool]:
        data, received = self._request(
            method = requests.post,
            urn = self.URNs.limit_update,
            params = {
                'LimitCode': data_limit.id_external,
                'Card': data_limit.card_number,
                'GFlag': self._convert_limit_type_data_ws(data_limit.type),
                'GCode': self._convert_item_data_ws(data_limit.type, data_limit.category, data_limit.item),
                'Prd': self._convert_period_data_ws(data_limit.period),
                'Currency': self._convert_unit_data_ws(data_limit.unit),
                'Val': data_limit.value_new,
                'CurValue': data_limit.value})
        return str(data), received

    def limit_delete_ws(self, card_number: str, id_external: str) -> Tuple[str, bool]:
        data, received = self._request(
            method = requests.post,
            urn = self.URNs.limit_delete,
            params = {
                'LimitCode': id_external,
                'Card': card_number})
        return str(data), received

    def transactions_get_ws(self, begin: datetime, end: datetime) -> Tuple[list[WSDataTransaction] | str, bool]:
        result = []
        periods = self._range_periods(begin, end, self.max_period_transaction)
        for period in periods:
            data, received = self._request(
                method = requests.get,
                urn = self.URNs.transactions_by_contract_get,
                params = {'begin': period.get('begin').isoformat(), 'end': period.get('end').isoformat()})
            if received:
                transaction_list = data.get('OperationList')
                for data_transaction in transaction_list:
                    data_transaction_obj = self._convert_data_ws_transaction(data_transaction)
                    if not data_transaction_obj.type:
                        continue
                    result.append(data_transaction_obj)
            else:
                result = str(data)
                break
        return result, received

    def _request(self, method: requests.Request, urn: str, headers: Dict = None,
                 params: Dict = None, data: str = None) -> Tuple[Any, bool]:
        
        url = f'{self.url}{urn}'

        if headers:
            headers_ready = {**self.base_headers, **headers}
        else:
            headers_ready = self.base_headers.copy()

        if params:
            params_ready = {**self.base_params, **params}
        else:
            params_ready = self.base_params.copy()

        try:
            
            response = method(
                url,
                headers = headers_ready,
                params = params_ready,
                data = data,
                timeout = 30)
            
            response.raise_for_status()
            
            data_recieved = response.json()
            return data_recieved, True
        
        except requests.RequestException as e:
            message = f'Ошибка запроса к API сервиса РН-Карт: {str(e)}'
            logger.error(message)
            return message, False
        except json.JSONDecodeError as e:
            message = f'Ошибка разбора полученного текста JSON от сервиса РН-Карт: {str(e)}'
            logger.error(message)
            return message, False

    @classmethod
    def _convert_data_ws_item_category(cls, data_item: dict) -> str:
        category = cls._value_to_str(data_item.get('Cat'))
        category_code = cls._convert_data_ws_name_category(category, 'category')
        if category_code:
            return category_code
        else:
            message = f'_convert_data_ws_item_category(data_limit={data_item}):' + \
                f'It was not possible to compare the received category code "{category}"'
            logger.error(message)
            raise RequestAborted(message)

    @classmethod
    def _convert_data_ws_card_status(cls, data_card: dict) -> str:
        status = cls._value_to_str(data_card.get('SCode'))
        status_code = cls._convert_data_ws_name_card_status(status)
        if status_code:
            return status_code
        else:
            message = f'_convert_data_ws_card_status(data_card={data_card}):' + \
                f'It was not possible to compare the received card status "{status}"'
            logger.error(message)
            raise RequestAborted(message)

    @classmethod
    def _convert_data_ws_card_limits(cls, card_limits: dict) -> WSDataCardLimits:
        card_number = cls._value_to_str(card_limits.get('Card'))
        result = WSDataCardLimits(card_number=card_number)
        limits = card_limits.get('Limits', [])
        for data_limit in limits:
            limit_type = cls._convert_data_ws_limit_type(data_limit)
            result.limits.append(
                WSDataLimit(
                    card_number = card_number,
                    id_external = cls._value_to_str(data_limit.get('Code')),
                    type = limit_type,
                    period = cls._convert_data_ws_name_period(data_limit.get('Prd', '')),
                    item = cls._convert_data_ws_limit_item(data_limit, limit_type),
                    category = cls._convert_data_ws_limit_category(data_limit, limit_type),
                    unit = cls._convert_data_ws_limit_unit(data_limit),
                    value = cls._value_to_float(data_limit.get('Val')),
                    balance = cls._value_to_float(data_limit.get('CurValue'))
                )
            )
        return result

    @classmethod
    def _convert_data_ws_transaction(cls, data_transaction: dict) -> WSDataTransaction:
        tz=pytz.timezone('UTC')
        price = cls._value_to_float(data_transaction.get('Price', 0.00))
        price_discount = cls._value_to_float(data_transaction.get('DPrice', 0.00))
        amount = cls._value_to_float(data_transaction.get('Sum', 0.00))
        amount_discount = cls._value_to_float(data_transaction.get('DSum', 0.00))
        date_format = datetime.strptime(data_transaction.get('Date', ''), '%Y-%m-%dT%H:%M:%S')
        date_format = datetime(year=date_format.year, month=date_format.month, day=date_format.day,
                               hour=date_format.hour, minute=date_format.minute,
                               second=date_format.second, tzinfo=tz)
        return WSDataTransaction(
            id_external = cls._value_to_str(data_transaction.get('Code')),
            type = cls._convert_data_ws_name_transaction_type(data_transaction.get('Type', 0)),
            card_number = cls._value_to_str(data_transaction.get('Card')),
            date = date_format,
            amount = cls._value_to_float(data_transaction.get('Sum', 0.00)),
            discount = cls._value_to_float(data_transaction.get('DSum', 0.00)),
            details = cls._value_to_str(data_transaction.get('Address')),
            items = [WSDataTransactionItem(
                item = cls._value_to_str(data_transaction.get('GCode')),
                item_description = cls._value_to_str(data_transaction.get('DTL')),
                quantity = cls._value_to_float(data_transaction.get('Value', 0.00)),
                price = price,
                price_with_discount = price + price_discount,
                amount = amount,
                amount_with_discount = amount + amount_discount
            )]
        )

    @classmethod
    def _convert_data_ws_limit_type(cls, data_limit: dict) -> str:
        limit_type = cls._value_to_str(data_limit.get('GFlag'))
        limit_type_code = cls._convert_data_ws_name_limit_type(limit_type)
        if limit_type_code:
            return limit_type_code
        else:
            message = f'_convert_data_ws_limit_type(data_limit={data_limit}):' + \
                f'It was not possible to compare the received type limit "{limit_type}"'
            logger.error(message)
            raise RequestAborted(message)

    @classmethod
    def _convert_data_ws_limit_item(cls, data_limit: dict, limit_type: str) -> str:
        item = cls._value_to_str(data_limit.get('GCat'))
        return cls._convert_data_ws_name_item(item, limit_type)

    @classmethod
    def _convert_data_ws_limit_category(cls, data_limit: dict, limit_type: str) -> str:
        category = cls._value_to_str(data_limit.get('GCat'))
        return cls._convert_data_ws_name_category(category, limit_type)

    @classmethod
    def _convert_data_ws_limit_unit(cls, data_limit: dict) -> str:
        unit = cls._value_to_str(data_limit.get('Currency'))
        unit_code = cls._convert_data_ws_name_unit(unit)
        if unit_code:
            return unit_code
        else:
            message = f'_convert_data_ws_limit_unit(data_limit={data_limit}):' + \
                f'It was not possible to compare the received unit code "{unit}"'
            logger.error(message)
            raise RequestAborted(message)

    @classmethod
    def _convert_data_ws_name_limit_type(cls, value: str) -> str:
        match value.strip().lower():
            case 'g':
                result = 'item'
            case 'c':
                result = 'category'
            case _:
                result = 'all'
        return result

    @classmethod
    def _convert_data_ws_name_item(cls, value: str, limit_type: str) -> str:
        if limit_type == 'item':
            return value
        else:
            return ''

    @classmethod
    def _convert_data_ws_name_category(cls, value: str, limit_type: str) -> str:
        if limit_type == 'category':
            match value.strip().lower():
                case 'fuel':
                    result = 'fuel'
                case 'service':
                    result = 'service'
                case 'goods':
                    result = 'goods'
                case _:
                    result = ''
        else:
            result = ''
        return result

    @classmethod
    def _convert_data_ws_name_unit(cls, value: str) -> str:
        match value.strip().lower():
            case 'c':
                result = '383' #Рубль. Код по ОКЕИ
            case 'v':
                result = '112' #Литр. Код по ОКЕИ
            case _:
                result = ''
        return result

    @classmethod
    def _convert_data_ws_name_period(cls, value: str) -> str:
        match value.strip().lower():
            case 'n':
                result = 'nonrenewable'
            case 'f':
                result = 'day'
            case 'f7':
                result = 'week'
            case 'm':
                result = 'month'
            case 'q':
                result = 'quarter'
            case _:
                result = ''
        return result

    @classmethod
    def _convert_data_ws_name_card_status(cls, value: str) -> str:
        match value.strip().lower():
            case '00':
                result = 'active'
            case _:
                result = 'block'
        return result

    @classmethod
    def _convert_data_ws_name_transaction_type(cls, value: int) -> str:
        match value:
            case 11:
                result = 'sale'
            case 24:
                result = 'return'
            case _:
                result = ''
        return result

    @classmethod
    def _convert_limit_type_data_ws(cls, type: str) -> str:
        match type:
            case 'category':
                result = 'C'
            case 'item':
                result = 'G'
            case _:
                result = 'A'
        return result

    @classmethod
    def _convert_item_data_ws(cls, type: str, category: str, item: str) -> str:
        match type:
            case 'category':
                result = category.upper()
            case 'item':
                result = item
            case _:
                result = ''
        return result

    @classmethod
    def _convert_period_data_ws(cls, period: str) -> str:
        match period:
            case 'day':
                result = 'F'
            case 'week':
                result = 'F7'
            case 'month':
                result = 'M'
            case 'quarter':
                result = 'Q'
            case _:
                result = 'N'
        return result

    @classmethod
    def _convert_unit_data_ws(cls, unit: str) -> str:
        match unit:
            case '383':
                result = 'C'
            case _:
                result = 'V'
        return result

    @classmethod
    def _range_periods(cls, begin: datetime, end: datetime,
                       max_period: timedelta, tz: pytz.timezone = pytz.timezone('Europe/Moscow')) -> list[dict]:
        result = []
        now_date = datetime.now(tz=tz)
        begin_date = datetime(year=begin.year, month=begin.month, day=begin.day, tzinfo=tz)
        end_date = datetime(year=end.year, month=end.month, day=end.day, tzinfo=tz)
        if end_date > now_date:
            end_date = datetime(year=now_date.year, month=now_date.month, day=now_date.day, tzinfo=tz)
        while begin_date < end_date:
            current_period = {'begin': begin_date, 'end': None}
            begin_date += (max_period - timedelta(seconds=1))
            if begin_date > end_date:
                begin_date = end_date + timedelta(hours=23, minutes=59, seconds=59)
            current_period.update(end=begin_date)
            result.append(current_period)
            begin_date += timedelta(seconds=1)
        return result

    @classmethod
    def _value_to_float(cls, value: any) -> float:
        result = 0.00
        if isinstance(value, float):
            result = value
        elif isinstance(value, int):
            result = float(value)
        elif isinstance(value, str) and value.replace('.','', 1).isdigit():
            result = float(value)
        return result

    @classmethod
    def _value_to_str(cls, value: any) -> str:
        result = ''
        if isinstance(value, str):
            result = value
        elif isinstance(value, int):
            result = str(value)
        elif isinstance(value, float):
            result = str(value)
        return result

    @classmethod
    def _value_to_date(cls, value: any) -> datetime | None:
        result = None
        if isinstance(value, str):
            result = parser.parse(value)
        elif isinstance(value, datetime):
            result = value
        return result


def handler_limits_get_by_card_numbers(ws: WSSiteRosneft, data: list[str], processed_data: list, processed_success: bool):
    if not processed_success:
        return
    for card_number in data:
        data, processed_success = ws._request(
            method = requests.get,
            urn = ws.URNs.limits_by_contract_get,
            params = {
                'card': card_number,
                'flagLimits': 'Y',
                'flagGoodsRestrictions': 'N',
                'flagRegionRestrictions': 'N',
                'flagContract': 'N',
                'flagCard': 'Y'
            }
        )
        if processed_success:
            processed_data.extend(data)
        else:
            raise 'Failed to retrieve data from service RN-Cart using the handler_limits_get_by_card_numbers function'
