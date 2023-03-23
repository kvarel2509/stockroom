class TargetIsHolder(Exception):
	"""Цель перемещения уже является держателем"""
	pass


class NotEnoughProduct(Exception):
	"""Недостаточно продукии"""
	pass


class LimitIsExceeded(Exception):
	"""Превышение лимитов"""
	pass


class BasketDoesNotSupportThisProduct(Exception):
	"""Нет разрешения на хранение типа продукции"""
	pass
