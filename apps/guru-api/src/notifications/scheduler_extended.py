"""
Phase 12: Extended Notification Scheduler

Scheduler that runs every 5 minutes to check and deliver notifications.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from src.notifications.delivery_engine import process_due_users

# Phase 12: Extended scheduler instance
extended_scheduler = BackgroundScheduler()


def start_extended_scheduler():
    """
    Phase 12: Start the extended scheduler for multi-channel notifications.
    
    Runs every 5 minutes to check which users need notifications.
    """
    try:
        # Schedule job to run every 5 minutes
        extended_scheduler.add_job(
            process_due_users,
            trigger=CronTrigger(
                minute="*/5",  # Every 5 minutes
                timezone=pytz.UTC
            ),
            id='multi_channel_notifications',
            name='Multi-Channel Notification Delivery',
            replace_existing=True
        )
        
        extended_scheduler.start()
        print("✅ Extended notification scheduler started (runs every 5 minutes)")
        return True
    
    except Exception as e:
        print(f"❌ Error starting extended scheduler: {e}")
        return False


def stop_extended_scheduler():
    """
    Phase 12: Stop the extended scheduler.
    """
    try:
        extended_scheduler.shutdown()
        print("Extended scheduler stopped")
        return True
    except Exception as e:
        print(f"Error stopping extended scheduler: {e}")
        return False


def get_extended_scheduler_status():
    """
    Phase 12: Get extended scheduler status.
    
    Returns:
        Dictionary with scheduler status
    """
    try:
        jobs = extended_scheduler.get_jobs()
        return {
            "running": extended_scheduler.running,
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

