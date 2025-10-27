"""
Release API routes for fetching and managing music releases.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any

from ..database import get_db
from ..models import Release, Artist
from ..schemas.release import ReleaseResponse
from ..services.spotify_service import SpotifyService

router = APIRouter(prefix="/releases", tags=["releases"])


@router.get("/", response_model=List[ReleaseResponse])
async def get_all_releases(
    only_new: bool = Query(False, description="Show only new releases"),
    artist_id: Optional[int] = Query(None, description="Filter by artist ID"),
    db: Session = Depends(get_db)
):
    """
    Get all releases with optional filtering.

    Args:
        only_new: If True, only return releases marked as new
        artist_id: If provided, only return releases from this artist

    Returns:
        List of releases sorted by release date (descending)
    """
    query = db.query(Release).options(joinedload(Release.artist))

    # Apply filters
    if only_new:
        query = query.filter(Release.is_new == True)

    if artist_id:
        query = query.filter(Release.artist_id == artist_id)

    # Sort by release date descending
    releases = query.order_by(Release.release_date.desc()).all()

    # Add artist name to response
    response_data = []
    for release in releases:
        release_dict = ReleaseResponse.model_validate(release)
        release_dict.artist_name = release.artist.name if release.artist else None
        response_data.append(release_dict)

    return response_data


@router.get("/latest", response_model=List[ReleaseResponse])
async def get_latest_releases(
    limit: Optional[int] = Query(None, ge=1, description="Number of releases to return (optional, returns all if not specified)"),
    db: Session = Depends(get_db)
):
    """
    Get the latest releases across all followed artists.
    Only returns releases from the last N months (configured in RELEASE_MONTHS_BACK).

    Args:
        limit: Maximum number of releases to return (optional, returns all if not specified)

    Returns:
        List of most recent releases within the configured date range
    """
    from datetime import datetime, timedelta
    from ..config import get_settings

    settings = get_settings()

    # Calculate cutoff date based on configured months back
    cutoff_date = datetime.now() - timedelta(days=settings.release_months_back * 30)
    cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')

    query = (
        db.query(Release)
        .options(joinedload(Release.artist))
        .filter(Release.release_date >= cutoff_date_str)  # Only releases within date range
        .order_by(Release.release_date.desc())
    )

    # Only apply limit if specified
    if limit:
        query = query.limit(limit)

    releases = query.all()

    # Add artist name to response
    response_data = []
    for release in releases:
        release_dict = ReleaseResponse.model_validate(release)
        release_dict.artist_name = release.artist.name if release.artist else None
        response_data.append(release_dict)

    return response_data


@router.post("/{release_id}/mark-seen")
async def mark_release_as_seen(
    release_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark a release as seen (no longer new).

    Args:
        release_id: Database ID of the release

    Returns:
        Success message
    """
    release = db.query(Release).filter(Release.id == release_id).first()

    if not release:
        return {"error": "Release not found"}

    release.is_new = False
    db.commit()

    return {"message": "Release marked as seen"}


@router.post("/mark-all-seen")
async def mark_all_releases_as_seen(db: Session = Depends(get_db)):
    """
    Mark all releases as seen.

    Returns:
        Count of releases updated
    """
    count = db.query(Release).filter(Release.is_new == True).update({"is_new": False})
    db.commit()

    return {"message": f"Marked {count} releases as seen"}


@router.get("/stats")
async def get_release_stats(db: Session = Depends(get_db)):
    """
    Get statistics about releases within the configured time range.

    Returns:
        Dictionary with various statistics
    """
    from datetime import datetime, timedelta
    from ..config import get_settings

    settings = get_settings()

    # Calculate cutoff date based on configured months back
    cutoff_date = datetime.now() - timedelta(days=settings.release_months_back * 30)
    cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')

    # Only count releases within the configured time range
    total_releases = db.query(Release).filter(Release.release_date >= cutoff_date_str).count()
    new_releases = db.query(Release).filter(Release.is_new == True, Release.release_date >= cutoff_date_str).count()
    total_artists = db.query(Artist).count()

    # Count by type (within time range)
    albums = db.query(Release).filter(Release.release_type == "album", Release.release_date >= cutoff_date_str).count()
    singles = db.query(Release).filter(Release.release_type == "single", Release.release_date >= cutoff_date_str).count()
    eps = db.query(Release).filter(Release.release_type == "ep", Release.release_date >= cutoff_date_str).count()

    return {
        "total_releases": total_releases,
        "new_releases": new_releases,
        "total_artists": total_artists,
        "by_type": {
            "albums": albums,
            "singles": singles,
            "eps": eps
        }
    }


@router.get("/{release_id}/tracks", response_model=List[Dict[str, Any]])
async def get_release_tracks(
    release_id: int,
    db: Session = Depends(get_db)
):
    """
    Fetch tracks for a specific release from Spotify.
    Caches the tracks in the database for future use.

    Args:
        release_id: Database ID of the release

    Returns:
        List of track information
    """
    release = db.query(Release).filter(Release.id == release_id).first()

    if not release:
        return {"error": "Release not found"}

    # If tracks are already cached, return them
    if release.tracks:
        return release.tracks

    # Fetch tracks from Spotify
    spotify = SpotifyService()
    tracks = await spotify.get_album_tracks(release.spotify_id)

    # Cache tracks in database
    release.tracks = tracks
    db.commit()

    return tracks
