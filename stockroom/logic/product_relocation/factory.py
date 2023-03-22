from stockroom.logic.product_relocation.check_relocate import CheckEnoughProductToRelocate, \
	CheckStockRoomBasketSupportsProduct, CheckFitInStockRoomBasketLimit, CheckFitInStockRoomLimit, CheckTargetIsHolder
from stockroom.logic.product_relocation.domain import RelocateManagerFactory, RelocateManager, \
	RelocateStage, CheckListRelocateBehavior, RelocateListActionBehavior, CheckRelocateBehavior
from stockroom.logic.product_relocation.product_relocation import ChangeProductBatchGiveAway, \
	ChangeStockRoomBasketLimitGiveAway, ChangeStockRoomLimitGiveAway, ProductBatchTakes, \
	ChangeStockRoomBasketLimitTakes, ChangeStockRoomLimitTakes
from stockroom.models import Client, StockRoomBasket


class BaseRelocateManagerFactory(RelocateManagerFactory):
	def get_relocate_manager(self) -> RelocateManager:
		return RelocateManager(
			move_request=self.move_request,
			give_away_stage=self._get_give_away_stage(),
			take_stage=self._get_take_stage()
		)

	def _get_give_away_stage(self) -> RelocateStage:
		if isinstance(self.move_request.product_batch.holder, Client):
			return RelocateStage(
				check_relocate_behavior=CheckListRelocateBehavior(
					check_list_relocate_behavior=(
						CheckTargetIsHolder(),
						CheckEnoughProductToRelocate(),
					)
				),
				relocate_behavior=ChangeProductBatchGiveAway(),
			)
		elif isinstance(self.move_request.product_batch.holder, StockRoomBasket):
			return RelocateStage(
				check_relocate_behavior=CheckListRelocateBehavior(
					check_list_relocate_behavior=(
						CheckTargetIsHolder(),
						CheckEnoughProductToRelocate(),
					)
				),
				relocate_behavior=RelocateListActionBehavior(
					relocate_list_action_behavior=(
						ChangeProductBatchGiveAway(),
						ChangeStockRoomBasketLimitGiveAway(),
						ChangeStockRoomLimitGiveAway(),
					)
				)
			)
		else:
			raise NotImplementedError()

	def _get_take_stage(self) -> RelocateStage:
		if isinstance(self.move_request.target, Client):
			return RelocateStage(
				check_relocate_behavior=CheckRelocateBehavior(),
				relocate_behavior=ProductBatchTakes()
			)
		elif isinstance(self.move_request.target, StockRoomBasket):
			return RelocateStage(
				check_relocate_behavior=CheckListRelocateBehavior(
					check_list_relocate_behavior=(
						CheckStockRoomBasketSupportsProduct(),
						CheckFitInStockRoomBasketLimit(),
						CheckFitInStockRoomLimit(),
					)
				),
				relocate_behavior=RelocateListActionBehavior(
					relocate_list_action_behavior=(
						ProductBatchTakes(),
						ChangeStockRoomBasketLimitTakes(),
						ChangeStockRoomLimitTakes()
					)
				)
			)
		else:
			raise NotImplementedError()
