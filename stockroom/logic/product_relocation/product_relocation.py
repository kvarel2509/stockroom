from stockroom.logic.product_relocation.domain import MoveRequest, RelocateBehavior
from stockroom.models import ProductBatch


class GiveAwayRelocateBehavior(RelocateBehavior):
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


class TakesRelocateBehavior(RelocateBehavior):
	def relocate(self, move_request: MoveRequest) -> None:
		product_batch = move_request.to_entity.product_batches.filter(
			own_obj=move_request.product_batch.own, product=move_request.product_batch.product
		)
		if product_batch:
			product_batch.amount += move_request.amount
			product_batch.save()
		else:
			move_request.product_batch.holder = move_request.to_entity
			move_request.product_batch.save()
