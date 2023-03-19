class CheckProductBatchHolderIsFromEntity(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.product_batch.holder is not self.move_request.from_entity:
			raise IsNotHolder()


class CheckEnoughProductToRelocate(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		if move_request.product_batch.amount < move_request.amount:
			raise NotEnoughProduct()


class CheckFitInStockRoomBasketLimit(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		current_occupancy = sum(
			move_request.to_entity.stock_room_basket_positions.values_list('amount', flat=True)
		)
		if move_request.amount + current_occupancy > move_request.to_entity.limit:
			raise LimitIsExceeded()


class CheckFitInStockRoomLimit(CheckRelocateBehavior):
	def check_relocate(self, move_request: MoveRequest) -> None:
		pass
		# current_occupancy = sum(
		# 	StockRoomBasketPosition.objects.filter(
		# 		stock_room_basket__stock_room=self.move_request_form.to_entity.stock_room,
		# 	).values_list('amount', flat=True)
		# )
		# return self.move_request_form.amount + current_occupancy <= self.move_request_form.to_entity.stock_room.limit
