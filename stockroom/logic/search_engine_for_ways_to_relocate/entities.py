from stockroom import models
from stockroom.logic.search_engine_for_ways_to_relocate.domain import SearchRequest

from dataclasses import dataclass


@dataclass
class SearchRequestData:
	product_batch_pk: int
	amount: int
	method_alias: str
	options_count: int

	def get_object(self):
		product_batch = models.ProductBatch.objects.get(pk=self.product_batch_pk)
		return SearchRequest(product_batch, self.amount, self.method_alias)
