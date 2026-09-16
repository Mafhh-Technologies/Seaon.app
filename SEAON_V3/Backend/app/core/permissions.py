from enum import StrEnum


class Role(StrEnum):
	ADMIN = "admin"
	MANAGER = "manager"
	OPERATOR = "operator"
	VIEWER = "viewer"


def can_manage_inventory(role: str) -> bool:
	return role in {Role.ADMIN, Role.MANAGER, Role.OPERATOR}


def can_manage_orders(role: str) -> bool:
	return role in {Role.ADMIN, Role.MANAGER}
