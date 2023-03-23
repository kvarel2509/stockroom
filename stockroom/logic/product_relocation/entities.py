from stockroom import models
from stockroom.logic.product_relocation.domain import MoveRequest

from dataclasses import dataclass

from django.contrib.contenttypes.models import ContentType


@dataclass
class MoveRequestData:
	target_pk: int
	target_content_type: int
	product_batch_pk: int
	amount: int

	def get_object(self):
		target_type = ContentType.objects.get_for_id(self.target_content_type)
		target = target_type.get_object_for_this_type(pk=self.target_pk)
		product_batch = models.ProductBatch.objects.get(pk=self.product_batch_pk)

		return MoveRequest(target, product_batch, self.amount)
