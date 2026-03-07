"""
APScheduler configuration for hourly Excel report.
Starts automatically when Django boots.
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.jobstores import DjangoJobStore

logger = logging.getLogger(__name__)

_scheduler = None


def start_scheduler():
    """Start the background scheduler with the hourly report job."""
    global _scheduler

    if _scheduler is not None:
        return  # Already started

    from .reports import email_report_to_owner

    _scheduler = BackgroundScheduler()
    _scheduler.add_jobstore(DjangoJobStore(), "default")

    _scheduler.add_job(
        email_report_to_owner,
        trigger=IntervalTrigger(hours=1),
        id="hourly_excel_report",
        name="Send hourly Excel report to owner",
        replace_existing=True,
        max_instances=1,
    )

    _scheduler.start()
    logger.info("[Scheduler] Started — hourly Excel report job registered.")
