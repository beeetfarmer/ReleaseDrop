"""
Jellyfin API integration service.
Checks if albums exist in Jellyfin library and tracks availability.
"""
import httpx
from typing import Dict, List, Optional
from difflib import SequenceMatcher
from ..config import get_settings


class JellyfinService:
    """Service for interacting with Jellyfin API."""

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.jellyfin_url.rstrip('/')
        self.api_key = settings.jellyfin_api_key
        self.headers = {
            "X-Emby-Token": self.api_key
        }

    def _similarity_ratio(self, str1: str, str2: str) -> float:
        """Calculate similarity ratio between two strings (0.0 to 1.0)."""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    async def get_artist_items(self, artist_name: str) -> List[Dict]:
        """
        Get all items (albums) for a specific artist in Jellyfin.

        Args:
            artist_name: Name of the artist

        Returns:
            List of album items from Jellyfin
        """
        if not self.base_url or not self.api_key:
            return []

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # First, get the user ID (required for most Jellyfin API calls)
                users_response = await client.get(
                    f"{self.base_url}/Users",
                    headers=self.headers
                )
                users_response.raise_for_status()
                users = users_response.json()

                if not users:
                    print(f"No users found in Jellyfin")
                    return []

                user_id = users[0]["Id"]  # Use first user

                # Search for artist using proper endpoint
                search_params = {
                    "searchTerm": artist_name,
                    "IncludeItemTypes": "MusicArtist",
                    "Recursive": "true",
                    "Limit": 50
                }

                response = await client.get(
                    f"{self.base_url}/Users/{user_id}/Items",
                    headers=self.headers,
                    params=search_params
                )
                response.raise_for_status()
                data = response.json()

                artists = data.get("Items", [])
                if not artists:
                    return []

                # Get the first matching artist's ID
                artist_id = artists[0]["Id"]

                # Get all albums for this artist
                album_params = {
                    "ArtistIds": artist_id,
                    "IncludeItemTypes": "MusicAlbum",
                    "Recursive": "true",
                    "Fields": "Path,MediaStreams",
                    "Limit": 500
                }

                album_response = await client.get(
                    f"{self.base_url}/Users/{user_id}/Items",
                    headers=self.headers,
                    params=album_params
                )
                album_response.raise_for_status()
                album_data = album_response.json()

                return album_data.get("Items", [])

            except Exception as e:
                print(f"Error fetching Jellyfin data for {artist_name}: {e}")
                return []

    async def get_album_tracks(self, album_id: str) -> List[Dict]:
        """
        Get all tracks for a specific album in Jellyfin.

        Args:
            album_id: Jellyfin album ID

        Returns:
            List of track items
        """
        if not self.base_url or not self.api_key:
            return []

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Get user ID
                users_response = await client.get(
                    f"{self.base_url}/Users",
                    headers=self.headers
                )
                users_response.raise_for_status()
                users = users_response.json()

                if not users:
                    return []

                user_id = users[0]["Id"]

                params = {
                    "ParentId": album_id,
                    "SortBy": "SortName"
                }

                response = await client.get(
                    f"{self.base_url}/Users/{user_id}/Items",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                return data.get("Items", [])

            except Exception as e:
                print(f"Error fetching tracks for album {album_id}: {e}")
                return []

    async def check_album_in_library(
        self,
        album_name: str,
        artist_name: str,
        spotify_tracks: List[Dict]
    ) -> Dict:
        """
        Check if an album exists in Jellyfin library.
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
                - available_tracks: list of track names in Jellyfin
                - missing_tracks: list of track names not in Jellyfin
                - jellyfin_album_id: str or None
        """
        print(f"Checking Jellyfin for: '{album_name}' by '{artist_name}'")
        jellyfin_albums = await self.get_artist_items(artist_name)

        if not jellyfin_albums:
            print(f"No albums found for artist: '{artist_name}'")
            return {
                "in_library": False,
                "match_type": "none",
                "match_confidence": 0.0,
                "available_tracks": [],
                "missing_tracks": [track["name"] for track in spotify_tracks],
                "jellyfin_album_id": None
            }

        print(f"Found {len(jellyfin_albums)} albums in Jellyfin for '{artist_name}':")
        for jf_album in jellyfin_albums:
            print(f"   - {jf_album['Name']}")

        # Try direct match first
        exact_match = None
        for jf_album in jellyfin_albums:
            if jf_album["Name"].lower() == album_name.lower():
                exact_match = jf_album
                break

        # If no exact match, try similarity matching
        best_match = None
        best_ratio = 0.0
        similarity_threshold = 0.85

        if not exact_match:
            for jf_album in jellyfin_albums:
                ratio = self._similarity_ratio(jf_album["Name"], album_name)
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = jf_album

        # Determine which match to use
        matched_album = exact_match or (best_match if best_ratio >= similarity_threshold else None)

        if not matched_album:
            print(f"No match found. Best similarity: {best_ratio:.2%}")
            return {
                "in_library": False,
                "match_type": "none",
                "match_confidence": best_ratio,
                "available_tracks": [],
                "missing_tracks": [track["name"] for track in spotify_tracks],
                "jellyfin_album_id": None
            }

        if exact_match:
            print(f"EXACT match found: '{matched_album['Name']}'")
        else:
            print(f"  SIMILAR match found: '{matched_album['Name']}' (confidence: {best_ratio:.2%})")

        # Get tracks from Jellyfin album
        jf_tracks = await self.get_album_tracks(matched_album["Id"])
        jf_track_names = {track["Name"].lower() for track in jf_tracks}

        # Compare tracks
        available_tracks = []
        missing_tracks = []

        for spotify_track in spotify_tracks:
            track_name = spotify_track["name"]
            # Try exact match or similarity match for track names
            if track_name.lower() in jf_track_names:
                available_tracks.append(track_name)
            else:
                # Try similarity matching for tracks
                found = False
                for jf_track_name in jf_track_names:
                    if self._similarity_ratio(track_name, jf_track_name) >= 0.9:
                        available_tracks.append(track_name)
                        found = True
                        break
                if not found:
                    missing_tracks.append(track_name)

        return {
            "in_library": True,
            "match_type": "exact" if exact_match else "similar",
            "match_confidence": 1.0 if exact_match else best_ratio,
            "available_tracks": available_tracks,
            "missing_tracks": missing_tracks,
            "jellyfin_album_id": matched_album["Id"],
            "jellyfin_album_name": matched_album["Name"]
        }
