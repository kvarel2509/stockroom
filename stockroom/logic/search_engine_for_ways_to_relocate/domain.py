from typing import Sequence, Generator

from stockroom.logic.product_relocation.domain import MoveRequest


class SearchRequest:
	def __init__(self, product_batch, amount) -> None:
		self.product_batch = product_batch
		self.amount = amount


class SearchRequestList:
	def __init__(self, search_request_list: Sequence[SearchRequest]) -> None:
		self.search_request_list = search_request_list

	def __iter__(self):
		return (i for i in self.search_request_list)

	def __len__(self):
		return len(self.search_request_list)

	def __getitem__(self, item):
		return self.search_request_list[item]


class SearchMethod:
	def search(self, search_request_list: SearchRequestList) -> Generator[MoveRequest]: ...


class SearchEngine:
	def __init__(self, search_request_list: SearchRequestList, search_method: SearchMethod):
		self.search_request_list = search_request_list
		self.search_method = search_method

	def search(self) -> Generator[MoveRequest]:
		return self.search_method.search(self.search_request_list)

