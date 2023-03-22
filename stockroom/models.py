from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Product(models.Model):
	name = models.CharField(
		verbose_name='название',
		max_length=255
	)

	def __str__(self):
		return f'Product<pk={self.pk}, name={self.name}>'

	class Meta:
		verbose_name = 'продукция'


class StockRoom(models.Model):
	name = models.CharField(
		verbose_name='название',
		max_length=255,
	)
	limit = models.PositiveIntegerField(
		verbose_name='общий лимит',
	)
	employed_limit = models.IntegerField(
		verbose_name='используемый лимит',
		default=0
	)

	def __str__(self):
		return f'StockRoom<pk={self.pk}, name={self.name}, limit={self.limit}>'

	class Meta:
		verbose_name = 'склад'


class Client(models.Model):
	name = models.CharField(
		verbose_name='имя',
		max_length=255
	)
	own_product_batches = GenericRelation(
		verbose_name='партия продукции',
		to='ProductBatch',
		content_type_field='content_type_own',
		object_id_field='object_id_own',
	)
	holder_product_batches = GenericRelation(
		verbose_name='партия продукции',
		to='ProductBatch',
		content_type_field='content_type_holder',
		object_id_field='object_id_holder',
	)

	def __str__(self):
		return f'Client<pk={self.pk}, name={self.name}>'

	class Meta:
		verbose_name = 'клиент'


class StockRoomBasket(models.Model):
	stock_room = models.ForeignKey(
		verbose_name='склад',
		to=StockRoom,
		on_delete=models.CASCADE,
		related_name='stock_room_baskets'
	)
	product = models.ForeignKey(
		verbose_name='продукция',
		to=Product,
		on_delete=models.CASCADE,
		related_name='stock_room_baskets'
	)
	limit = models.PositiveIntegerField(
		verbose_name='лимит',
	)
	employed_limit = models.IntegerField(
		verbose_name='используемый лимит',
		default=0
	)
	tariff = models.DecimalField(
		verbose_name='тариф',
		help_text='за единицу продукта',
		max_digits=10,
		decimal_places=1
	)
	own_product_batches = GenericRelation(
		verbose_name='партии продукции',
		to='ProductBatch',
		content_type_field='content_type_own',
		object_id_field='object_id_own',
		related_query_name='own_object'
	)
	holder_product_batches = GenericRelation(
		verbose_name='партии продукции',
		to='ProductBatch',
		content_type_field='content_type_holder',
		object_id_field='object_id_own',
		related_query_name='holder_object'
	)

	def __str__(self):
		return f'StockRoomBasket<pk={self.pk}, product={self.product.pk}, limit={self.limit}, tariff={self.tariff}>'

	class Meta:
		verbose_name = 'позиция на складе'


class ProductBatch(models.Model):
	product = models.ForeignKey(
		verbose_name='продукция',
		to=Product,
		on_delete=models.CASCADE
	)
	amount = models.PositiveIntegerField(
		verbose_name='количество'
	)
	content_type_own = models.ForeignKey(
		to=ContentType,
		on_delete=models.CASCADE,
		related_name='+'
	)
	object_id_own = models.PositiveIntegerField()
	own = GenericForeignKey(
		ct_field='content_type_own',
		fk_field='object_id_own'
	)
	content_type_holder = models.ForeignKey(
		to=ContentType,
		on_delete=models.CASCADE,
		related_name='+'
	)
	object_id_holder = models.PositiveIntegerField()
	holder = GenericForeignKey(
		ct_field='content_type_holder',
		fk_field='object_id_holder'
	)

	def __str__(self):
		return f'ProductBatch<pk={self.pk}, product={self.product.pk}, amount={self.amount}>'


class Road(models.Model):
	client = models.ForeignKey(
		verbose_name='клиент',
		to=Client,
		on_delete=models.CASCADE,
		related_name='roads'
	)
	stock_room = models.ForeignKey(
		verbose_name='склад',
		to=StockRoom,
		on_delete=models.CASCADE,
		related_name='roads'
	)
	distance = models.PositiveIntegerField(
		verbose_name='дистанция'
	)

	def __str__(self):
		return f'Road<pk={self.pk}, client={self.client.pk}, stock_room={self.stock_room.pk}, distance={self.distance}>'
