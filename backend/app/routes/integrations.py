"""
Integration API routes for Last.fm and Jellyfin.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
import httpx

from ..database import get_db
from ..models import Artist, Release
from ..services.lastfm_service import LastFmService
from ..services.jellyfin_service import JellyfinService
from ..services.plex_service import PlexService
from ..services.spotify_service import SpotifyService
from ..services.gotify_service import GotifyService
from ..services.ntfy_service import NtfyService
from ..config import get_settings

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/status")
async def check_integration_status():
    """
    Check connectivity status of all integrations.
    Returns which services are available and configured.
    """
    settings = get_settings()
    jellyfin_available = False
    plex_available = False
    gotify_configured = False
    ntfy_configured = False
    errors = {}

    # Check Jellyfin
    try:
        jellyfin = JellyfinService()
        if jellyfin.base_url and jellyfin.api_key:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{jellyfin.base_url}/System/Info",
                    headers=jellyfin.headers
                )
                if response.status_code == 200:
                    jellyfin_available = True
    except Exception as e:
        errors["jellyfin"] = str(e)

    # Check Plex
    try:
        plex = PlexService()
        if plex.base_url and plex.token:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{plex.base_url}/",
                    headers=plex.headers
                )
                if response.status_code == 200:
                    plex_available = True
    except Exception as e:
        errors["plex"] = str(e)

    # Check Gotify configuration
    gotify_configured = bool(settings.gotify_url and settings.gotify_token)

    # Check Ntfy configuration
    ntfy_configured = bool(settings.ntfy_url and settings.ntfy_topic)

    return {
        "jellyfin_available": jellyfin_available,
        "plex_available": plex_available,
        "gotify_configured": gotify_configured,
        "ntfy_configured": ntfy_configured,
        "errors": errors
    }


@router.post("/gotify/test")
async def test_gotify_connection():
    """
    Send a test notification via Gotify.

    Returns:
        Success status and message
    """
    settings = get_settings()

    if not settings.gotify_url or not settings.gotify_token:
        raise HTTPException(
            status_code=400,
            detail="Gotify is not configured. Please set GOTIFY_URL and GOTIFY_TOKEN."
        )

    try:
        gotify = GotifyService()
        success = await gotify.test_connection()

        if success:
            return {"success": True, "message": "Gotify test notification sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send Gotify notification")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gotify test failed: {str(e)}")


@router.post("/ntfy/test")
async def test_ntfy_connection():
    """
    Send a test notification via ntfy.

    Returns:
        Success status and message
    """
    settings = get_settings()

    if not settings.ntfy_url or not settings.ntfy_topic:
        raise HTTPException(
            status_code=400,
            detail="Ntfy is not configured. Please set NTFY_URL and NTFY_TOPIC."
        )

    try:
        ntfy = NtfyService()
        success = await ntfy.test_connection()

        if success:
            return {"success": True, "message": "Ntfy test notification sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send ntfy notification")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ntfy test failed: {str(e)}")


# Pydantic models for requests/responses
class LastFmImportRequest(BaseModel):
    period: str = "overall"  # "7day", "1month", "3month", "6month", "12month", or "overall"
    limit: int = 50


class LastFmImportResponse(BaseModel):
    total_artists: int
    new_artists: int
    existing_artists: int
    artists_added: List[str]


class JellyfinCheckResponse(BaseModel):
    release_id: int
    in_library: bool
    match_type: str
    match_confidence: float
    available_tracks: List[str]
    missing_tracks: List[str]


class PlexCheckResponse(BaseModel):
    release_id: int
    in_library: bool
    match_type: str
    match_confidence: float
    available_tracks: List[str]
    missing_tracks: List[str]


@router.post("/lastfm/import", response_model=LastFmImportResponse)
async def import_lastfm_artists(
    request: LastFmImportRequest,
    db: Session = Depends(get_db)
):
    """
    Import top artists from Last.fm and automatically follow them.

    Args:
        request: Import configuration (period and limit)

    Returns:
        Summary of import operation
    """
    try:
        lastfm = LastFmService()
        spotify = SpotifyService()

        # Get top artists from Last.fm
        lastfm_artists = await lastfm.get_top_artists(request.period, request.limit)
        print(f"Processing {len(lastfm_artists)} artists from Last.fm...")

        new_count = 0
        existing_count = 0
        artists_added = []
        skipped = []

        for idx, lastfm_artist in enumerate(lastfm_artists, 1):
            artist_name = lastfm_artist["name"]
            print(f"   [{idx}/{len(lastfm_artists)}] Processing: {artist_name}")

            try:
                # Check if artist already exists by name
                existing = db.query(Artist).filter(Artist.name.ilike(artist_name)).first()

                if existing:
                    print(f"      Already following (by name)")
                    existing_count += 1
                    continue

                # Search for artist on Spotify
                spotify_results = await spotify.search_artists(artist_name, limit=1)

                if not spotify_results:
                    print(f"      Not found on Spotify")
                    skipped.append(artist_name)
                    continue

                spotify_artist = spotify_results[0]
                print(f"      Found on Spotify: {spotify_artist.name}")

                # Check if artist already exists by Spotify ID (name might differ)
                existing_by_id = db.query(Artist).filter(
                    Artist.spotify_id == spotify_artist.spotify_id
                ).first()

                if existing_by_id:
                    print(f"Already following as '{existing_by_id.name}' (same Spotify ID)")
                    existing_count += 1
                    continue

                # Create new artist
                new_artist = Artist(
                    spotify_id=spotify_artist.spotify_id,
                    name=spotify_artist.name,
                    spotify_url=spotify_artist.spotify_url,
                    image_url=spotify_artist.image_url
                )

                db.add(new_artist)
                db.flush()  # Flush to database to detect duplicates immediately
                artists_added.append(spotify_artist.name)
                new_count += 1

            except Exception as e:
                print(f"Error processing {artist_name}: {e}")
                skipped.append(artist_name)
                continue

        print(f"Committing {new_count} new artists to database...")
        db.commit()
        print(f"Import complete!")
        print(f"   New: {new_count}, Existing: {existing_count}, Skipped: {len(skipped)}")

        return LastFmImportResponse(
            total_artists=len(lastfm_artists),
            new_artists=new_count,
            existing_artists=existing_count,
            artists_added=artists_added
        )

    except Exception as e:
        import traceback
        print(f"FATAL ERROR during Last.fm import:")
        print(traceback.format_exc())
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to import Last.fm artists: {str(e)}")


@router.post("/jellyfin/check/{release_id}", response_model=JellyfinCheckResponse)
async def check_jellyfin_library(
    release_id: int,
    db: Session = Depends(get_db)
):
    """
    Check if a release exists in Jellyfin library.
    Updates the release record with Jellyfin status.

    Args:
        release_id: Database ID of the release

    Returns:
        Jellyfin library status information
    """
    release = db.query(Release).filter(Release.id == release_id).first()

    if not release:
        raise HTTPException(status_code=404, detail="Release not found")

    try:
        jellyfin = JellyfinService()
        spotify = SpotifyService()

        # Get tracks from Spotify
        spotify_tracks = await spotify.get_album_tracks(release.spotify_id)

        # Check in Jellyfin
        jellyfin_status = await jellyfin.check_album_in_library(
            release.name,
            release.artist.name,
            spotify_tracks
        )

        # Update release record
        release.in_jellyfin = jellyfin_status["in_library"]
        release.jellyfin_match_type = jellyfin_status["match_type"]
        release.jellyfin_match_confidence = jellyfin_status["match_confidence"]
        release.jellyfin_album_id = jellyfin_status.get("jellyfin_album_id")
        release.tracks = spotify_tracks
        release.available_tracks = jellyfin_status["available_tracks"]
        release.missing_tracks = jellyfin_status["missing_tracks"]

        db.commit()

        return JellyfinCheckResponse(
            release_id=release.id,
            in_library=jellyfin_status["in_library"],
            match_type=jellyfin_status["match_type"],
            match_confidence=jellyfin_status["match_confidence"],
            available_tracks=jellyfin_status["available_tracks"],
            missing_tracks=jellyfin_status["missing_tracks"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check Jellyfin library: {str(e)}")


@router.post("/jellyfin/check-all")
async def check_all_jellyfin(db: Session = Depends(get_db)):
    """
    Check all releases against Jellyfin library.
    Useful for initial setup or refresh.

    Returns:
        Summary of checked releases
    """
    releases = db.query(Release).all()

    jellyfin = JellyfinService()
    spotify = SpotifyService()

    checked_count = 0
    in_library_count = 0
    errors = []

    for release in releases:
        try:
            # Get tracks from Spotify
            spotify_tracks = await spotify.get_album_tracks(release.spotify_id)

            # Check in Jellyfin
            jellyfin_status = await jellyfin.check_album_in_library(
                release.name,
                release.artist.name,
                spotify_tracks
            )

            # Update release record
            release.in_jellyfin = jellyfin_status["in_library"]
            release.jellyfin_match_type = jellyfin_status["match_type"]
            release.jellyfin_match_confidence = jellyfin_status["match_confidence"]
            release.jellyfin_album_id = jellyfin_status.get("jellyfin_album_id")
            release.tracks = spotify_tracks
            release.available_tracks = jellyfin_status["available_tracks"]
            release.missing_tracks = jellyfin_status["missing_tracks"]

            if jellyfin_status["in_library"]:
                in_library_count += 1

            checked_count += 1

        except Exception as e:
            errors.append(f"Error checking {release.name}: {str(e)}")

    db.commit()

    return {
        "total_releases": len(releases),
        "checked": checked_count,
        "in_library": in_library_count,
        "not_in_library": checked_count - in_library_count,
        "errors": errors
    }


@router.post("/plex/check/{release_id}", response_model=PlexCheckResponse)
async def check_plex_library(
    release_id: int,
    db: Session = Depends(get_db)
):
    """
    Check if a release exists in Plex library.
    Updates the release record with Plex status.

    Args:
        release_id: Database ID of the release

    Returns:
        Plex library status information
    """
    release = db.query(Release).filter(Release.id == release_id).first()

    if not release:
        raise HTTPException(status_code=404, detail="Release not found")

    try:
        plex = PlexService()
        spotify = SpotifyService()

        # Get tracks from Spotify
        spotify_tracks = await spotify.get_album_tracks(release.spotify_id)

        # Check in Plex
        plex_status = await plex.check_album_in_library(
            release.name,
            release.artist.name,
            spotify_tracks
        )

        # Update release record
        release.in_plex = plex_status["in_library"]
        release.plex_match_type = plex_status["match_type"]
        release.plex_match_confidence = plex_status["match_confidence"]
        release.plex_album_id = plex_status.get("plex_album_id")
        release.tracks = spotify_tracks
        release.plex_available_tracks = plex_status["available_tracks"]
        release.plex_missing_tracks = plex_status["missing_tracks"]

        db.commit()

        return PlexCheckResponse(
            release_id=release.id,
            in_library=plex_status["in_library"],
            match_type=plex_status["match_type"],
            match_confidence=plex_status["match_confidence"],
            available_tracks=plex_status["available_tracks"],
            missing_tracks=plex_status["missing_tracks"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check Plex library: {str(e)}")


@router.post("/plex/check-all")
async def check_all_plex(db: Session = Depends(get_db)):
    """
    Check all releases against Plex library.
    Useful for initial setup or refresh.

    Returns:
        Summary of checked releases
    """
    releases = db.query(Release).all()

    plex = PlexService()
    spotify = SpotifyService()

    checked_count = 0
    in_library_count = 0
    errors = []

    for release in releases:
        try:
            # Get tracks from Spotify
            spotify_tracks = await spotify.get_album_tracks(release.spotify_id)

            # Check in Plex
            plex_status = await plex.check_album_in_library(
                release.name,
                release.artist.name,
                spotify_tracks
            )

            # Update release record
            release.in_plex = plex_status["in_library"]
            release.plex_match_type = plex_status["match_type"]
            release.plex_match_confidence = plex_status["match_confidence"]
            release.plex_album_id = plex_status.get("plex_album_id")
            release.tracks = spotify_tracks
            release.plex_available_tracks = plex_status["available_tracks"]
            release.plex_missing_tracks = plex_status["missing_tracks"]

            if plex_status["in_library"]:
                in_library_count += 1

            checked_count += 1

        except Exception as e:
            errors.append(f"Error checking {release.name}: {str(e)}")

    db.commit()

    return {
        "total_releases": len(releases),
        "checked": checked_count,
        "in_library": in_library_count,
        "not_in_library": checked_count - in_library_count,
        "errors": errors
    }
