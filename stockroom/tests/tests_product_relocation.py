from django.test import TestCase

from stockroom import models
from stockroom.logic.product_relocation.domain import MoveRequest
from stockroom.logic.product_relocation.exceptions import NotEnoughProduct, TargetIsHolder
from stockroom.logic.product_relocation.factory import BaseRelocateManagerFactory
from stockroom.logic.search_engine_for_ways_to_relocate.domain import SearchRequest
from stockroom.logic.search_engine_for_ways_to_relocate.search_methods import \
	ShortWayClientToStockRoomSearchMethod, CheapWayClientToStockRoomSearchMethod
from stockroom.models import Road


class ProductRelocateTests(TestCase):
	def setUp(self) -> None:
		self.client1 = models.Client.objects.create(name='Иван')
		self.client2 = models.Client.objects.create(name='Петр')

		self.product1 = models.Product.objects.create(name='Продукт')
		self.product2 = models.Product.objects.create(name='Продукт2')
		self.product3 = models.Product.objects.create(name='Продукт3')

		self.stock_room1 = models.StockRoom.objects.create(name='Склад1', limit=10)
		self.stock_room2 = models.StockRoom.objects.create(name='Склад2', limit=15)
		self.stock_room3 = models.StockRoom.objects.create(name='Склад3', limit=15)

		Road.objects.create(stock_room=self.stock_room1, client=self.client1, distance=600)
		Road.objects.create(stock_room=self.stock_room2, client=self.client1, distance=600)
		Road.objects.create(stock_room=self.stock_room3, client=self.client1, distance=600)

		self.stock_room1_basket1 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room1, product=self.product1, limit=5, tariff=2
		)
		self.stock_room1_basket2 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room1, product=self.product2, limit=15, tariff=2
		)

		self.stock_room1_basket3 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room2, product=self.product1, limit=4, tariff=2
		)
		self.stock_room1_basket4 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room2, product=self.product3, limit=20, tariff=2
		)

		self.stock_room1_basket5 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room3, product=self.product1, limit=5, tariff=1
		)

		self.product_batch1 = models.ProductBatch.objects.create(product=self.product1, amount=10, own=self.client1, holder=self.client1)
		self.product_batch2 = models.ProductBatch.objects.create(product=self.product2, amount=5, own=self.client1, holder=self.client1)
		self.product_batch3 = models.ProductBatch.objects.create(product=self.product3, amount=100, own=self.client1, holder=self.client1)
		self.product_batch4 = models.ProductBatch.objects.create(product=self.product3, amount=100, own=self.client1, holder=self.client2)

	def test_client_to_client_relocation(self):
		move_request1 = MoveRequest(
			target=self.client2,
			product_batch=self.product_batch1,
			amount=5
		)
		move_request2 = MoveRequest(
			target=self.client1,
			product_batch=self.product_batch1,
			amount=5
		)
		move_request3 = MoveRequest(
			target=self.client2,
			product_batch=self.product_batch1,
			amount=1000
		)
		move_request4 = MoveRequest(
			target=self.client2,
			product_batch=self.product_batch1,
			amount=5
		)

		factory1 = BaseRelocateManagerFactory(move_request1)
		factory2 = BaseRelocateManagerFactory(move_request2)
		factory3 = BaseRelocateManagerFactory(move_request3)
		factory4 = BaseRelocateManagerFactory(move_request4)

		relocate_manager1 = factory1.get_relocate_manager()
		relocate_manager2 = factory2.get_relocate_manager()
		relocate_manager3 = factory3.get_relocate_manager()
		relocate_manager4 = factory4.get_relocate_manager()

		with self.assertRaises(TargetIsHolder):
			relocate_manager2.relocate()

		with self.assertRaises(NotEnoughProduct):
			relocate_manager3.relocate()

		relocate_manager1.relocate()
		client1_product_batch_now = self.client1.holder_product_batches.filter(product=self.product1).first()
		client2_product_batch_now = self.client2.holder_product_batches.filter(product=self.product1).first()
		self.assertEqual(client1_product_batch_now.amount, 5)
		self.assertEqual(client2_product_batch_now.amount, 5)
		relocate_manager4.relocate()
		client1_product_batch_now = self.client1.holder_product_batches.filter(product=self.product1).first()
		client2_product_batch_now = self.client2.holder_product_batches.filter(product=self.product1).first()
		self.assertEqual(client1_product_batch_now, None)
		self.assertEqual(client2_product_batch_now.amount, 10)

	def test_client_to_stock_room_relocation(self):
		move_request1 = MoveRequest(
			target=self.stock_room1_basket1,
			product_batch=self.product_batch1,
			amount=1
		)
		move_request2 = MoveRequest(
			target=self.stock_room1_basket1,
			product_batch=self.product_batch2,
			amount=2
		)
		move_request3 = MoveRequest(
			target=self.stock_room1_basket1,
			product_batch=self.product_batch1,
			amount=6
		)
		move_request4 = MoveRequest(
			target=self.stock_room1_basket2,
			product_batch=self.product_batch2,
			amount=12
		)
		move_request5 = MoveRequest(
			target=self.stock_room1_basket1,
			product_batch=self.product_batch1,
			amount=4
		)

		factory1 = BaseRelocateManagerFactory(move_request1)
		factory2 = BaseRelocateManagerFactory(move_request2)
		factory3 = BaseRelocateManagerFactory(move_request3)
		factory4 = BaseRelocateManagerFactory(move_request4)
		factory5 = BaseRelocateManagerFactory(move_request5)

		relocate_manager1 = factory1.get_relocate_manager()
		relocate_manager2 = factory2.get_relocate_manager()
		relocate_manager3 = factory3.get_relocate_manager()
		relocate_manager4 = factory4.get_relocate_manager()
		relocate_manager5 = factory4.get_relocate_manager()

		relocate_manager1.relocate()
		client1_product_batch_now = self.client1.holder_product_batches.filter(product=self.product1).first()
		stock_room_product_batch_now = self.stock_room1_basket1.holder_product_batches.filter(client=self.client1).first()
		self.assertEqual(client1_product_batch_now.amount, 9)
		self.assertEqual(stock_room_product_batch_now.amount, 1)


	def test_eq_correct_way(self):
		pass

	def test_short_query(self):
		s = SearchRequest(product_batch=self.product_batch1, amount=10)
		a = ShortWayClientToStockRoomSearchMethod()
		gen = a.search(s)
		way = next(gen)
		print(way.coat)
		print([i.__dict__ for i in way.move_requests])
		way1 = next(gen)
		print(way1.coat)
		print([i.__dict__ for i in way1.move_requests])
		way2 = next(gen)
		print(way2.coat)
		print([i.__dict__ for i in way2.move_requests])

	def test_cheap_query(self):
		s = SearchRequest(product_batch=self.product_batch1, amount=10)
		a = CheapWayClientToStockRoomSearchMethod()
		gen = a.search(s)
		way = next(gen)
		print(way.coat)
		print([i.__dict__ for i in way.move_requests])