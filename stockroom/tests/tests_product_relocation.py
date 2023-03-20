from django.test import TestCase
from stockroom import models
from stockroom.logic.product_relocation.check_relocate import CheckProductBatchHolderIsFromEntity, \
	CheckEnoughProductToRelocate, CheckFitInStockRoomBasketLimit, CheckFitInStockRoomLimit
from stockroom.logic.product_relocation.domain import MoveRequest
from stockroom.logic.product_relocation.exceptions import IsNotHolder, NotEnoughProduct, LimitIsExceeded


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
			stock_room=self.stock_room1, product=self.product2, limit=20, tariff=1
		)
		self.stock_room1_basket3 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room2, product=self.product1, limit=10, tariff=1
		)
		self.stock_room1_basket4 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room2, product=self.product2, limit=10, tariff=1
		)
		self.product_batch = models.ProductBatch.objects.create(product=self.product1, amount=5, own=self.client2, holder=self.client2)
		self.product_batch2 = models.ProductBatch.objects.create(product=self.product1, amount=5, own=self.client1, holder=self.client2)
		self.product_batch3 = models.ProductBatch.objects.create(product=self.product1, amount=100, own=self.client1, holder=self.client1)
		self.product_batch4 = models.ProductBatch.objects.create(product=self.product1, amount=100, own=self.client2, holder=self.client2)

	def test_check_product_batch_holder_is_from_entity_successfully(self):
		checker = CheckProductBatchHolderIsFromEntity()
		move_request = MoveRequest(from_entity=self.client2, to_entity=self.client1, product_batch=self.product_batch, amount=1)
		move_request2 = MoveRequest(from_entity=self.client2, to_entity=self.client1, product_batch=self.product_batch2, amount=1)
		self.assertIsNone(checker.check_relocate(move_request))
		self.assertIsNone(checker.check_relocate(move_request2))

	def test_check_product_batch_holder_is_from_entity_not_to_miss(self):
		move_request = MoveRequest(from_entity=self.client1, to_entity=self.client2, product_batch=self.product_batch, amount=1)
		move_request2 = MoveRequest(from_entity=self.client1, to_entity=self.client2, product_batch=self.product_batch2, amount=1)
		checker = CheckProductBatchHolderIsFromEntity()
		with self.assertRaises(IsNotHolder):
			checker.check_relocate(move_request)
		with self.assertRaises(IsNotHolder):
			checker.check_relocate(move_request2)

	def test_check_enough_product_to_relocate_successfully(self):
		checker = CheckEnoughProductToRelocate()
		move_request = MoveRequest(from_entity=self.client2, to_entity=self.client1, product_batch=self.product_batch, amount=1)
		move_request2 = MoveRequest(from_entity=self.client2, to_entity=self.client1, product_batch=self.product_batch, amount=5)
		self.assertIsNone(checker.check_relocate(move_request))
		self.assertIsNone(checker.check_relocate(move_request2))

	def test_check_enough_product_to_relocate_not_to_miss(self):
		checker = CheckEnoughProductToRelocate()
		move_request = MoveRequest(from_entity=self.client2, to_entity=self.client1, product_batch=self.product_batch, amount=6)

		with self.assertRaises(NotEnoughProduct):
			checker.check_relocate(move_request)

	def test_check_fit_in_stock_room_basket_successfully(self):
		checker = CheckFitInStockRoomBasketLimit()
		move_request = MoveRequest(from_entity=self.client1, to_entity=self.stock_room1_basket1, product_batch=self.product_batch3, amount=1)
		self.assertIsNone(checker.check_relocate(move_request))

	def test_check_fit_in_stock_room_basket_not_to_miss(self):
		checker = CheckFitInStockRoomBasketLimit()
		move_request = MoveRequest(from_entity=self.client1, to_entity=self.stock_room1_basket1, product_batch=self.product_batch3, amount=15)
		with self.assertRaises(LimitIsExceeded):
			checker.check_relocate(move_request)

	def test_check_fit_in_stock_room_successfully(self):
		checker = CheckFitInStockRoomLimit()
		move_request = MoveRequest(from_entity=self.client1, to_entity=self.stock_room1_basket1, product_batch=self.product_batch3, amount=1)
		self.assertIsNone(checker.check_relocate(move_request))

	# def test_client_successfully_transfers_part_product_another_client_(self):
	# 	self.product_relocation.client_to_client(self.client1, self.client2, self.product1, 5)
	# 	self.assertEqual(self.client1.client_products.get(product=self.product1).amount, 5)
	# 	self.assertEqual(self.client2.client_products.get(product=self.product1).amount, 5)
	#
	# def test_client_successfully_transfers_all_product_another_client(self):
	# 	self.product_relocation.client_to_client(self.client1, self.client2, self.product1, 10)
	# 	self.assertEqual(self.client1.client_products.filter(product=self.product1).first(), None)
	# 	self.assertEqual(self.client2.client_products.get(product=self.product1).amount, 10)
	#
	# def test_client_cannot_transfer_product_to_another_client_which_he_does_not_have(self):
	# 	self.assertRaises(
	# 		Exception,
	# 		lambda: self.product_relocation.client_to_client(self.client1, self.client2, self.product2, 10))
	#
	# def test_client_cannot_transfer_product_to_another_client_which_he_has_little(self):
	# 	self.assertRaises(
	# 		Exception,
	# 		lambda: self.product_relocation.client_to_client(self.client1, self.client2, self.product1, 15))
	#
