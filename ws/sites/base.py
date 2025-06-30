
from datetime import datetime
from typing import Tuple, List
from django.db import transaction

from .common import (
    WSDataSiteBalance,
    WSDataCard,
    WSDataItem,
    WSDataCardLimits,
    WSDataLimit,
    WSDataTransaction,
    WSDataTransactionItem)

from cards.models import(
    EnumItemCategory,
    EnumCardStatus,
    EnumLimitType,
    EnumLimitPeriod,
    EnumTransactionType,
    Site,
    SiteBalance,
    Item,
    Card,
    Limit,
    Transaction,
    TransactionItem)

class WSSiteBase:

    def __init__(self, site: Site):
        self.site = site
        self.url = site.url
        self.login = site.login
        self.password = site.password
        self.contract_id = site.contract_id
        self.base_headers = {}
        self.base_params = {}

    @transaction.atomic
    def balance_get(self) -> Tuple[SiteBalance | str, bool]:
        data, success = self.balance_get_ws()
        if success:
            result = self._balance_update_or_create(data)
        else:
            result = data
        return result, success

    @transaction.atomic
    def items_get(self) -> Tuple[list[Item], bool]:
        result = []
        data, success = self.items_get_ws()
        if success:
            for data_item in data:
                result.append(self._item_update_or_create(data_item))
        else:
            result = data
        return result, success

    @transaction.atomic
    def cards_get(self) -> Tuple[list[Card] | str, bool]:
        result = []
        relevant_card_numbers = [card_obj.number for card_obj in Card.objects.filter(site=self.site, relevant=True)]

        data, success = self.cards_get_ws()

        if success:
            for data_card in data:
                card_obj = self._card_update_or_create(data_card)
                if data_card.number in relevant_card_numbers:
                    relevant_card_numbers.remove(data_card.number)
                result.append(card_obj)
            for number in relevant_card_numbers:
                Card.objects.filter(site=self.site, number=number).update(relevant = False)
        else:
            result = data

        return result, success
    
    @transaction.atomic
    def card_status_update(self, card_number: str, status: str) -> Tuple[Card | str, bool]:
        result = ''
        data, success = self.card_status_update_ws(card_number, status)
        if success:
            result = Card.objects.update_or_create(
                site = self.site,
                number=card_number,
                defaults={'status': EnumCardStatus.objects.get(code_str=status)})[0]
        else:
            result = data
        return result, success

    @transaction.atomic
    def limits_get(self, cards: List[Card] = None) -> Tuple[list[Limit] | str, bool]:
        
        result = []
        
        if cards:
            card_numbers = [card_obj.number for card_obj in cards]
            data, success = self.limits_get_ws(card_numbers = card_numbers)
        else:
            data, success = self.limits_get_ws()
        
        if success:

            for card_limits in data:
                card_obj = self._find_or_create_card(self.site, card_limits.card_number)
                if not card_obj:
                    continue
                
                limits_not_deleted = Limit.objects.filter(card=card_obj, deleted=False)
                for limit_by_card in limits_not_deleted:
                    deleted = True
                    for data_limit in card_limits.limits:
                        if limit_by_card.id_external == data_limit.id_external:
                            deleted = False
                            break
                    if deleted:
                        limit_by_card.deleted = True
                        limit_by_card.save()

                for data_limit in card_limits.limits:
                    limit_obj = self._limit_update_or_create(card_obj, data_limit)
                    result.append(limit_obj)
        else:
            result = data

        return result, success

    @transaction.atomic
    def limit_add(self, data_limit: WSDataLimit) -> Tuple[Limit | str, bool]:
        result = ''
        data, success = self.limit_add_ws(data_limit)
        if success:
            match data_limit.type:
                case 'category':
                    category_obj = EnumItemCategory.objects.get(code_str=data_limit.category)
                    item_obj = None
                case 'item':
                    category_obj = None
                    item_obj = Item.objects.get(site=self.site, id_external=data_limit.item)
                case _:
                    category_obj = None
                    item_obj = None
            result = Limit.objects.create(
                site = self.site,
                card = Card.objects.get(site=self.site, number=data_limit.card_number),
                id_external = data_limit.id_external,
                type = EnumLimitType.objects.get(code_str=data_limit.type),
                period = EnumLimitPeriod.objects.get(code_str=data_limit.period),
                category = category_obj,
                item = item_obj,
                unit = data_limit.unit,
                value = data_limit.value,
                deleted = False)
        else:
            result = data
        return result, success

    @transaction.atomic
    def limit_update(self, data_limit: WSDataLimit) -> Tuple[str, bool]:
        result = ''
        data, success = self.limit_update_ws(data_limit)
        if success:
            match data_limit.type:
                case 'category':
                    category_obj = EnumItemCategory.objects.get(code_str=data_limit.category)
                    item_obj = None
                case 'item':
                    category_obj = None
                    item_obj = Item.objects.get(site=self.site, id_external=data_limit.item)
                case _:
                    category_obj = None
                    item_obj = None
            queryset = Limit.objects.filter(
                site = self.site,
                card = Card.objects.get(site=self.site, number=data_limit.card_number),
                id_external = data_limit.id_external)
            queryset.update(
                type = EnumLimitType.objects.get(code_str=data_limit.type),
                period = EnumLimitPeriod.objects.get(code_str=data_limit.period),
                category = category_obj,
                item = item_obj,
                unit = data_limit.unit,
                value = data_limit.value_new,
                deleted = False)
            result = queryset[0]
        else:
            result = data
        return result, success

    @transaction.atomic
    def limit_delete(self, card_number: str, id_external: str) -> Tuple[str, bool]:
        result = ''
        data, success = self.limit_delete_ws(card_number, id_external)
        if success:
            Limit.objects.filter(
                site = self.site,
                card = Card.objects.get(site=self.site, number=card_number),
                id_external = id_external
            ).update(deleted = True)
        else:
            result = data
        return result, success

    @transaction.atomic
    def transactions_get(self, begin: datetime, end: datetime) -> Tuple[list[Transaction] | str, bool]:
        result = []
        data, success = self.transactions_get_ws(begin, end)
        if success:
            for data_transaction in data:
                transaction_obj = self._transaction_update_or_create(data_transaction)
                self._transaction_item_update_or_create(transaction_obj, data_transaction.items)
                result.append(transaction_obj)
        else:
            result = data
        return result, success

    def balance_get_ws(self) -> Tuple[WSDataSiteBalance | str, bool]:
        return 'Не корректное наследование класса сайта', False

    def items_get_ws(self) -> Tuple[list[WSDataItem] | str, bool]:
        return 'Не корректное наследование класса сайта', False

    def cards_get_ws(self) -> Tuple[list[WSDataCard] | str, bool]:
        return 'Не корректное наследование класса сайта', False

    def card_status_update_ws(self, card_number: str, status:str) -> Tuple[str, bool]:
        return 'Не корректное наследование класса сайта', False

    def limits_get_ws(self, card_numbers: List[str] = None) -> Tuple[list[WSDataCardLimits] | str, bool]:
        return 'Не корректное наследование класса сайта', False

    def limit_add_ws(self, data_limit: WSDataLimit) -> Tuple[str, bool]:
        return 'Не корректное наследование класса сайта', False

    def limit_update_ws(self, data_limit: WSDataLimit) -> Tuple[str, bool]:
        return 'Не корректное наследование класса сайта', False

    def limit_delete_ws(self, card_number: str, id_external: str) -> Tuple[str, bool]:
        return 'Не корректное наследование класса сайта', False

    def transactions_get_ws(self, begin: datetime, end: datetime) -> Tuple[list[WSDataTransaction] | str, bool]:
        return 'Не корректное наследование класса сайта', False

    def _balance_update_or_create(self, data_balance: WSDataSiteBalance) -> SiteBalance:
        queryset = SiteBalance.objects.filter(
            site = self.site,
            date = data_balance.date)

        if queryset.exists():
            queryset.update(
                balance = data_balance.balance,
                credit = data_balance.credit)
            return queryset[0]
        else:
            return SiteBalance.objects.create(
                site = self.site,
                date = data_balance.date,
                balance = data_balance.balance,
                credit = data_balance.credit)

    def _item_update_or_create(self, data_item: WSDataItem) -> Item:
        queryset = Item.objects.filter(
            site = self.site,
            id_external = data_item.id)

        if queryset.exists():
            queryset.update(
                category = EnumItemCategory.objects.get(code_str=data_item.category),
                name = data_item.name)
            return queryset[0]
        else:
            return Item.objects.create(
                site = self.site,
                id_external = data_item.id,
                category = EnumItemCategory.objects.get(code_str=data_item.category),
                name = data_item.name)

    def _card_update_or_create(self, data_card: WSDataCard) -> Card:
        queryset = Card.objects.filter(
            site = self.site,
            number = data_card.number)

        if queryset.exists():
            queryset.update(
                status = EnumCardStatus.objects.get(code_str=data_card.status),
                relevant = True)
            return queryset[0]
        else:
            return Card.objects.create(
                site = self.site,
                number = data_card.number,
                status = EnumCardStatus.objects.get(code_str=data_card.status),
                relevant = True)

    def _limit_update_or_create(self, card_obj: Card, data_limit: WSDataLimit) -> Limit:
        type_obj = EnumLimitType.objects.get(code_str=data_limit.type)
        period_obj = EnumLimitPeriod.objects.get(code_str=data_limit.period)

        match data_limit.type:
            case 'category':
                item_obj = None
                category_obj = EnumItemCategory.objects.get(code_str=data_limit.category)
            case 'item':
                item_obj = Item.objects.get(site=self.site, id_external=data_limit.item)
                category_obj = None
            case _:
                item_obj = None
                category_obj = None

        queryset = Limit.objects.filter(
            site = self.site,
            card = card_obj,
            id_external = data_limit.id_external)

        if queryset.exists():
            queryset.update(
                deleted = False,
                type = type_obj,
                item = item_obj,
                category = category_obj,
                period = period_obj,
                unit = data_limit.unit,
                value = data_limit.value,
                balance = data_limit.balance)
            return queryset[0]
        else:
            return Limit.objects.create(
                site=self.site,
                card = card_obj,
                id_external = data_limit.id_external,
                deleted = False,
                type = type_obj,
                item = item_obj,
                category = category_obj,
                period = period_obj,
                unit = data_limit.unit,
                value = data_limit.value,
                balance = data_limit.balance)

    def _transaction_update_or_create(self, data_transaction: WSDataTransaction) -> Transaction:

        type_obj = EnumTransactionType.objects.get(code_str=data_transaction.type)
        card_obj = Card.objects.get(site=self.site, number=data_transaction.card_number)

        queryset = Transaction.objects.filter(
            site = self.site,
            card = card_obj,
            id_external = data_transaction.id_external)

        if queryset.exists():
            queryset.update(
                type = type_obj,
                date = data_transaction.date,
                amount = data_transaction.amount,
                discount = data_transaction.discount,
                details = data_transaction.details)
            return queryset[0]
        else:
            return Transaction.objects.create(
                site = self.site,
                card = card_obj,
                id_external = data_transaction.id_external,
                type = type_obj,
                date = data_transaction.date,
                amount = data_transaction.amount,
                discount = data_transaction.discount,
                details = data_transaction.details)

    def _transaction_item_update_or_create(self, transaction_obj: Transaction, data_transaction_items: List[WSDataTransactionItem]) -> List[TransactionItem]:
        result = []
        TransactionItem.objects.filter(transaction=transaction_obj).delete()

        for data_transaction_item in data_transaction_items:

            if Item.objects.filter(site=self.site, id_external=data_transaction_item.item).exists():
                item_obj = Item.objects.get(site=self.site, id_external=data_transaction_item.item)
            else:
                item_obj = None

            result.append(TransactionItem.objects.create(
                transaction = transaction_obj,
                item = item_obj,
                item_description = data_transaction_item.item_description,
                quantity = data_transaction_item.quantity,
                price = data_transaction_item.price,
                price_with_discount = data_transaction_item.price_with_discount,
                amount = data_transaction_item.amount,
                amount_with_discount = data_transaction_item.amount_with_discount
            ))
        return result

    def _find_or_create_card(self, site: Site, card_number: str, relevant: bool = True) -> Card | None:
        if not card_number:
            return
        if Card.objects.filter(site=site, number=card_number).exists():
            result = Card.objects.get(site=self.site, number=card_number)
        else:
            status_obj = EnumCardStatus.objects.get(code_str='block')
            result = Card.objects.create(site=self.site, number = card_number,
                                         status = status_obj, relevant = relevant)
        return result
