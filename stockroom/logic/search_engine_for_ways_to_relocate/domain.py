from stockroom.logic.product_relocation.domain import MoveRequest
from stockroom.models import ProductBatch

from typing import Generator, List


class SearchRequest:
	"""Сущность - запрос на поиск путей размещения"""

	def __init__(self, product_batch: ProductBatch, amount: int, method_alias: str) -> None:
		self.product_batch = product_batch
		self.amount = amount
		self.method_alias = method_alias


class SearchResponse:
	"""Сущность - результат поиска пути размещения"""

	def __init__(self, move_requests: List[MoveRequest], coat: float) -> None:
		self.move_requests = move_requests
		self.coat = coat

	def __len__(self) -> int:
		return len(self.move_requests)

	def __eq__(self, other) -> bool:
		return all([
			isinstance(self, type(other)),
			other.move_requests == self.move_requests,
			self.coat == other.coat,
		])


class SearchMethod:
	"""Базовый класс - Алгоритм поиска пути размещения"""

	def search(self, search_request: SearchRequest) -> Generator: ...


class SearchEngine:
	"""Контекст поиска путей размещения."""

	def __init__(self, search_request: SearchRequest, search_method: SearchMethod) -> None:
		self.search_request = search_request
		self.search_method = search_method

	def search(self) -> Generator:
		return self.search_method.search(self.search_request)


class SearchEngineFactory:
	"""Фабрика, порождающая контекст поиска путей размещения - экземпляр SearchEngine"""

	def __init__(self, search_request: SearchRequest) -> None:
		self.search_request = search_request

	def get_search_engine(self) -> SearchEngine: ...
