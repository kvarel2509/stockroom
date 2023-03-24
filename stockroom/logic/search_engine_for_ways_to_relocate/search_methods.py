from stockroom.constants import TRANSPORTATION_COST
from stockroom.logic.product_relocation.domain import MoveRequest
from stockroom.logic.search_engine_for_ways_to_relocate.domain import SearchMethod, SearchRequest, SearchResponse
from stockroom.models import StockRoomBasket, Road

from django.db.models import F, OuterRef, Subquery, IntegerField, ExpressionWrapper
from django.db.models.functions import Least


class ShortWayClientToStockRoomSearchMethod(SearchMethod):
	"""Реализация алгоритма поиска наикратчайших путей размещения продукции на склад"""

	def search(self, search_request: SearchRequest) -> SearchResponse:
		distance = Road.objects.filter(
			client=search_request.product_batch.holder,
			stockroom=OuterRef('stockroom')
		).order_by('distance').values('distance')[:1]
		targets = StockRoomBasket.objects.filter(product=search_request.product_batch.product)
		targets = targets.filter(limit__gt=0, stockroom__limit__gt=0)
		targets = targets.annotate(distance=Subquery(distance))
		targets = targets.filter(distance__isnull=False)
		targets = targets.annotate(
			available_limit=ExpressionWrapper(
				Least(F('limit') - F('employed_limit'), F('stockroom__limit')), output_field=IntegerField()
			),
			unit_transportation_costs=F('distance') * TRANSPORTATION_COST + F('tariff')
		)
		targets = targets.order_by('-available_limit')

		combination_length = 1
		need_to_collect = search_request.amount
		while combination_length < len(targets):
			such_length_best_way = None
			such_length_best_coat = float('inf')
			target_combination = [None for _ in range(combination_length-1)]
			accumulated_limit = 0
			accumulated_coat = 0
			cursor = 0

			while cursor >= 0:
				if cursor == len(target_combination):
					for last_target_ind in range(target_combination[cursor-1] + 1 if cursor > 0 else 0, len(targets)):
						limit = accumulated_limit + targets[last_target_ind].available_limit
						if limit >= need_to_collect:
							coat = accumulated_coat + targets[last_target_ind].unit_transportation_costs * (need_to_collect - accumulated_limit)
							if coat < such_length_best_coat:
								such_length_best_way = target_combination + [last_target_ind]
								such_length_best_coat = coat
						else:
							break
					cursor -= 1
					if cursor >= 0:
						accumulated_limit -= targets[target_combination[cursor]].available_limit
						accumulated_coat -= targets[target_combination[cursor]].unit_transportation_costs * targets[target_combination[cursor]].available_limit
						target_combination[cursor] += 1
				else:
					if target_combination[cursor] is None:
						target_combination[cursor] = target_combination[cursor-1] + 1 if cursor > 0 else 0

					if accumulated_coat >= such_length_best_coat or target_combination[cursor] >= len(targets) - cursor:
						target_combination[cursor] = None
						cursor -= 1
						if cursor >= 0:
							accumulated_limit -= targets[target_combination[cursor]].available_limit
							accumulated_coat -= targets[target_combination[cursor]].unit_transportation_costs * targets[target_combination[cursor]].available_limit
							target_combination[cursor] += 1

					elif accumulated_limit + targets[target_combination[cursor]].available_limit < need_to_collect:
						accumulated_limit += targets[target_combination[cursor]].available_limit
						accumulated_coat += targets[target_combination[cursor]].unit_transportation_costs * targets[target_combination[cursor]].available_limit
						cursor += 1

			if such_length_best_way:
				move_requests = []

				for target_ind in such_length_best_way:
					move_request = MoveRequest(
						target=targets[target_ind],
						product_batch=search_request.product_batch,
						amount=min([targets[target_ind].available_limit, need_to_collect])
					)
					move_requests.append(move_request)
					need_to_collect -= move_request.amount
				return SearchResponse(move_requests=move_requests, coat=such_length_best_coat)
			combination_length += 1


class CheapWayClientToStockRoomSearchMethod(SearchMethod):
	"""Реализация алгоритма поиска самого дешевого пути размещения продукции на склад"""

	def search(self, search_request: SearchRequest) -> SearchResponse:
		distance = Road.objects.filter(
			client=search_request.product_batch.holder,
			stockroom=OuterRef('stockroom')
		).order_by('distance').values('distance')[:1]
		targets = StockRoomBasket.objects.filter(product=search_request.product_batch.product)
		targets = targets.filter(limit__gt=0, stockroom__limit__gt=0)
		targets = targets.annotate(distance=Subquery(distance))
		targets = targets.filter(distance__isnull=False)
		targets = targets.annotate(
			available_limit=ExpressionWrapper(
				Least(F('limit') - F('employed_limit'), F('stockroom__limit')), output_field=IntegerField()
			),
			unit_transportation_costs=F('distance') * TRANSPORTATION_COST + F('tariff')
		)
		targets = targets.order_by('unit_transportation_costs')

		need_to_collect = search_request.amount
		total_limit = sum([target.available_limit for target in targets])

		if total_limit > need_to_collect:
			move_requests = []
			total_coat = 0

			for target in targets:
				move_request = MoveRequest(
					target=target,
					product_batch=search_request.product_batch,
					amount=min([target.available_limit, need_to_collect])
				)
				move_requests.append(move_request)
				need_to_collect -= move_request.amount
				total_coat += target.unit_transportation_costs * move_request.amount

				if need_to_collect == 0:
					break

			search_response = SearchResponse(
				move_requests=move_requests,
				coat=total_coat
			)
			return search_response
