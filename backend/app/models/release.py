"""
Release database model.
Stores album/single/EP releases from Spotify.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Release(Base):
    """Model for storing music releases."""

    __tablename__ = "releases"

    id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    release_type = Column(String, nullable=False)  # album, single, ep
    release_date = Column(String, nullable=False)  # Format: YYYY-MM-DD
    spotify_url = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    total_tracks = Column(Integer, default=0)

    # Foreign key to artist
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)

    # Tracking fields
    is_new = Column(Boolean, default=True)
    notified = Column(Boolean, default=False)
    discovered_at = Column(DateTime, default=datetime.utcnow)

    # Phase 2: Jellyfin integration fields
    in_jellyfin = Column(Boolean, default=None, nullable=True)
    jellyfin_match_type = Column(String, nullable=True)  # "exact" | "similar" | "none"
    jellyfin_match_confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    jellyfin_album_id = Column(String, nullable=True)

    # Plex integration fields
    in_plex = Column(Boolean, default=None, nullable=True)
    plex_match_type = Column(String, nullable=True)  # "exact" | "similar" | "none"
    plex_match_confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    plex_album_id = Column(String, nullable=True)

    # Track information (stored as JSON)
    tracks = Column(JSON, nullable=True)  # List of track objects
    available_tracks = Column(JSON, nullable=True)  # Tracks available in Jellyfin
    missing_tracks = Column(JSON, nullable=True)  # Tracks missing from Jellyfin
    plex_available_tracks = Column(JSON, nullable=True)  # Tracks available in Plex
    plex_missing_tracks = Column(JSON, nullable=True)  # Tracks missing from Plex

    # Relationship to artist
    artist = relationship("Artist", back_populates="releases")

    def __repr__(self):
        return f"<Release {self.name} by {self.artist.name if self.artist else 'Unknown'}>"
