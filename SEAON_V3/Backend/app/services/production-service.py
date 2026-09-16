from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import InvalidOperationError, NotFoundError
from app.models.production import ProductionJob
from app.schemes.production import ProductionCreate


def list_jobs(db: Session) -> list[ProductionJob]:
	return list(db.scalars(select(ProductionJob).order_by(ProductionJob.id.desc())))


def start_job(db: Session, payload: ProductionCreate) -> ProductionJob:
	job = ProductionJob(
		product=payload.product,
		quantity=payload.quantity,
		operator=payload.operator,
		status="in-progress",
		started_at=datetime.now(timezone.utc),
	)
	db.add(job)
	db.commit()
	db.refresh(job)
	return job


def complete_job(db: Session, job_id: int, output: int) -> ProductionJob:
	job = db.get(ProductionJob, job_id)
	if job is None:
		raise NotFoundError("Production job not found")
	if job.status == "completed":
		raise InvalidOperationError("Production job is already completed")
	job.status = "completed"
	job.quantity = output
	job.completed_at = datetime.now(timezone.utc)
	db.commit()
	db.refresh(job)
	return job