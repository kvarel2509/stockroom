from stockroom.logic.product_relocation.exceptions import (
	NotEnoughProduct,
	TargetIsHolder,
	LimitIsExceeded,
	BasketDoesNotSupportThisProduct
)
from stockroom.logic.product_relocation.factory import BaseRelocateManagerFactory
from stockroom.logic.product_relocation.entities import MoveRequestData
from stockroom.logic.search_engine_for_ways_to_relocate.factory import BaseSearchEngineFactory
from stockroom.logic.search_engine_for_ways_to_relocate.entities import SearchRequestData
from stockroom.logic.queries.read import BrokerDB

from typing import Sequence, Literal
from dataclasses import dataclass

from django.db import transaction


@dataclass
class Response:
	"""Шаблон ответа блока логики"""
	data: dict
	status: Literal['ok', 'error']


def product_relocate(move_request_data_list: Sequence[MoveRequestData]):
	"""эндпоинт для выполнения перемещения продукции"""
	try:
		with transaction.atomic():
			for move_request_data in move_request_data_list:
				move_request = move_request_data.get_object()
				factory = BaseRelocateManagerFactory(move_request)
				relocate_manager = factory.get_relocate_manager()
				relocate_manager.relocate()
		return Response(data={'msg': 'Операция выполнена успешно'}, status='ok')
	except (TargetIsHolder, NotEnoughProduct, LimitIsExceeded, BasketDoesNotSupportThisProduct):
		return Response(data={'msg': 'Операция не выполнена, произошла ошибка'}, status='error')


def find_way_for_relocate(search_request_data: SearchRequestData):
	"""эндпоинт для выполнения поиска вариантов перемещения"""
	search_request = search_request_data.get_object()
	factory = BaseSearchEngineFactory(search_request)
	search_engine = factory.get_search_engine()
	search_response = search_engine.search()
	return Response(data={'search_response': search_response}, status='ok')


def get_client_list():
	client_list = BrokerDB.get_client_list()
	return Response(data={'clients': client_list}, status='ok')


def get_client(client_pk):
	client = BrokerDB.get_client(client_pk)
	return Response(data={'client': client}, status='ok')


def get_client_holder_product_batches(client_pk):
	product_batch_list = BrokerDB.get_client_holder_product_batches_by_pk(client_pk)
	return Response(data={'product_batches': product_batch_list}, status='ok')


def get_available_stockroom_baskets_for_relocate_product_batch(product_batch_pk):
	product_batch = BrokerDB.get_product_batch(product_batch_pk)
	product = product_batch.product
	stockroom_baskets = BrokerDB.get_available_stockroom_baskets_for_relocate_product(product)
	return Response(data={'stockroom_baskets': stockroom_baskets}, status='ok')


