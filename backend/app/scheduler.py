"""
APScheduler configuration for daily release checks.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from zoneinfo import ZoneInfo

from .database import SessionLocal
from .models import Artist, Release
from .services.spotify_service import SpotifyService
from .services.gotify_service import GotifyService
from .services.ntfy_service import NtfyService
from .config import get_settings

settings = get_settings()
scheduler = BackgroundScheduler()


async def check_for_new_releases():
    """
    Background job to check for new releases from all followed artists.
    Runs daily at configured time.
    """
    print(f"[{datetime.now()}] Starting daily release check...")

    db = SessionLocal()
    try:
        # Get all followed artists
        artists = db.query(Artist).all()

        if not artists:
            print("No artists to check")
            return

        spotify = SpotifyService()

        # Initialize notification services if configured
        gotify = None
        ntfy = None
        if settings.gotify_url and settings.gotify_token:
            gotify = GotifyService()
        if settings.ntfy_url and settings.ntfy_topic:
            ntfy = NtfyService()

        total_new = 0

        for artist in artists:
            print(f"Checking releases for: {artist.name}")

            # Fetch releases from Spotify
            releases_data = await spotify.get_artist_releases(
                artist.spotify_id,
                settings.release_months_back
            )

            # Track new releases for this artist
            new_releases = []

            for release_data in releases_data:
                # Check if release already exists in database
                existing = db.query(Release).filter(
                    Release.spotify_id == release_data['spotify_id']
                ).first()

                if not existing:
                    # Create new release entry
                    new_release = Release(
                        spotify_id=release_data['spotify_id'],
                        name=release_data['name'],
                        release_type=release_data['release_type'],
                        release_date=release_data['release_date'],
                        spotify_url=release_data['spotify_url'],
                        image_url=release_data['image_url'],
                        total_tracks=release_data['total_tracks'],
                        artist_id=artist.id,
                        is_new=True,
                        notified=False
                    )
                    db.add(new_release)
                    db.flush()  # Flush to make this release visible to subsequent queries
                    new_releases.append(release_data)
                    total_new += 1

            # Update artist's last checked timestamp
            artist.last_checked = datetime.utcnow()

            # Send notification if there are new releases
            if new_releases:
                print(f"  Found {len(new_releases)} new release(s)")

                # Send notification to configured services
                if gotify:
                    await gotify.send_release_notification(
                        artist.name,
                        new_releases
                    )
                if ntfy:
                    await ntfy.send_release_notification(
                        artist.name,
                        new_releases
                    )

                # Mark releases as notified
                for release_data in new_releases:
                    release = db.query(Release).filter(
                        Release.spotify_id == release_data['spotify_id']
                    ).first()
                    if release:
                        release.notified = True

        # Commit all changes
        db.commit()

        print(f"Release check complete. Found {total_new} new release(s) total.")

    except Exception as e:
        print(f"Error during release check: {e}")
        db.rollback()

    finally:
        db.close()


def run_sync_check():
    """
    Synchronous wrapper for the async check function.
    Required for APScheduler compatibility.
    """
    import asyncio

    # Create new event loop for the background thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(check_for_new_releases())
    finally:
        loop.close()


def start_scheduler():
    """
    Start the background scheduler for daily checks.
    """
    # Parse the check time from settings (format: HH:MM)
    try:
        hour, minute = map(int, settings.release_check_time.split(':'))
    except:
        hour, minute = 9, 0  # Default to 9:00 AM

    # Get timezone from settings
    try:
        tz = ZoneInfo(settings.timezone)
    except Exception as e:
        print(f"Invalid timezone '{settings.timezone}', falling back to UTC")
        tz = ZoneInfo("UTC")

    # Add job to run daily at specified time
    scheduler.add_job(
        run_sync_check,
        trigger=CronTrigger(hour=hour, minute=minute, timezone=tz),
        id='daily_release_check',
        name='Check for new releases',
        replace_existing=True
    )

    # Start the scheduler
    scheduler.start()
    print(f"Scheduler configured to run daily at {hour:02d}:{minute:02d} {settings.timezone}")


def stop_scheduler():
    """
    Stop the background scheduler.
    """
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler stopped")
