from stockroom.logic.product_relocation.domain import CheckRelocateBehavior, MoveRequest
from stockroom.logic.product_relocation.exceptions import IsNotHolder, NotEnoughProduct, LimitIsExceeded, \
	BasketDoesNotSupportThisProduct


class CheckProductBatchHolderIsFromEntity(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.product_batch.holder is not move_request.from_entity:
			raise IsNotHolder()


class CheckEnoughProductToRelocate(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.product_batch.amount < move_request.amount:
			raise NotEnoughProduct()


class CheckStockRoomBasketSupportsProduct(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.product_batch.product is not move_request.to_entity.product:
			raise BasketDoesNotSupportThisProduct()


class CheckFitInStockRoomBasketLimit(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.amount + move_request.to_entity.employed_limit > move_request.to_entity.limit:
			raise LimitIsExceeded()


class CheckFitInStockRoomLimit(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.amount + move_request.to_entity.stock_room.employed_limit > move_request.to_entity.stock_room.limit:
			raise LimitIsExceeded()
