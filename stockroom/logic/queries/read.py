from stockroom import models

from django.contrib.contenttypes.models import ContentType


class BrokerDB:
	@staticmethod
	def get_client_list():
		return models.Client.objects.all()

	@staticmethod
	def get_client(client_pk):
		return models.Client.objects.get(pk=client_pk)

	@staticmethod
	def get_client_holder_product_batches_by_pk(client_pk):
		client_type = ContentType.objects.get_for_model(models.Client)
		return models.ProductBatch.objects.filter(content_type_holder=client_type, object_id_holder=client_pk)

	@staticmethod
	def get_client_holder_product_batches_by_object(client):
		return client.holder_product_batches.all()

	@staticmethod
	def get_product_batch(product_batch_pk):
		return models.ProductBatch.objects.get(pk=product_batch_pk)

	@staticmethod
	def get_available_stockroom_baskets_for_relocate_product(product):
		return models.StockRoomBasket.objects.filter(product=product)
