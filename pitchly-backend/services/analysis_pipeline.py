import logging
import time

from services.session_store import (
    create_demo_result,
    mark_job_complete,
    mark_job_error,
    update_session_status,
)

logger = logging.getLogger(__name__)


def run_analysis_pipeline(job_id: str, session_id: str, mode: str) -> None:
    # Responsibility: Run asynchronous analysis after upload without blocking requests.
    try:
        logger.info("Analysis started: job_id=%s session_id=%s", job_id, session_id)
        time.sleep(1)
        create_demo_result(session_id, mode)
        update_session_status(session_id, "complete")
        mark_job_complete(job_id, session_id)
        logger.info("Analysis complete: job_id=%s", job_id)
    except Exception as exc:
        logger.exception("Analysis failed: job_id=%s", job_id)
        update_session_status(session_id, "error")
        mark_job_error(job_id, session_id, str(exc))