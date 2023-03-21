from django.test import TestCase
from stockroom import models
from stockroom.logic.product_relocation.check_relocate import CheckProductBatchHolderIsFromEntity, \
	CheckEnoughProductToRelocate, CheckFitInStockRoomBasketLimit, CheckFitInStockRoomLimit
from stockroom.logic.product_relocation.domain import MoveRequest
from stockroom.logic.product_relocation.exceptions import IsNotHolder, NotEnoughProduct, LimitIsExceeded
from stockroom.logic.product_relocation.factory import BaseRelocateManagerBuilder


class ProductRelocateTests(TestCase):
	def setUp(self) -> None:
		self.client1 = models.Client.objects.create(name='Иван')
		self.client2 = models.Client.objects.create(name='Петр')

		self.product1 = models.Product.objects.create(name='Продукт')
		self.product2 = models.Product.objects.create(name='Продукт2')
		self.product3 = models.Product.objects.create(name='Продукт3')

		self.stock_room1 = models.StockRoom.objects.create(name='Склад1', limit=15)
		self.stock_room2 = models.StockRoom.objects.create(name='Склад2', limit=15)

		self.stock_room1_basket1 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room1, product=self.product1, limit=10, tariff=1
		)
		self.stock_room1_basket2 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room1, product=self.product2, limit=20, tariff=2
		)

		self.stock_room1_basket3 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room2, product=self.product1, limit=10, tariff=1
		)
		self.stock_room1_basket4 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room2, product=self.product3, limit=20, tariff=2
		)

		self.product_batch1 = models.ProductBatch.objects.create(product=self.product1, amount=100, own=self.client1, holder=self.client1)
		self.product_batch2 = models.ProductBatch.objects.create(product=self.product2, amount=5, own=self.client1, holder=self.client1)
		self.product_batch3 = models.ProductBatch.objects.create(product=self.product3, amount=100, own=self.client1, holder=self.client1)
		self.product_batch4 = models.ProductBatch.objects.create(product=self.product3, amount=100, own=self.client1, holder=self.client2)

	def test_client_to_client_relocation_is_successful(self):
		move_request = MoveRequest(
			from_entity=self.client1,
			to_entity=self.client2,
			product_batch=self.product_batch1,
			amount=10
		)
		factory = BaseRelocateManagerBuilder(move_request)
		relocate_manager = factory.get_relocate_manager()
		relocate_manager.relocate()

		client1_product_batch_now = self.client1.holder_product_batches.filter(product=self.product1).first()
		client2_product_batch_now = self.client2.holder_product_batches.filter(product=self.product1).first()

		self.assertEqual(client1_product_batch_now.amount, 90)
		self.assertEqual(client2_product_batch_now.amount, 10)

	def test_client_to_client_relocation_unification_of_parties_is_successful(self):
		move_request = MoveRequest(
			from_entity=self.client1,
			to_entity=self.client2,
			product_batch=self.product_batch3,
			amount=10
		)
		factory = BaseRelocateManagerBuilder(move_request)
		relocate_manager = factory.get_relocate_manager()
		relocate_manager.relocate()

		client1_product_batch_now = self.client1.holder_product_batches.filter(product=self.product3).first()
		client2_product_batch_now = self.client2.holder_product_batches.filter(product=self.product3).first()

		self.assertEqual(client1_product_batch_now.amount, 90)
		self.assertEqual(client2_product_batch_now.amount, 110)

	def test_client_to_client_relocation_is_fail_is_not_holder(self):
		move_request = MoveRequest(
			from_entity=self.client2,
			to_entity=self.client1,
			product_batch=self.product_batch1,
			amount=10
		)
		factory = BaseRelocateManagerBuilder(move_request)
		relocate_manager = factory.get_relocate_manager()

		with self.assertRaises(IsNotHolder):
			relocate_manager.relocate()

		client1_product_batch_now = self.client1.holder_product_batches.filter(product=self.product1).first()
		client2_product_batch_now = self.client2.holder_product_batches.filter(product=self.product1).first()

		self.assertEqual(client1_product_batch_now.amount, 100)
		self.assertEqual(client2_product_batch_now, None)

	def test_client_to_client_relocation_is_fail_is_not_enough_product(self):
			move_request = MoveRequest(
				from_entity=self.client1,
				to_entity=self.client2,
				product_batch=self.product_batch1,
				amount=110
			)
			factory = BaseRelocateManagerBuilder(move_request)
			relocate_manager = factory.get_relocate_manager()

			with self.assertRaises(NotEnoughProduct):
				relocate_manager.relocate()

			client1_product_batch_now = self.client1.holder_product_batches.filter(product=self.product1).first()
			client2_product_batch_now = self.client2.holder_product_batches.filter(product=self.product1).first()

			self.assertEqual(client1_product_batch_now.amount, 100)
			self.assertEqual(client2_product_batch_now, None)
