"""
Plex API integration service.
Checks if albums exist in Plex library and tracks availability.
"""
import httpx
from typing import Dict, List, Optional
from difflib import SequenceMatcher
from ..config import get_settings


class PlexService:
    """Service for interacting with Plex API."""

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.plex_url.rstrip('/')
        self.token = settings.plex_token
        self.headers = {
            "X-Plex-Token": self.token,
            "Accept": "application/json"
        }

    def _similarity_ratio(self, str1: str, str2: str) -> float:
        """Calculate similarity ratio between two strings (0.0 to 1.0)."""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    async def get_music_libraries(self) -> List[Dict]:
        """
        Get all music libraries from Plex server.

        Returns:
            List of music library sections
        """
        if not self.base_url or not self.token:
            return []

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/library/sections",
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()

                # Filter for music libraries only
                music_libraries = []
                for section in data.get("MediaContainer", {}).get("Directory", []):
                    if section.get("type") == "artist":
                        music_libraries.append({
                            "key": section.get("key"),
                            "title": section.get("title")
                        })

                return music_libraries

            except Exception as e:
                print(f"Error fetching Plex music libraries: {e}")
                return []

    async def search_artist_in_library(self, library_key: str, artist_name: str) -> Optional[Dict]:
        """
        Search for an artist in a specific Plex library.

        Args:
            library_key: Plex library section key
            artist_name: Name of the artist to search

        Returns:
            Artist data if found, None otherwise
        """
        if not self.base_url or not self.token:
            return None

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/library/sections/{library_key}/all",
                    headers=self.headers,
                    params={"type": 8}  # Type 8 = Artist
                )
                response.raise_for_status()
                data = response.json()

                artists = data.get("MediaContainer", {}).get("Metadata", [])

                # Try exact match first
                for artist in artists:
                    if artist.get("title", "").lower() == artist_name.lower():
                        return artist

                # Try similarity match
                best_match = None
                best_ratio = 0.0
                for artist in artists:
                    ratio = self._similarity_ratio(artist.get("title", ""), artist_name)
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_match = artist

                if best_ratio >= 0.85:
                    return best_match

                return None

            except Exception as e:
                print(f"Error searching for artist in Plex library {library_key}: {e}")
                return None

    async def get_artist_albums(self, library_key: str, artist_name: str) -> List[Dict]:
        """
        Get all albums for a specific artist in Plex.
        Searches for albums in the library section by artist name.

        Args:
            library_key: Plex library section key
            artist_name: Name of the artist

        Returns:
            List of album data
        """
        if not self.base_url or not self.token:
            return []

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Get all albums from the library section (type 9 = Album)
                response = await client.get(
                    f"{self.base_url}/library/sections/{library_key}/all",
                    headers=self.headers,
                    params={"type": 9}  # Type 9 = Album
                )
                response.raise_for_status()
                data = response.json()

                all_albums = data.get("MediaContainer", {}).get("Metadata", [])

                # Filter albums by artist name (exact or fuzzy match)
                artist_albums = []
                artist_name_lower = artist_name.lower()

                for album in all_albums:
                    # Check if artist name matches
                    album_artist = album.get("parentTitle", "").lower()

                    # Use exact match or similarity ratio
                    if album_artist == artist_name_lower:
                        # Exact match
                        artist_albums.append(album)
                    elif self._similarity_ratio(album_artist, artist_name) >= 0.85:
                        # Fuzzy match with high confidence
                        artist_albums.append(album)

                return artist_albums

            except Exception as e:
                print(f"Error fetching albums for artist {artist_name}: {e}")
                return []

    async def get_album_tracks(self, album_key: str) -> List[Dict]:
        """
        Get all tracks for a specific album in Plex.

        Args:
            album_key: Plex album rating key

        Returns:
            List of track data
        """
        if not self.base_url or not self.token:
            return []

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}{album_key}",
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()

                tracks = data.get("MediaContainer", {}).get("Metadata", [])
                return tracks

            except Exception as e:
                print(f"Error fetching tracks for album {album_key}: {e}")
                return []

    async def check_album_in_library(
        self,
        album_name: str,
        artist_name: str,
        spotify_tracks: List[Dict]
    ) -> Dict:
        """
        Check if an album exists in any Plex music library.
        Uses direct match first, then similarity matching.

        Args:
            album_name: Name of the album
            artist_name: Name of the artist
            spotify_tracks: List of track data from Spotify

        Returns:
            Dictionary with:
                - in_library: bool
                - match_type: "exact" | "similar" | "none"
                - match_confidence: float (0.0 to 1.0)
                - available_tracks: list of track names in Plex
                - missing_tracks: list of track names not in Plex
                - plex_album_id: str or None
        """
        print(f"Checking Plex for: '{album_name}' by '{artist_name}'")

        # Get all music libraries
        music_libraries = await self.get_music_libraries()

        if not music_libraries:
            print(f"No music libraries found in Plex")
            return {
                "in_library": False,
                "match_type": "none",
                "match_confidence": 0.0,
                "available_tracks": [],
                "missing_tracks": [track["name"] for track in spotify_tracks],
                "plex_album_id": None
            }

        print(f"Found {len(music_libraries)} music library(ies) in Plex")

        # Search across all music libraries
        for library in music_libraries:
            print(f"   Searching in library: {library['title']}")

            # Find artist in library
            artist = await self.search_artist_in_library(library["key"], artist_name)

            if not artist:
                print(f"   Artist not found in {library['title']}")
                continue

            print(f"   Found artist: {artist.get('title')}")

            # Get all albums for the artist from the library
            albums = await self.get_artist_albums(library["key"], artist_name)

            if not albums:
                print(f"   No albums found for artist")
                continue

            print(f"   Found {len(albums)} album(s)")
            for album in albums:
                print(f"      - {album.get('title')} (Artist: {album.get('parentTitle', 'N/A')})")

            # Find all exact matches (there might be duplicates)
            exact_matches = []
            for album in albums:
                if album.get("title", "").lower() == album_name.lower():
                    exact_matches.append(album)

            # If we have exact matches, find the best one based on actual track count
            matched_album = None
            if exact_matches:
                if len(exact_matches) == 1:
                    matched_album = exact_matches[0]
                    print(f"   EXACT match found: '{matched_album.get('title')}'")
                else:
                    # Multiple albums with same name - fetch tracks and compare
                    print(f"     Found {len(exact_matches)} albums with name '{album_name}'")
                    spotify_track_count = len(spotify_tracks)

                    best_album = None
                    best_track_diff = float('inf')

                    for album in exact_matches:
                        # Fetch actual tracks to get real count
                        album_tracks = await self.get_album_tracks(album.get("key"))
                        album_track_count = len(album_tracks)
                        track_diff = abs(album_track_count - spotify_track_count)
                        print(f"      - '{album.get('title')}' has {album_track_count} tracks (diff: {track_diff})")

                        if track_diff < best_track_diff:
                            best_track_diff = track_diff
                            best_album = album

                    matched_album = best_album
                    actual_count = len(await self.get_album_tracks(matched_album.get("key")))
                    print(f"   Selected album with {actual_count} tracks (closest to Spotify's {spotify_track_count})")

            # If no exact match, try similarity matching
            if not matched_album:
                best_match = None
                best_ratio = 0.0
                similarity_threshold = 0.80

                for album in albums:
                    ratio = self._similarity_ratio(album.get("title", ""), album_name)
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_match = album

                if best_ratio >= similarity_threshold:
                    matched_album = best_match
                    print(f"     SIMILAR match found: '{matched_album.get('title')}' (confidence: {best_ratio:.2%})")

            if not matched_album:
                print(f"   No match found")
                continue

            # Get tracks from Plex album
            plex_tracks = await self.get_album_tracks(matched_album.get("key"))
            plex_track_names = {track.get("title", "").lower() for track in plex_tracks}

            print(f"   Plex has {len(plex_tracks)} track(s):")
            for track in plex_tracks:
                print(f"      - {track.get('title', 'UNKNOWN')}")

            # Compare tracks
            available_tracks = []
            missing_tracks = []

            for spotify_track in spotify_tracks:
                track_name = spotify_track["name"]
                # Try exact match or similarity match for track names
                if track_name.lower() in plex_track_names:
                    available_tracks.append(track_name)
                else:
                    # Try similarity matching for tracks
                    found = False
                    for plex_track_name in plex_track_names:
                        if self._similarity_ratio(track_name, plex_track_name) >= 0.9:
                            available_tracks.append(track_name)
                            found = True
                            break
                    if not found:
                        missing_tracks.append(track_name)

            print(f"   Matched {len(available_tracks)}/{len(spotify_tracks)} tracks")
            if missing_tracks:
                print(f"   Missing tracks: {missing_tracks}")

            # Determine match type and confidence
            is_exact_match = len(exact_matches) > 0
            match_confidence = 1.0 if is_exact_match else best_ratio if 'best_ratio' in locals() else 1.0

            return {
                "in_library": True,
                "match_type": "exact" if is_exact_match else "similar",
                "match_confidence": match_confidence,
                "available_tracks": available_tracks,
                "missing_tracks": missing_tracks,
                "plex_album_id": matched_album.get("ratingKey"),
                "plex_album_name": matched_album.get("title")
            }

        # No match found in any library
        print(f"Album not found in any Plex library")
        return {
            "in_library": False,
            "match_type": "none",
            "match_confidence": 0.0,
            "available_tracks": [],
            "missing_tracks": [track["name"] for track in spotify_tracks],
            "plex_album_id": None
        }
