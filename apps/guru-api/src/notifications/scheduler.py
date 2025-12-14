"""
Phase 10: Cron Scheduler

Schedules daily notification generation using APScheduler.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from src.notifications.notification_engine import run_daily_notifications

# Phase 10: Initialize scheduler
scheduler = BackgroundScheduler()


def start_scheduler():
    """
    Phase 10: Start the background scheduler for daily notifications.
    
    Schedules daily notification generation at 6:00 AM IST (00:30 UTC).
    IST = UTC + 5:30, so 6:00 AM IST = 00:30 UTC
    """
    try:
        # IST timezone
        ist = pytz.timezone('Asia/Kolkata')
        
        # Schedule daily job at 6:00 AM IST
        scheduler.add_job(
            run_daily_notifications,
            trigger=CronTrigger(
                hour=0,  # UTC hour (00:30 UTC = 6:00 AM IST)
                minute=30,
                timezone=pytz.UTC
            ),
            id='daily_notifications',
            name='Daily Horoscope Notifications',
            replace_existing=True
        )
        
        scheduler.start()
        print("✅ Daily notification scheduler started (runs at 6:00 AM IST)")
        return True
    
    except Exception as e:
        print(f"❌ Error starting scheduler: {e}")
        return False


def stop_scheduler():
    """
    Phase 10: Stop the scheduler.
    """
    try:
        scheduler.shutdown()
        print("Scheduler stopped")
        return True
    except Exception as e:
        print(f"Error stopping scheduler: {e}")
        return False


def get_scheduler_status():
    """
    Phase 10: Get scheduler status.
    
    Returns:
        Dictionary with scheduler status information
    """
    try:
        jobs = scheduler.get_jobs()
        return {
            "running": scheduler.running,
            "jobs_count": len(jobs),
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in jobs
            ]
        }
    except Exception as e:
        return {
            "running": False,
            "error": str(e)
        }

