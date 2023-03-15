from django.test import TestCase
from stockroom import models
from stockroom.logic.product_relocation import ProductRelocation


class ProductRelocationTests(TestCase):
	def setUp(self) -> None:
		self.product_relocation = ProductRelocation()
		self.client1 = models.Client.objects.create(name='Иван')
		self.client2 = models.Client.objects.create(name='Петр')
		self.product1 = models.Product.objects.create(name='Продукт')
		self.product2 = models.Product.objects.create(name='Продукт2')
		self.stock_room1 = models.StockRoom.objects.create(name='Склад1', limit=100)
		self.stock_room1_basket1 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room1, product=self.product1, limit=90
		)
		self.stock_room1_basket2 = models.StockRoomBasket.objects.create(
			stock_room=self.stock_room1, product=self.product2, limit=90
		)

		self.client1.products.add(self.product1, through_defaults={'amount': 10})
		models.ClientProduct.objects.create(client=self.client2, product=self.product2, amount=10)

	def test_client_successfully_transfers_part_product_another_client(self):
		self.product_relocation.client_to_client(self.client1, self.client2, self.product1, 5)
		self.assertEqual(self.client1.client_products.get(product=self.product1).amount, 5)
		self.assertEqual(self.client2.client_products.get(product=self.product1).amount, 5)

	def test_client_successfully_transfers_all_product_another_client(self):
		self.product_relocation.client_to_client(self.client1, self.client2, self.product1, 10)
		self.assertEqual(self.client1.client_products.filter(product=self.product1).first(), None)
		self.assertEqual(self.client2.client_products.get(product=self.product1).amount, 10)

	def test_client_cannot_transfer_product_to_another_client_which_he_does_not_have(self):
		self.assertRaises(
			Exception,
			lambda: self.product_relocation.client_to_client(self.client1, self.client2, self.product2, 10))

	def test_client_cannot_transfer_product_to_another_client_which_he_has_little(self):
		self.assertRaises(
			Exception,
			lambda: self.product_relocation.client_to_client(self.client1, self.client2, self.product1, 15))

