from stockroom.logic.product_relocation.domain import CheckRelocateBehavior, MoveRequest
from stockroom.logic.product_relocation.exceptions import IsNotHolder, NotEnoughProduct, LimitIsExceeded
from stockroom.models import ProductBatch


class CheckProductBatchHolderIsFromEntity(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.product_batch.holder is not move_request.from_entity:
			raise IsNotHolder()


class CheckEnoughProductToRelocate(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.product_batch.amount < move_request.amount:
			raise NotEnoughProduct()


class CheckFitInStockRoomBasketLimit(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		current_occupancy = sum(
			move_request.to_entity.holder_product_batches.values_list('amount', flat=True)
		)
		if move_request.amount + current_occupancy > move_request.to_entity.limit:
			raise LimitIsExceeded()


class CheckFitInStockRoomLimit(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		current_occupancy = sum(
			ProductBatch.objects.filter(
				own_object__stock_room=move_request.to_entity.stock_room
			).values_list('amount', flat=True)
		)
		if move_request.amount + current_occupancy > move_request.to_entity.stock_room.limit:
			raise LimitIsExceeded()
