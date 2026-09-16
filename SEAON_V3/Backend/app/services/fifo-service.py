from dataclasses import dataclass

from app.core.exceptions import InvalidOperationError


@dataclass
class StockLot:
	lot_id: str
	quantity: float


def consume_fifo(lots: list[StockLot], quantity: float) -> list[tuple[str, float]]:
	"""Consume the oldest lots first and return (lot_id, consumed_quantity)."""
	if quantity <= 0:
		raise InvalidOperationError("Quantity to consume must be positive")
	if sum(lot.quantity for lot in lots) < quantity:
		raise InvalidOperationError("Insufficient stock")
	remaining = quantity
	consumed: list[tuple[str, float]] = []
	for lot in lots:
		if remaining == 0:
			break
		amount = min(lot.quantity, remaining)
		lot.quantity -= amount
		remaining -= amount
		consumed.append((lot.lot_id, amount))
	return consumed
