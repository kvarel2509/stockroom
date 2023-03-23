from stockroom.logic.product_relocation.domain import CheckRelocateBehavior, MoveRequest
from stockroom.logic.product_relocation.exceptions import (
	NotEnoughProduct,
	LimitIsExceeded,
	BasketDoesNotSupportThisProduct,
	TargetIsHolder
)


class CheckTargetIsHolder(CheckRelocateBehavior):
	"""Цель перемещения должна отличаться от текущего держателя"""

	def check_relocate(self, move_request: MoveRequest) -> None:
		if all([
			isinstance(move_request.product_batch.holder, type(move_request.target)),
			move_request.product_batch.holder.pk == move_request.target.pk
		]):
			raise TargetIsHolder()


class CheckEnoughProductToRelocate(CheckRelocateBehavior):
	"""У держателя должно быть достаточное количество продукции для перемещения"""

	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.product_batch.amount < move_request.amount:
			raise NotEnoughProduct()


class CheckStockRoomBasketSupportsProduct(CheckRelocateBehavior):
	"""Принимающий склад должен разрешать прием данного вида продукции"""

	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.product_batch.product.pk != move_request.target.product.pk:
			raise BasketDoesNotSupportThisProduct()


class CheckFitInStockRoomBasketLimit(CheckRelocateBehavior):
	"""Должны соблюдаться лимиты склада на количество хранимой конкретной продукции"""

	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.amount + move_request.target.employed_limit > move_request.target.limit:
			raise LimitIsExceeded()


class CheckFitInStockRoomLimit(CheckRelocateBehavior):
	"""Должны соблюдаться общие лимиты склада на количество хранимой продукции"""

	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.amount + move_request.target.stockroom.employed_limit > move_request.target.stockroom.limit:
			raise LimitIsExceeded()
