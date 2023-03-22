from typing import Sequence

from django.db import transaction


class MoveRequest:
	"""Сущность - запрос на перемещение продукции"""
	def __init__(self, target, product_batch, amount) -> None:
		self.target = target
		self.product_batch = product_batch
		self.amount = amount

	def __eq__(self, other):
		return self.target is other.target and self.product_batch is other.product_batch and self.amount == other.amount

	def __hash__(self):
		return hash((self.target, self.product_batch, self.amount))


class CheckRelocateBehavior:
	"""Базовый класс - проверка на возможность выполнения перемещения продукции"""
	def check_relocate(self, move_request: MoveRequest) -> None: ...


class CheckListRelocateBehavior(CheckRelocateBehavior):
	"""
	Расширение для CheckRelocateBehavior - искапсуляция перечня проверок на возможность
	выполнения перемещения продукции
	"""
	def __init__(self, check_list_relocate_behavior: Sequence[CheckRelocateBehavior]) -> None:
		self.check_list_relocate_behavior = check_list_relocate_behavior

	def check_relocate(self, move_request: MoveRequest) -> None:
		for check_relocate_behavior in self.check_list_relocate_behavior:
			check_relocate_behavior.check_relocate(move_request)


class RelocateBehavior:
	"""Базовый класс - этап алгоритма перемещения продукции"""
	def relocate(self, move_request: MoveRequest) -> None: ...


class RelocateListActionBehavior(RelocateBehavior):
	"""Расширение для RelocateBehavior - искапсуляция перечня действий для перемещения продукции"""
	def __init__(self, relocate_list_action_behavior: Sequence[RelocateBehavior]) -> None:
		self.relocate_list_action_behavior = relocate_list_action_behavior

	def relocate(self, move_request: MoveRequest) -> None:
		for relocate_behavior in self.relocate_list_action_behavior:
			relocate_behavior.relocate(move_request)


class RelocateStage:
	"""Контекст для стратегий этапа перемещения. Реализует логику этапа перемещения продукции"""
	def __init__(self, check_relocate_behavior: CheckRelocateBehavior, relocate_behavior: RelocateBehavior) -> None:
		self.check_relocate_behavior = check_relocate_behavior
		self.relocate_behavior = relocate_behavior

	def relocate(self, move_request: MoveRequest) -> None:
		self.check_relocate(move_request)
		self.relocate_behavior.relocate(move_request)

	def check_relocate(self, move_request: MoveRequest) -> None:
		return self.check_relocate_behavior.check_relocate(move_request)


class RelocateManager:
	"""Контекст перемещения продукции. Выполняет оркестрацию процесса передачи продукции между держателями"""
	def __init__(self, move_request: MoveRequest, give_away_stage: RelocateStage, take_stage: RelocateStage) -> None:
		self.move_request = move_request
		self.give_away_stage = give_away_stage
		self.take_stage = take_stage

	def relocate(self) -> None:
		with transaction.atomic():
			self.give_away_stage.relocate(self.move_request)
			self.take_stage.relocate(self.move_request)


class RelocateManagerFactory:
	"""Фабрика, предоставляющая менеджер, отвечающий за перемещение продукции"""
	def __init__(self, move_request: MoveRequest) -> None:
		self.move_request = move_request

	def get_relocate_manager(self) -> RelocateManager: ...
