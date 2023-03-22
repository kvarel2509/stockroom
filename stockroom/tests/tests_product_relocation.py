from django.test import TestCase

from stockroom import models
from stockroom.logic.product_relocation.domain import MoveRequest
from stockroom.logic.product_relocation.exceptions import BasketDoesNotSupportThisProduct, LimitIsExceeded, NotEnoughProduct, TargetIsHolder
from stockroom.logic.product_relocation.factory import BaseRelocateManagerFactory
from stockroom.logic.search_engine_for_ways_to_relocate.domain import SearchRequest
from stockroom.logic.search_engine_for_ways_to_relocate.factory import BaseSearchEngineFactory
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

		Road.objects.create(stock_room=self.stock_room1, client=self.client1, distance=100)
		Road.objects.create(stock_room=self.stock_room2, client=self.client1, distance=100)
		Road.objects.create(stock_room=self.stock_room3, client=self.client1, distance=100)

		self.stock_room1_basket1 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room1, product=self.product1, limit=5, tariff=1
		)
		self.stock_room1_basket2 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room1, product=self.product2, limit=15, tariff=2
		)

		self.stock_room1_basket3 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room2, product=self.product1, limit=6, tariff=2
		)
		self.stock_room1_basket4 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room2, product=self.product3, limit=20, tariff=2
		)

		self.stock_room1_basket5 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room3, product=self.product1, limit=7, tariff=3
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
		stock_room_product_batch_now = self.stock_room1_basket1.holder_product_batches.first()
		self.assertEqual(client1_product_batch_now.amount, 9)
		self.assertEqual(stock_room_product_batch_now.amount, 1)
		self.assertEqual(self.stock_room1_basket1.employed_limit, 1)
		self.assertEqual(self.stock_room1_basket1.stock_room.employed_limit, 1)
		
		with self.assertRaises(BasketDoesNotSupportThisProduct):
			relocate_manager2.relocate()

		with self.assertRaises(LimitIsExceeded):
			relocate_manager3.relocate()
		
		with self.assertRaises(LimitIsExceeded):
			relocate_manager4.relocate()
		
		relocate_manager5.relocate()
		client1_product_batch_now = self.client1.holder_product_batches.filter(product=self.product1).first()
		stock_room_product_batch_now = self.stock_room1_basket1.holder_product_batches.first()
		self.assertEqual(client1_product_batch_now.amount, 5)
		self.assertEqual(stock_room_product_batch_now.amount, 5)
		self.assertEqual(self.stock_room1_basket1.employed_limit, 5)
		self.assertEqual(self.stock_room1_basket1.stock_room.employed_limit, 5)


	def test_stock_room_to_stock_room(self):
		move_request1 = MoveRequest(
			target=self.stock_room1_basket1,
			product_batch=self.product_batch1,
			amount=1
		)
		factory1 = BaseRelocateManagerFactory(move_request1)
		relocate_manager1 = factory1.get_relocate_manager()
		relocate_manager1.relocate()
		stock_room_product_batch_now = self.stock_room1_basket1.holder_product_batches.first()
		move_request2 = MoveRequest(
			target=self.stock_room1_basket3,
			product_batch=stock_room_product_batch_now,
			amount=1
		)
		factory2 = BaseRelocateManagerFactory(move_request2)
		relocate_manager2 = factory2.get_relocate_manager()
		relocate_manager2.relocate()
		stock_room1_product_batch_now = self.stock_room1_basket1.holder_product_batches.first()
		stock_room3_product_batch_now = self.stock_room1_basket3.holder_product_batches.first()
		self.assertEqual(stock_room1_product_batch_now, None)
		self.assertEqual(self.stock_room1_basket1.employed_limit, 0)
		self.assertEqual(self.stock_room1_basket1.stock_room.employed_limit, 0)
		self.assertEqual(stock_room3_product_batch_now.amount, 1)
		self.assertEqual(self.stock_room1_basket3.employed_limit, 1)
		self.assertEqual(self.stock_room1_basket3.stock_room.employed_limit, 1)

	def test_search_ways_for_relocate(self):
		search_request1 = SearchRequest(
			product_batch=self.product_batch1,
			amount=7,
			method_alias='short_way'
		)
		factory1 = BaseSearchEngineFactory(search_request1)
		search_engine1 = factory1.get_search_engine()
		gen = search_engine1.search()

		search_response = next(gen)
		self.assertEqual(search_response.coat, 21)
		self.assertEqual(len(search_response), 1)
		move_request = search_response.move_requests[0]
		self.assertEqual(move_request.target, self.stock_room1_basket5)
		self.assertEqual(move_request.amount, 7)
		search_response = next(gen)
		self.assertEqual(search_response.coat, 9)
		self.assertEqual(len(search_response), 2)
		fake_move_request1 = MoveRequest(target=self.stock_room1_basket1, product_batch=self.product_batch1, amount=5)
		fake_move_request2 = MoveRequest(target=self.stock_room1_basket3, product_batch=self.product_batch1, amount=2)
		self.assertIn(fake_move_request1, search_response.move_requests)
		self.assertIn(fake_move_request2, search_response.move_requests)
		
		search_request2 = SearchRequest(
			product_batch=self.product_batch1,
			amount=20,
			method_alias='short_way'
		)
		factory2 = BaseSearchEngineFactory(search_request2)
		search_engine2 = factory2.get_search_engine()
		gen = search_engine2.search()

		with self.assertRaises(StopIteration):
			next(gen)
		
		search_request3 = SearchRequest(
			product_batch=self.product_batch1,
			amount=7,
			method_alias='cheap_way'
		)
		factory3 = BaseSearchEngineFactory(search_request3)
		search_engine3 = factory3.get_search_engine()
		gen = search_engine3.search()
		search_response = next(gen)
		self.assertEqual(search_response.coat, 9)
		self.assertEqual(len(search_response), 2)
		self.assertIn(fake_move_request1, search_response.move_requests)
		self.assertIn(fake_move_request2, search_response.move_requests)
