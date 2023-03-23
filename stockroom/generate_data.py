import random
import itertools
from stockroom import models


def generate_data(product_count, stockroom_count, client_count):
	products = models.Product.objects.bulk_create([models.Product(name=f'P{i}') for i in range(product_count)])
	clients = models.Client.objects.bulk_create([models.Client(name=f'C{i}') for i in range(client_count)])
	stockrooms = models.StockRoom.objects.bulk_create(
		[models.StockRoom(name=f'SR{i}', limit=random.randint(10, 100)) for i in range(stockroom_count)]
	)

	for stockroom in stockrooms:
		stockroom_basket_count = random.randint(0, product_count)
		products_for_stockroom_basket = random.sample(products, stockroom_basket_count)
		models.StockRoomBasket.objects.bulk_create([models.StockRoomBasket(
			stockroom=stockroom,
			product=product,
			limit=random.randint(10, 100),
			tariff=random.randint(1, 10)
		) for product in products_for_stockroom_basket])

	models.Road.objects.bulk_create([models.Road(
		client=client,
		stockroom=stockroom,
		distance=random.randint(100, 1000)
	) for client, stockroom in itertools.product([clients, stockrooms])])

	for client in clients:
		product_batch_count = random.randint(0, product_count)
		products_for_client = random.sample(products, product_batch_count)
		client.holder_product_batches.set([models.ProductBatch(
			product=product,
			amount=random.randint(10, 50),
			own=client
		) for product in products_for_client])
