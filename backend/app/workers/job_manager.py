"""
SatQuery AI - Job Manager
Manages async analysis jobs with real-time SSE progress streaming.
"""
import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncGenerator, Dict, Optional, List

logger = logging.getLogger(__name__)


@dataclass
class JobState:
    job_id: str
    status: str = "pending"       # pending | running | completed | failed | cancelled
    stage: str = ""
    progress: int = 0
    error: Optional[str] = None
    result: Optional[Dict] = None
    steps: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class JobManager:
    """
    In-memory job manager for async analysis jobs.
    Provides SSE-compatible progress streaming.
    
    Production upgrade path: replace _jobs dict with Redis-backed store
    and use Celery for actual task execution.
    """

    def __init__(self):
        self._jobs: Dict[str, JobState] = {}
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}

    def create_job(self) -> str:
        """Create a new job and return its ID."""
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = JobState(job_id=job_id)
        self._subscribers[job_id] = []
        logger.info(f"Job created: {job_id}")
        return job_id

    def get_job(self, job_id: str) -> Optional[JobState]:
        return self._jobs.get(job_id)

    async def update_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        stage: Optional[str] = None,
        progress: Optional[int] = None,
        error: Optional[str] = None,
        result: Optional[Dict] = None,
        step: Optional[Dict] = None,
    ) -> None:
        """Update job state and notify subscribers."""
        job = self._jobs.get(job_id)
        if not job:
            return

        if status:
            job.status = status
            if status == "running" and not job.started_at:
                job.started_at = datetime.utcnow()
            if status in ("completed", "failed", "cancelled"):
                job.completed_at = datetime.utcnow()

        if stage:
            job.stage = stage
        if progress is not None:
            job.progress = progress
        if error:
            job.error = error
        if result:
            job.result = result
        if step:
            job.steps.append(step)

        # Notify SSE subscribers
        event = {
            "job_id": job_id,
            "status": job.status,
            "stage": job.stage,
            "progress": job.progress,
            "error": job.error,
            "step": step,
        }
        await self._notify(job_id, event)

    async def _notify(self, job_id: str, event: Dict) -> None:
        """Push event to all SSE subscribers for this job."""
        dead_queues = []
        for q in self._subscribers.get(job_id, []):
            try:
                await q.put(event)
            except Exception:
                dead_queues.append(q)
        for q in dead_queues:
            try:
                self._subscribers[job_id].remove(q)
            except ValueError:
                pass

    async def subscribe(self, job_id: str) -> AsyncGenerator[str, None]:
        """
        SSE generator for job progress.
        Yields Server-Sent Events formatted strings.
        """
        if job_id not in self._jobs:
            yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
            return

        q: asyncio.Queue = asyncio.Queue()
        self._subscribers[job_id].append(q)

        try:
            # Send current state immediately
            job = self._jobs[job_id]
            current_state = {
                "job_id": job_id,
                "status": job.status,
                "stage": job.stage,
                "progress": job.progress,
                "error": job.error,
            }
            yield f"data: {json.dumps(current_state)}\n\n"

            # Stream updates
            while True:
                try:
                    event = await asyncio.wait_for(q.get(), timeout=30.0)
                    yield f"data: {json.dumps(event)}\n\n"

                    # Stop streaming if terminal state
                    if event.get("status") in ("completed", "failed", "cancelled"):
                        break

                except asyncio.TimeoutError:
                    # Keepalive comment
                    yield ": keepalive\n\n"

        finally:
            try:
                self._subscribers[job_id].remove(q)
            except (ValueError, KeyError):
                pass

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or running job."""
        job = self._jobs.get(job_id)
        if not job:
            return False
        if job.status in ("completed", "failed", "cancelled"):
            return False
        job.status = "cancelled"
        job.completed_at = datetime.utcnow()
        return True

    def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """Remove jobs older than max_age_hours. Returns count removed."""
        cutoff = time.time() - max_age_hours * 3600
        to_remove = [
            jid for jid, j in self._jobs.items()
            if j.created_at.timestamp() < cutoff
        ]
        for jid in to_remove:
            del self._jobs[jid]
            self._subscribers.pop(jid, None)
        return len(to_remove)


# Global job manager instance
job_manager = JobManager()
