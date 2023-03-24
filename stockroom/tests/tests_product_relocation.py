from stockroom import models
from stockroom.logic.product_relocation.domain import MoveRequest
from stockroom.logic.product_relocation.exceptions import (
	BasketDoesNotSupportThisProduct,
	LimitIsExceeded,
	NotEnoughProduct,
	TargetIsHolder
)
from stockroom.logic.product_relocation.factory import BaseRelocateManagerFactory
from stockroom.logic.search_engine_for_ways_to_relocate.domain import SearchRequest
from stockroom.logic.search_engine_for_ways_to_relocate.factory import BaseSearchEngineFactory
from stockroom.models import Road

import decimal

from django.test import TestCase


class ProductRelocateTests(TestCase):
	def setUp(self) -> None:
		self.client1 = models.Client.objects.create(name='Иван')
		self.client2 = models.Client.objects.create(name='Петр')

		self.product1 = models.Product.objects.create(name='Продукт')
		self.product2 = models.Product.objects.create(name='Продукт2')
		self.product3 = models.Product.objects.create(name='Продукт3')

		self.stockroom1 = models.StockRoom.objects.create(name='Склад1', limit=10)
		self.stockroom2 = models.StockRoom.objects.create(name='Склад2', limit=10)
		self.stockroom3 = models.StockRoom.objects.create(name='Склад3', limit=15)

		Road.objects.create(stockroom=self.stockroom1, client=self.client1, distance=100)
		Road.objects.create(stockroom=self.stockroom2, client=self.client1, distance=100)
		Road.objects.create(stockroom=self.stockroom3, client=self.client1, distance=100)

		self.stockroom1_basket1 = models.StockRoomBasket.objects.create(
			stockroom=self.stockroom1, product=self.product1, limit=5, tariff=1
		)
		self.stockroom1_basket2 = models.StockRoomBasket.objects.create(
			stockroom=self.stockroom1, product=self.product2, limit=15, tariff=2
		)
		self.stockroom2_basket3 = models.StockRoomBasket.objects.create(
			stockroom=self.stockroom2, product=self.product1, limit=6, tariff=2
		)
		self.stockroom2_basket4 = models.StockRoomBasket.objects.create(
			stockroom=self.stockroom2, product=self.product3, limit=20, tariff=2
		)
		self.stockroom3_basket5 = models.StockRoomBasket.objects.create(
			stockroom=self.stockroom3, product=self.product1, limit=7, tariff=3
		)
		self.product_batch1 = models.ProductBatch.objects.create(product=self.product1, amount=10, own=self.client1, holder=self.client1)
		self.product_batch2 = models.ProductBatch.objects.create(product=self.product2, amount=15, own=self.client1, holder=self.client1)
		self.product_batch3 = models.ProductBatch.objects.create(product=self.product3, amount=100, own=self.client1, holder=self.client1)
		self.product_batch4 = models.ProductBatch.objects.create(product=self.product3, amount=100, own=self.client1, holder=self.client2)

	def test_client_to_client_relocation_success_with_remains(self):
		move_request = MoveRequest(
			target=self.client2,
			product_batch=self.product_batch1,
			amount=5
		)
		factory = BaseRelocateManagerFactory(move_request)
		relocate_manager = factory.get_relocate_manager()
		relocate_manager.relocate()
		client1_product_batch_now = self.client1.holder_product_batches.filter(product=self.product1).first()
		client2_product_batch_now = self.client2.holder_product_batches.filter(product=self.product1).first()
		self.assertEqual(client1_product_batch_now.amount, 5)
		self.assertEqual(client2_product_batch_now.amount, 5)

	def test_client_to_client_relocation_success_without_remains(self):
		move_request = MoveRequest(
			target=self.client2,
			product_batch=self.product_batch1,
			amount=10
		)
		factory = BaseRelocateManagerFactory(move_request)
		relocate_manager = factory.get_relocate_manager()
		relocate_manager.relocate()
		client1_product_batch_now = self.client1.holder_product_batches.filter(product=self.product1).first()
		client2_product_batch_now = self.client2.holder_product_batches.filter(product=self.product1).first()
		self.assertEqual(client1_product_batch_now, None)
		self.assertEqual(client2_product_batch_now.amount, 10)

	def test_client_to_client_relocation_fail_target_is_holder(self):
		move_request = MoveRequest(
			target=self.client1,
			product_batch=self.product_batch1,
			amount=5
		)
		factory = BaseRelocateManagerFactory(move_request)
		relocate_manager = factory.get_relocate_manager()

		with self.assertRaises(TargetIsHolder):
			relocate_manager.relocate()

	def test_client_to_client_relocation_fail_not_enough_product(self):
		move_request = MoveRequest(
			target=self.client2,
			product_batch=self.product_batch1,
			amount=1000
		)
		factory = BaseRelocateManagerFactory(move_request)
		relocate_manager = factory.get_relocate_manager()

		with self.assertRaises(NotEnoughProduct):
			relocate_manager.relocate()

	def test_client_to_stockroom_relocation_success(self):
		move_request = MoveRequest(
			target=self.stockroom1_basket1,
			product_batch=self.product_batch1,
			amount=1
		)
		factory = BaseRelocateManagerFactory(move_request)
		relocate_manager = factory.get_relocate_manager()
		relocate_manager.relocate()
		client1_product_batch_now = self.client1.holder_product_batches.filter(product=self.product1).first()
		stockroom_product_batch_now = self.stockroom1_basket1.holder_product_batches.first()
		self.assertEqual(client1_product_batch_now.amount, 9)
		self.assertEqual(stockroom_product_batch_now.amount, 1)
		self.assertEqual(self.stockroom1_basket1.employed_limit, 1)
		self.assertEqual(self.stockroom1_basket1.stockroom.employed_limit, 1)

	def test_client_to_stockroom_relocation_fail_basket_does_not_support_product(self):
		move_request = MoveRequest(
			target=self.stockroom1_basket1,
			product_batch=self.product_batch2,
			amount=2
		)
		factory = BaseRelocateManagerFactory(move_request)
		relocate_manager = factory.get_relocate_manager()

		with self.assertRaises(BasketDoesNotSupportThisProduct):
			relocate_manager.relocate()

	def test_client_to_stockroom_relocation_fail_basket_limit_is_exceeded(self):
		move_request = MoveRequest(
			target=self.stockroom1_basket1,
			product_batch=self.product_batch1,
			amount=6
		)
		factory = BaseRelocateManagerFactory(move_request)
		relocate_manager = factory.get_relocate_manager()

		with self.assertRaises(LimitIsExceeded):
			relocate_manager.relocate()

	def test_client_to_stockroom_relocation_fail_stockroom_limit_is_exceeded(self):
		move_request = MoveRequest(
			target=self.stockroom1_basket2,
			product_batch=self.product_batch2,
			amount=12
		)
		factory = BaseRelocateManagerFactory(move_request)
		relocate_manager = factory.get_relocate_manager()

		with self.assertRaises(LimitIsExceeded):
			relocate_manager.relocate()

	def test_stockroom_to_stockroom_success_with_remains(self):
		move_request = MoveRequest(
			target=self.stockroom1_basket1,
			product_batch=self.product_batch1,
			amount=5
		)
		factory = BaseRelocateManagerFactory(move_request)
		relocate_manager = factory.get_relocate_manager()
		relocate_manager.relocate()

		stockroom_product_batch_now = self.stockroom1_basket1.holder_product_batches.first()
		move_request2 = MoveRequest(
			target=self.stockroom2_basket3,
			product_batch=stockroom_product_batch_now,
			amount=1
		)
		factory2 = BaseRelocateManagerFactory(move_request2)
		relocate_manager2 = factory2.get_relocate_manager()
		relocate_manager2.relocate()

		stockroom1_basket1_product_batch_now = self.stockroom1_basket1.holder_product_batches.first()
		stockroom2_basket3_product_batch_now = self.stockroom2_basket3.holder_product_batches.first()

		self.assertEqual(stockroom1_basket1_product_batch_now.holder.employed_limit, 4)
		self.assertEqual(stockroom1_basket1_product_batch_now.holder.stockroom.employed_limit, 4)
		self.assertEqual(stockroom1_basket1_product_batch_now.amount, 4)
		self.assertEqual(stockroom2_basket3_product_batch_now.amount, 1)
		self.assertEqual(self.stockroom2_basket3.employed_limit, 1)
		self.assertEqual(self.stockroom2_basket3.stockroom.employed_limit, 1)

	def test_search_ways_for_relocate_short_way(self):
		search_request1 = SearchRequest(
			product_batch=self.product_batch1,
			amount=20,
			method_alias='short_way'
		)
		factory1 = BaseSearchEngineFactory(search_request1)
		search_engine1 = factory1.get_search_engine()
		search_response = search_engine1.search()
		self.assertEqual(search_response.coat, decimal.Decimal('28'))
		self.assertEqual(len(search_response), 1)

		move_request = search_response.move_requests.pop()
		self.assertEqual(move_request.target, self.stockroom3_basket5)
		self.assertEqual(move_request.amount, 7)

		search_request2 = SearchRequest(
			product_batch=self.product_batch1,
			amount=20,
			method_alias='short_way'
		)
		factory2 = BaseSearchEngineFactory(search_request2)
		search_engine2 = factory2.get_search_engine()
		search_response = search_engine2.search()
		self.assertEqual(search_response, None)

	def test_search_ways_for_relocate_cheap_way(self):
		search_request3 = SearchRequest(
			product_batch=self.product_batch1,
			amount=7,
			method_alias='cheap_way'
		)
		factory3 = BaseSearchEngineFactory(search_request3)
		search_engine3 = factory3.get_search_engine()
		search_response = search_engine3.search()
		self.assertEqual(search_response.coat, decimal.Decimal('16'))
		self.assertEqual(len(search_response), 2)
		move_request1, move_request2 = sorted(list(search_response.move_requests), key=lambda x: x.amount)
		self.assertEqual(move_request1.amount, 2)
		self.assertEqual(move_request2.amount, 5)
		self.assertEqual(move_request1.target, self.stockroom2_basket3)
		self.assertEqual(move_request2.target, self.stockroom1_basket1)

