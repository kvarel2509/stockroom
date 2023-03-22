from stockroom.logic.product_relocation.domain import MoveRequest
from stockroom.logic.product_relocation.exceptions import NotEnoughProduct, TargetIsHolder
from stockroom.logic.product_relocation.factory import BaseRelocateManagerFactory
from stockroom.logic.search_engine_for_ways_to_relocate.domain import SearchRequest
from stockroom.logic.search_engine_for_ways_to_relocate.factory import BaseSearchEngineFactory


def get_move_request(target_pk: int, target_content_type: int, product_batch_pk: int, amount: int) -> MoveRequest:
    ...

def get_search_request(product_batch_pk: int, amount: int, method_alias: str) -> SearchRequest:
    ...


def product_relocate(target_pk: int, product_batch_pk: int, amount: int):
    move_request = get_move_request(target_pk, product_batch_pk, amount)
    factory = BaseRelocateManagerFactory(move_request)
    relocate_manager = factory.get_relocate_manager()
    try:
        relocate_manager.relocate()
    except TargetIsHolder:
        pass
    except NotEnoughProduct:
        pass
    ...


def find_way_for_relocate(product_batch_pk: int, amount: int, method_alias: str):
    search_request = get_search_request(product_batch_pk, amount, method_alias)
    factory = BaseSearchEngineFactory(search_request)
    search_engine = factory.get_search_engine()
    try:
        search_engine.search()
    except StopIteration:
        pass
    ...
