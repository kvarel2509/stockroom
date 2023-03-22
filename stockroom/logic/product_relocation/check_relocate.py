from stockroom.logic.product_relocation.domain import CheckRelocateBehavior, MoveRequest
from stockroom.logic.product_relocation.exceptions import NotEnoughProduct, LimitIsExceeded, \
	BasketDoesNotSupportThisProduct, TargetIsHolder


class CheckTargetIsHolder(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.product_batch.holder is move_request.target:
			raise TargetIsHolder()


class CheckEnoughProductToRelocate(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.product_batch.amount < move_request.amount:
			raise NotEnoughProduct()


class CheckStockRoomBasketSupportsProduct(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.product_batch.product is not move_request.target.product:
			raise BasketDoesNotSupportThisProduct()


class CheckFitInStockRoomBasketLimit(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.amount + move_request.target.employed_limit > move_request.target.limit:
			raise LimitIsExceeded()


class CheckFitInStockRoomLimit(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.amount + move_request.target.stock_room.employed_limit > move_request.target.stock_room.limit:
			raise LimitIsExceeded()
