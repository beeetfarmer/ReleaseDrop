"""
Pydantic schemas for Release API responses.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class ReleaseResponse(BaseModel):
    """Schema for release response with all details."""

    id: int
    spotify_id: str
    name: str
    release_type: str
    release_date: str
    spotify_url: str
    image_url: Optional[str] = None
    total_tracks: int
    is_new: bool
    notified: bool
    discovered_at: datetime

    # Jellyfin integration fields
    in_jellyfin: Optional[bool] = None
    jellyfin_match_type: Optional[str] = None
    jellyfin_match_confidence: Optional[float] = None
    jellyfin_album_id: Optional[str] = None

    # Plex integration fields
    in_plex: Optional[bool] = None
    plex_match_type: Optional[str] = None
    plex_match_confidence: Optional[float] = None
    plex_album_id: Optional[str] = None

    # Track information
    tracks: Optional[List[Dict[str, Any]]] = None
    available_tracks: Optional[List[str]] = None
    missing_tracks: Optional[List[str]] = None
    plex_available_tracks: Optional[List[str]] = None
    plex_missing_tracks: Optional[List[str]] = None

    # Artist information
    artist_id: int
    artist_name: Optional[str] = None

    class Config:
        from_attributes = True
