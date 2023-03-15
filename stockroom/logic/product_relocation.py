from stockroom.models import Client, Product, StockRoom, ClientProduct


class OutOfStock(Exception):
	pass


class ProductRelocation:
	def client_to_client(self, from_client: Client, to_client: Client, product: Product, amount: int):
		from_client_product = from_client.client_products.filter(product=product).first()

		if not from_client_product or from_client_product.amount < amount:
			raise OutOfStock(f'Перемещение невозможно, нет нужного количества у отправителя')

		from_client_product.amount -= amount

		if from_client_product.amount == 0:
			from_client_product.delete()
		else:
			from_client_product.save()

		to_client_product = to_client.client_products.filter(product=product).first()
		if to_client_product:
			to_client_product.amount += amount
			to_client_product.save()
		else:
			ClientProduct.objects.create(client=to_client, product=product, amount=amount)

	def stock_room_to_client(self, from_stock_room: StockRoom, to_client: Client, product: Product, amount):
		from_stock_room_product = to_client.stock_room_basket_position.filter(
			stock_room_basket__stock_room=from_stock_room, product=product
		).first()

		if not from_stock_room_product or from_stock_room_product.amount < amount:
			raise OutOfStock(f'Перемещение невозможно, нет нужного количества у отправителя')

		from_stock_room_product.amount -= amount

		if from_stock_room_product.amount == 0:
			from_stock_room_product.delete()
		else:
			from_stock_room_product.save()

		to_client_product = to_client.client_products.filter(product=product).first()
		if to_client_product:
			to_client_product.amount += amount
			to_client_product.save()
		else:
			ClientProduct.objects.create(client=to_client, product=product, amount=amount)
