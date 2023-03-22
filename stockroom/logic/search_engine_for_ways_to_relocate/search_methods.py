from typing import Generator
from itertools import combinations

from django.db.models import F, OuterRef, Subquery, IntegerField, ExpressionWrapper
from django.db.models.functions import Least

from stockroom.constants import TRANSPORTATION_COST
from stockroom.logic.product_relocation.domain import MoveRequest
from stockroom.logic.search_engine_for_ways_to_relocate.domain import SearchMethod, SearchRequest, SearchResponse
from stockroom.models import StockRoomBasket, Road


class ShortWayClientToStockRoomSearchMethod(SearchMethod):
	"""Реализация алгоритма поиска наикратчайших путей размещения продукции на склад"""
	def search(self, search_request: SearchRequest) -> Generator:
		distance = Road.objects.filter(
			client=search_request.product_batch.holder,
			stock_room=OuterRef('stock_room')
		).order_by('distance').values('distance')[:1]
		targets = StockRoomBasket.objects.filter(product=search_request.product_batch.product)
		targets = targets.filter(limit__gt=0, stock_room__limit__gt=0)
		targets = targets.annotate(distance=Subquery(distance))
		targets = targets.filter(distance__isnull=False)
		targets = targets.annotate(
			available_limit=ExpressionWrapper(
				Least(F('limit') - F('employed_limit'), F('stock_room__limit')), output_field=IntegerField()
			),
			unit_transportation_costs=F('distance') * TRANSPORTATION_COST + F('tariff')
		)

		all_search_responses = set()
		length = 1
		while length <= len(targets):
			search_responses_by_curr_length = []
			for target_set in combinations(targets, length):
				total_limit = sum([target.available_limit for target in target_set])
				# Если доступного лимита на множестве складов хватает для размещения продукции, создаются
				# запросы на размещение. Приоритет по количеству продукции отдается более дешевым складам.
				if total_limit >= search_request.amount:
					sorted_target_set = sorted(target_set, key=lambda x: x.unit_transportation_costs, reverse=True)
					need_to_collect = search_request.amount
					total_coat = 0
					move_requests = set()
					while need_to_collect > 0:
						target = sorted_target_set.pop()
						move_request = MoveRequest(
							target=target,
							product_batch=search_request.product_batch,
							amount=min([target.available_limit, need_to_collect])
						)
						move_requests.add(move_request)
						need_to_collect -= move_request.amount
						total_coat += target.unit_transportation_costs * move_request.amount
					search_response = SearchResponse(
						move_requests=move_requests,
						coat=total_coat
					)
					if search_response not in all_search_responses:
						all_search_responses.add(search_response)
						search_responses_by_curr_length.append(search_response)
			# Все найденные перестановки складов возвращаются в порядке увеличения стоимости размещения
			for i in sorted(search_responses_by_curr_length, key=lambda x: x.coat):
				yield i
			length += 1


class CheapWayClientToStockRoomSearchMethod(SearchMethod):
	"""Реализация алгоритма поиска самого дешевого пути размещения продукции на склад"""
	def search(self, search_request: SearchRequest) -> Generator:
		distance = Road.objects.filter(
			client=search_request.product_batch.holder,
			stock_room=OuterRef('stock_room')
		).order_by('distance').values('distance')[:1]
		targets = StockRoomBasket.objects.filter(product=search_request.product_batch.product)
		targets = targets.filter(limit__gt=0, stock_room__limit__gt=0)
		targets = targets.annotate(distance=Subquery(distance))
		targets = targets.filter(distance__isnull=False)
		targets = targets.annotate(
			available_limit=ExpressionWrapper(
				Least(F('limit') - F('employed_limit'), F('stock_room__limit')), output_field=IntegerField()
			),
			unit_transportation_costs=F('distance') * TRANSPORTATION_COST + F('tariff')
		)
		targets = targets.order_by('unit_transportation_costs')

		need_to_collect = search_request.amount
		total_limit = sum([target.available_limit for target in targets])
		if total_limit > need_to_collect:
			move_requests = set()
			total_coat = 0
			for target in targets:
				move_request = MoveRequest(
					target=target,
					product_batch=search_request.product_batch,
					amount=min([target.available_limit, need_to_collect])
				)
				move_requests.add(move_request)
				need_to_collect -= move_request.amount
				total_coat += target.unit_transportation_costs * move_request.amount
				if need_to_collect == 0:
					break

			search_response = SearchResponse(
				move_requests=move_requests,
				coat=total_coat
			)
			yield search_response
