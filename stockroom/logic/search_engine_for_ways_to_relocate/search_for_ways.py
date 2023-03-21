from typing import Generator

from django.db.models import F, OuterRef, Subquery
from django.db.models.functions import Least

from stockroom.constants import TRANSPORTATION_COST
from stockroom.logic.product_relocation.domain import MoveRequest
from stockroom.logic.search_engine_for_ways_to_relocate.domain import SearchMethod, SearchRequestList
from stockroom.models import StockRoomBasket, Road


class ShortWayClientToStockRoomOneProductSearchMethod(SearchMethod):
	def search(self, search_request_list: SearchRequestList) -> Generator[MoveRequest]:
		search_request = search_request_list[0]
		distance = Road.objects.filter(
			client=search_request.product_batch.holder,
			stock_room=OuterRef('stock_room')
		)
		targets = StockRoomBasket.objects.filter(
			product=search_request.product_batch.product
		).filter(
			limit__gt=0, stock_room__limit__gt=0
		).annotate(
			available_limit=Least((F('limit') - F('employed_limit'), F('stock_room__limit'))),
			unit_transportation_costs=Subquery(distance.values('distance')[:1]) * TRANSPORTATION_COST
		)
		print(targets)

