from decimal import Decimal
from enum import Enum


TRANSPORTATION_COST = Decimal('0.01')


class SearchWayRelocationAlias(Enum):
	SHORT_WAY = 'short_way'
	CHEAP_WAY = 'cheap_way'
