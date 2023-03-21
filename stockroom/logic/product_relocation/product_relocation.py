from django.contrib.contenttypes.models import ContentType

from stockroom.logic.product_relocation.domain import MoveRequest, RelocateBehavior
from stockroom.models import ProductBatch


class ChangeProductBatchGiveAway(RelocateBehavior):
	def relocate(self, move_request: MoveRequest) -> None:
		product_batch = ProductBatch(
			product=move_request.product_batch.product,
			amount=move_request.amount,
			own=move_request.product_batch.own
		)
		move_request.product_batch.amount -= move_request.amount
		
		if move_request.product_batch.amount == 0:
			move_request.product_batch.delete()
		else:
			move_request.product_batch.save()
		
		move_request.product_batch = product_batch


class ProductBatchTakes(RelocateBehavior):
	def relocate(self, move_request: MoveRequest) -> None:
		own_type = ContentType.objects.get_for_model(move_request.product_batch.own.__class__)
		own_id = move_request.product_batch.own.id
		product_batch = move_request.to_entity.holder_product_batches.filter(
			content_type_own=own_type, object_id_own=own_id, product=move_request.product_batch.product
		).first()
		if product_batch:
			product_batch.amount += move_request.amount
			product_batch.save()
		else:
			move_request.product_batch.holder = move_request.to_entity
			move_request.product_batch.save()


class ChangeStockRoomBasketLimitGiveAway(RelocateBehavior):
	def relocate(self, move_request: MoveRequest) -> None:
		move_request.from_entity.employed_limit -= move_request.amount
		move_request.from_entity.save()


class ChangeStockRoomLimitGiveAway(RelocateBehavior):
	def relocate(self, move_request: MoveRequest) -> None:
		move_request.from_entity.stock_room.employed_limit -= move_request.amount
		move_request.from_entity.stock_room.save()


class ChangeStockRoomBasketLimitTakes(RelocateBehavior):
	def relocate(self, move_request: MoveRequest) -> None:
		move_request.to_entity.employed_limit += move_request.amount
		move_request.to_entity.save()


class ChangeStockRoomLimitTakes(RelocateBehavior):
	def relocate(self, move_request: MoveRequest) -> None:
		move_request.to_entity.stock_room.employed_limit -= move_request.amount
		move_request.from_entity.stock_room.save()
