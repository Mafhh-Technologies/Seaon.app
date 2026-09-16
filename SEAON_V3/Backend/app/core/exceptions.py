class ServiceError(Exception):
	"""Base exception for expected service-layer failures."""


class NotFoundError(ServiceError):
	pass


class ConflictError(ServiceError):
	pass


class InvalidOperationError(ServiceError):
	pass
