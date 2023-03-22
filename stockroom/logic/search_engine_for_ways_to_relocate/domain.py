from typing import Generator, Set

from stockroom.logic.product_relocation.domain import MoveRequest
from stockroom.models import ProductBatch


class SearchRequest:
	def __init__(self, product_batch: ProductBatch, amount: int) -> None:
		self.product_batch = product_batch
		self.amount = amount


class SearchResponse:
	def __init__(self, move_requests: Set[MoveRequest], coat: float) -> None:
		self.move_requests = move_requests
		self.coat = coat

	def __len__(self) -> int:
		return len(self.move_requests)

	def __eq__(self, other) -> bool:
		return type(other) == type(self) and other.move_requests == self.move_requests and self.coat == other.coat

	def __hash__(self):
		return sum([hash(mr) for mr in self.move_requests]) + hash(self.coat)


class SearchMethod:
	def search(self, search_request: SearchRequest) -> Generator: ...


class SearchEngine:
	def __init__(self, search_request: SearchRequest, search_method: SearchMethod) -> None:
		self.search_request = search_request
		self.search_method = search_method

	def search(self) -> Generator:
		return self.search_method.search(self.search_request)


class SearchEngineFactory:
	def __init__(self, search_request: SearchRequest, method_alias: str) -> None:
		self.search_request = search_request
		self.method_alias = method_alias

	def get_search_engine(self) -> SearchEngine: ...
