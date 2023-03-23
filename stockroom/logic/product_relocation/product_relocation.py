from stockroom.logic.product_relocation.domain import MoveRequest, RelocateBehavior
from stockroom.models import ProductBatch

from django.contrib.contenttypes.models import ContentType


class ChangeProductBatchGiveAway(RelocateBehavior):
	"""Внесение изменений в product_batch при снятии с хранения"""

	def relocate(self, move_request: MoveRequest) -> None:
		product_batch = ProductBatch(
			product=move_request.product_batch.product,
			amount=move_request.amount,
			own=move_request.product_batch.own,
			holder=move_request.product_batch.holder
		)
		move_request.product_batch.amount -= move_request.amount

		if move_request.product_batch.amount == 0:
			move_request.product_batch.delete()
		else:
			move_request.product_batch.save()

		move_request.product_batch = product_batch


class ProductBatchTakes(RelocateBehavior):
	"""Внесение изменений в product_batch при размещении продукции"""

	def relocate(self, move_request: MoveRequest) -> None:
		own_type = ContentType.objects.get_for_model(move_request.product_batch.own.__class__)
		own_id = move_request.product_batch.own.id
		product_batch = move_request.target.holder_product_batches.filter(
			content_type_own=own_type, object_id_own=own_id, product=move_request.product_batch.product
		).first()

		if product_batch:
			product_batch.amount += move_request.amount
			product_batch.save()
		else:
			move_request.product_batch.holder = move_request.target
			move_request.product_batch.save()


class ChangeStockRoomBasketLimitGiveAway(RelocateBehavior):
	"""Внесение изменений в лимиты склада на конкретную продукцию при снятии с хранения"""

	def relocate(self, move_request: MoveRequest) -> None:
		move_request.product_batch.holder.employed_limit -= move_request.amount
		move_request.product_batch.holder.save()


class ChangeStockRoomLimitGiveAway(RelocateBehavior):
	"""Внесение изменений в общие лимиты склада при снятии с хранения"""

	def relocate(self, move_request: MoveRequest) -> None:
		move_request.product_batch.holder.stockroom.employed_limit -= move_request.amount
		move_request.product_batch.holder.stockroom.save()


class ChangeStockRoomBasketLimitTakes(RelocateBehavior):
	"""Внесение изменений в лимиты склада на конкретную продукцию при размещении продукции"""

	def relocate(self, move_request: MoveRequest) -> None:
		move_request.target.employed_limit += move_request.amount
		move_request.target.save()


class ChangeStockRoomLimitTakes(RelocateBehavior):
	"""Внесение изменений в общие лимиты склада при размещении продукции"""

	def relocate(self, move_request: MoveRequest) -> None:
		move_request.target.stockroom.employed_limit += move_request.amount
		move_request.product_batch.holder.stockroom.save()
