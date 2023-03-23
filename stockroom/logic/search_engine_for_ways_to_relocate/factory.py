from stockroom.constants import SearchWayRelocationAlias
from stockroom.logic.search_engine_for_ways_to_relocate.domain import SearchEngineFactory, SearchEngine
from stockroom.logic.search_engine_for_ways_to_relocate.search_methods import (
	CheapWayClientToStockRoomSearchMethod,
	ShortWayClientToStockRoomSearchMethod
)


class BaseSearchEngineFactory(SearchEngineFactory):
	"""Реализация фабрики, представляющей контекст для поиска путей размещения"""

	def get_search_engine(self) -> SearchEngine:
		if self.search_request.method_alias == SearchWayRelocationAlias.CHEAP_WAY.value:
			return SearchEngine(
				search_request=self.search_request,
				search_method=CheapWayClientToStockRoomSearchMethod()
			)
		elif self.search_request.method_alias == SearchWayRelocationAlias.SHORT_WAY.value:
			return SearchEngine(
				search_request=self.search_request,
				search_method=ShortWayClientToStockRoomSearchMethod()
			)
		else:
			raise NotImplementedError()
