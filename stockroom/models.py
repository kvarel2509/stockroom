from django.db import models


class Product(models.Model):
	name = models.CharField(
		verbose_name='название',
		max_length=255
	)

	def __str__(self):
		return f'Product<pk={self.pk}, name={self.name}>'

	class Meta:
		verbose_name = 'продукт'


class StockRoom(models.Model):
	name = models.CharField(
		verbose_name='название',
		max_length=255,
	)
	limit = models.PositiveIntegerField(
		verbose_name='общий лимит',
	)
	products = models.ManyToManyField(
		verbose_name='продукт',
		to=Product,
		through='StockRoomBasket',
		related_name='stock_rooms'
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
	products = models.ManyToManyField(
		verbose_name='продукты',
		to=Product,
		through='ClientProduct',
		related_name='clients'
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
		verbose_name='продукт',
		to=Product,
		on_delete=models.CASCADE,
		related_name='stock_room_baskets'
	)
	limit = models.PositiveIntegerField(
		verbose_name='лимит',
	)
	tariff = models.DecimalField(
		verbose_name='тариф',
		help_text='за единицу продукта',
		max_digits=10,
		decimal_places=1
	)
	clients = models.ManyToManyField(
		verbose_name='клиенты',
		to=Client,
		through='StockRoomBasketPosition',
		related_name='stock_room_baskets'
	)

	def __str__(self):
		return f'StockRoomBasket<pk={self.pk}, stock_room={self.stock_room}, product={self.product}>'

	class Meta:
		verbose_name = 'позиция на складе'


class StockRoomBasketPosition(models.Model):
	stock_room_basket = models.ForeignKey(
		verbose_name='позиция на складе',
		to=StockRoomBasket,
		on_delete=models.CASCADE,
		related_name='stock_room_basket_position'
	)
	client = models.ForeignKey(
		verbose_name='владелец',
		to=Client,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='stock_room_basket_position'
	)
	amount = models.PositiveIntegerField(
		verbose_name='количество'
	)

	def __str__(self):
		return f'StockRoomBasketPosition<pk={self.pk}, stock_room_basket={self.stock_room_basket}, amount={self.amount}>'

	class Meta:
		verbose_name = 'продукт на складе'


class ClientProduct(models.Model):
	client = models.ForeignKey(
		verbose_name='владелец',
		to=Client,
		on_delete=models.CASCADE,
		related_name='client_products'
	)
	product = models.ForeignKey(
		verbose_name='продукт',
		to=Product,
		on_delete=models.CASCADE,
		related_name='client_products'
	)
	amount = models.PositiveIntegerField(
		verbose_name='количество'
	)

	def __str__(self):
		return f'ClientProduct<pk={self.pk}, client={self.client}, product={self.product}, amount={self.amount}>'

	class Meta:
		verbose_name = 'продукт клиента'


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
		return f'Road<pk={self.pk}, client={self.client}, stock_room={self.stock_room}, distance={self.distance}>'
