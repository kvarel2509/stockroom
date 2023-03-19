from typing import Iterable


class MoveRequest:
	"""Сущность - запрос на перемещение продукции"""

	def __init__(self, from_entity, to_entity, product_batch, amount):
		self.from_entity = from_entity
		self.to_entity = to_entity
		self.product_batch = product_batch
		self.amount = amount


class CheckRelocateBehavior:
	"""Базовый класс - проверка на возможность выполнения перемещения продукции"""

	def check_relocate(self, move_request: MoveRequest) -> None: ...


class CheckListRelocate(CheckRelocateBehavior):
	"""Расширение для CheckRelocateBehavior - искапсуляция перечня проверок на возможность выполнения перемещения продукции"""

	def __init__(self, check_list_relocate_behavior: Iterable[CheckRelocateBehavior]) -> None:
		self.check_list_relocate_behavior = check_list_relocate_behavior

	def check_relocate(self, move_request: MoveRequest) -> None:
		for check_relocate_behavior in self.check_list_relocate_behavior:
			check_relocate_behavior.check_relocate(move_request)


class RelocateBehavior:
	"""Базовый класс - этап алгоритма перемещения продукции"""

	def relocate(self, move_request: MoveRequest) -> None: ...
	

class RelocateStage:
	"""Контекст для стратегий этапа перемещения. Реализует логику этапа перемещения продукции"""

	def __init__(self, check_relocate_behavior: CheckRelocateBehavior, relocate_behavior: RelocateBehavior):
		self.check_relocate_behavior = check_relocate_behavior
		self.relocate_behavior = relocate_behavior

	def relocate(self, move_request: MoveRequest):
		self.check_relocate(move_request)
		self.relocate_behavior.relocate(move_request)

	def check_relocate(self, move_request: MoveRequest):
		return self.check_relocate_behavior.check_relocate(move_request)


class RelocateManager:
	"""Контекст перемещения продукции. Выполняет оркестрацию процесса передачи продукции между держателями"""

	def __init__(self, move_request: MoveRequest, give_away_stage: RelocateStage, take_stage: RelocateStage) -> None:
		self.move_request = move_request
		self.give_away_stage = give_away_stage
		self.take_stage = take_stage

	def relocate(self):
		with transaction.atomic():
			self.give_away_stage.relocate(self.move_request)
			self.take_stage.relocate(self.move_request)
