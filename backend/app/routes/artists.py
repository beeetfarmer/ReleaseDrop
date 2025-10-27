"""
Artist API routes for searching, following, and managing artists.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..models import Artist
from ..schemas.artist import ArtistCreate, ArtistResponse, ArtistSearch
from ..services.spotify_service import SpotifyService

router = APIRouter(prefix="/artists", tags=["artists"])


@router.get("/search", response_model=List[ArtistSearch])
async def search_artists(
    query: str = Query(..., min_length=1, description="Search query for artists"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return")
):
    """
    Search for artists on Spotify.

    Args:
        query: Artist name or search term
        limit: Maximum number of results (1-50)

    Returns:
        List of matching artists from Spotify
    """
    spotify = SpotifyService()
    results = await spotify.search_artists(query, limit)
    return results


@router.post("/follow", response_model=ArtistResponse)
async def follow_artist(
    artist_data: ArtistCreate,
    db: Session = Depends(get_db)
):
    """
    Add an artist to the follow list.

    Args:
        artist_data: Artist information from Spotify

    Returns:
        Created artist record

    Raises:
        HTTPException: If artist is already followed
    """
    # Check if artist already exists
    existing = db.query(Artist).filter(Artist.spotify_id == artist_data.spotify_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Artist is already being followed")

    # Create new artist
    new_artist = Artist(
        spotify_id=artist_data.spotify_id,
        name=artist_data.name,
        spotify_url=artist_data.spotify_url,
        image_url=artist_data.image_url
    )

    db.add(new_artist)
    db.commit()
    db.refresh(new_artist)

    return new_artist


@router.get("/followed", response_model=List[ArtistResponse])
async def get_followed_artists(db: Session = Depends(get_db)):
    """
    Get all followed artists.

    Returns:
        List of all artists in the follow list
    """
    artists = db.query(Artist).order_by(Artist.name).all()
    return artists


@router.delete("/{artist_id}")
async def unfollow_artist(
    artist_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove an artist from the follow list.

    Args:
        artist_id: Database ID of the artist to unfollow

    Returns:
        Success message

    Raises:
        HTTPException: If artist not found
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()

    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    db.delete(artist)
    db.commit()

    return {"message": f"Unfollowed {artist.name}"}


@router.post("/{artist_id}/refresh")
async def refresh_artist_releases(
    artist_id: int,
    db: Session = Depends(get_db)
):
    """
    Manually refresh releases for a specific artist.

    Args:
        artist_id: Database ID of the artist

    Returns:
        Summary of new releases found

    Raises:
        HTTPException: If artist not found
    """
    from ..models import Release
    from ..config import get_settings
    from ..services.gotify_service import GotifyService
    from ..services.ntfy_service import NtfyService

    settings = get_settings()

    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    # Fetch releases from Spotify
    spotify = SpotifyService()
    releases_data = await spotify.get_artist_releases(
        artist.spotify_id,
        settings.release_months_back
    )

    new_count = 0
    new_releases = []

    for release_data in releases_data:
        # Check if release already exists
        existing = db.query(Release).filter(
            Release.spotify_id == release_data['spotify_id']
        ).first()

        if not existing:
            # Create new release
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
            new_count += 1

    # Update last checked timestamp
    artist.last_checked = datetime.utcnow()

    # Send notification if there are new releases
    if new_releases:
        # Send to configured notification services
        if settings.gotify_url and settings.gotify_token:
            gotify = GotifyService()
            await gotify.send_release_notification(
                artist.name,
                new_releases
            )
        if settings.ntfy_url and settings.ntfy_topic:
            ntfy = NtfyService()
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

    db.commit()

    return {
        "artist": artist.name,
        "new_releases": new_count,
        "total_releases": len(releases_data)
    }


@router.get("/{artist_id}/releases")
async def get_artist_all_releases(
    artist_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all releases for a specific artist from database and fetch any new ones from Spotify.

    Args:
        artist_id: Database ID of the artist

    Returns:
        All releases for the artist, including recent and older ones

    Raises:
        HTTPException: If artist not found
    """
    from ..models import Release
    from ..config import get_settings
    from ..schemas.release import ReleaseResponse

    settings = get_settings()

    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    # Fetch ALL releases from Spotify (every release ever)
    spotify = SpotifyService()

    # Get ALL releases by setting a very large months_back value
    # This will fetch all available releases from Spotify
    releases_data = await spotify.get_artist_releases(
        artist.spotify_id,
        months_back=1200  # 100 years - effectively gets all releases
    )

    # Sync with database - add any new releases
    for release_data in releases_data:
        existing = db.query(Release).filter(
            Release.spotify_id == release_data['spotify_id']
        ).first()

        if not existing:
            new_release = Release(
                spotify_id=release_data['spotify_id'],
                name=release_data['name'],
                release_type=release_data['release_type'],
                release_date=release_data['release_date'],
                spotify_url=release_data['spotify_url'],
                image_url=release_data['image_url'],
                total_tracks=release_data['total_tracks'],
                artist_id=artist.id,
                is_new=False,  # These are fetched on-demand, not from scheduled check
                notified=False
            )
            db.add(new_release)
            db.flush()  # Flush to make this release visible to subsequent queries

    db.commit()

    # Get all releases for this artist from database
    releases = db.query(Release).filter(
        Release.artist_id == artist_id
    ).order_by(Release.release_date.desc()).all()

    # Return releases with artist info included
    return {
        "artist": artist,
        "releases": releases,
        "release_months_back": settings.release_months_back
    }
