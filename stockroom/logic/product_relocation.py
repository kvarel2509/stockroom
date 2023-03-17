from stockroom.models import Client, Product, StockRoom
from functools import cached_property


class OutOfStock(Exception):
	pass


class MoveRequest:
	def __init__(self, from_entity, to_entity, product_batch, amount):
		self.from_entity = from_entity
		self.to_entity = to_entity
		self.product_batch = product_batch
		self.amount = amount


class RelocationBehavior:
	def __init__(self, move_request: MoveRequest):
		self.move_request = move_request

	def perform(self):
		if self.can_perform():
			self.process()
		else:
			self.failure()

	def can_perform(self): ...

	def process(self): ...

	def failure(self): ...


class GivesAwayBehavior(RelocationBehavior):
	def process(self):
		self.move_request.product_batch.amount -= self.move_request.amount
		if self.move_request.product_batch.amount == 0:
			self.move_request.product_batch.delete()
		else:
			self.move_request.product_batch.save()

	def can_perform(self):
		return all([
			self.move_request.product_batch.holder is self.move_request.from_entity,
			self.move_request.product_batch.amount >= self.move_request.amount
		])

	def failure(self):
		raise OutOfStock('Перемещение невозможно. У отправителя нет нужного количества товара.')


class ClientTakeBehavior(RelocationBehavior):
	def process(self):
		product_batches = self.
		if self.client_product:
			self.client_product.amount += self.move_request_form.amount
			self.client_product.save()
		else:
			ClientProduct.objects.create(
				client=self.move_request_form.to_entity,
				product=self.move_request_form.product,
				amount=self.move_request_form.amount
			)

	def can_perform(self):
		return True


class StockRoomBasketTakesBehavior(RelocationBehavior):
	def perform(self):
		stock_room_basket_position = self.move_request_form.to_entity.stock_room_basket_positions.filter(
			client=self.move_request_form.from_entity
		).first()
		if stock_room_basket_position:
			stock_room_basket_position.amount += self.move_request_form.amount
			stock_room_basket_position.save()
		else:
			StockRoomBasketPosition.objects.create(
				stock_room_basket=self.move_request_form.to_entity,
				client=self.move_request_form.from_entity,
				amount=self.move_request_form.amount
			)

	def can_perform(self):
		return self.check_stock_room_basket_limit() and self.check_stock_room_limit()

	def check_stock_room_basket_limit(self):
		current_occupancy = sum(
			self.move_request_form.to_entity.stock_room_basket_positions.values_list('amount', flat=True)
		)
		return self.move_request_form.amount + current_occupancy <= self.move_request_form.to_entity.limit

	def check_stock_room_limit(self):
		current_occupancy = sum(
			StockRoomBasketPosition.objects.filter(
				stock_room_basket__stock_room=self.move_request_form.to_entity.stock_room,
			).values_list('amount', flat=True)
		)
		return self.move_request_form.amount + current_occupancy <= self.move_request_form.to_entity.stock_room.limit
