"""
Cleanup script to remove releases outside the configured date range.
This removes releases older than RELEASE_MONTHS_BACK months.
"""
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.release import Release
from app.config import get_settings


def cleanup_old_releases():
    """Remove releases older than the configured months_back setting."""
    db = SessionLocal()
    settings = get_settings()

    try:
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=settings.release_months_back * 30)
        cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')

        print(f"Configured to keep releases from the last {settings.release_months_back} months")
        print(f"Cutoff date: {cutoff_date_str}")
        print(f"Releases OLDER than this will be removed\n")

        # Find old releases
        old_releases = db.query(Release).filter(
            Release.release_date < cutoff_date_str
        ).all()

        if not old_releases:
            print("No old releases found. Database is clean!")
            return

        print(f"Found {len(old_releases)} old release(s):\n")

        # Group by artist for display
        releases_by_artist = {}
        for release in old_releases:
            artist_name = release.artist.name if release.artist else "Unknown"
            if artist_name not in releases_by_artist:
                releases_by_artist[artist_name] = []
            releases_by_artist[artist_name].append(release)

        # Display what will be removed
        for artist_name, releases in releases_by_artist.items():
            print(f"\n{artist_name}:")
            for release in releases:
                print(f"  - {release.name} ({release.release_type}) - {release.release_date}")

        # Confirm deletion
        print(f"\n This will permanently delete {len(old_releases)} release(s) from your database.")
        response = input("Do you want to proceed? (yes/no): ")

        if response.lower() not in ['yes', 'y']:
            print("Cleanup cancelled.")
            return

        # Delete old releases
        count = 0
        for release in old_releases:
            db.delete(release)
            count += 1

        db.commit()

        print(f"\nSuccessfully removed {count} old release(s)!")
        print(f"Tip: Refresh your browser to see the updated list.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    print("Release Cleanup Script\n")

    # Check for --yes flag
    if len(sys.argv) > 1 and sys.argv[1] in ['--yes', '-y']:
        # Modify cleanup function to auto-confirm
        original_input = __builtins__.input
        __builtins__.input = lambda _: "yes"
        cleanup_old_releases()
        __builtins__.input = original_input
    else:
        cleanup_old_releases()
