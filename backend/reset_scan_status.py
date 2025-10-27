"""
Reset scan status for releases.
Sets in_jellyfin and in_plex to NULL for releases that haven't been scanned.
A release is considered "not scanned" if:
- in_jellyfin/in_plex is False AND
- jellyfin_match_type/plex_match_type is NULL (meaning no scan was ever performed)
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from app.models.release import Release


def reset_scan_status():
    """Reset scan status to NULL for unscanned releases."""
    db = SessionLocal()

    try:
        # Find releases that have False but were never actually scanned
        jellyfin_reset = db.query(Release).filter(
            Release.in_jellyfin == False,
            Release.jellyfin_match_type == None
        ).update({
            "in_jellyfin": None
        })

        plex_reset = db.query(Release).filter(
            Release.in_plex == False,
            Release.plex_match_type == None
        ).update({
            "in_plex": None
        })

        db.commit()

        print(f"Reset scan status:")
        print(f"   - Jellyfin: {jellyfin_reset} releases set to NULL")
        print(f"   - Plex: {plex_reset} releases set to NULL")
        print(f"\nReleases that were actually scanned (with match_type set) were not affected.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Resetting scan status for unscanned releases...\n")
    reset_scan_status()
