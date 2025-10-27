"""
Last.fm API integration service.
Fetches user's top artists for automatic following.
"""
import httpx
from typing import List, Dict
from ..config import get_settings


class LastFmService:
    """Service for interacting with Last.fm API."""

    BASE_URL = "http://ws.audioscrobbler.com/2.0/"

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.lastfm_api_key
        self.username = settings.lastfm_username

    async def get_top_artists(self, period: str = "overall", limit: int = 50) -> List[Dict]:
        """
        Fetch user's top artists from Last.fm.

        Args:
            period: Time period - "7day", "1month", "3month", "6month", "12month", or "overall"
            limit: Number of artists to return (max 1000)

        Returns:
            List of artist dictionaries with name and playcount
        """
        if not self.api_key or not self.username:
            print("Last.fm credentials missing!")
            print(f"   API Key: {'Set' if self.api_key else 'NOT SET'}")
            print(f"   Username: {'Set' if self.username else 'NOT SET'}")
            raise ValueError("Last.fm API key and username must be configured")

        print(f"Fetching Last.fm top artists for user: {self.username}")
        print(f"   Period: {period}, Limit: {limit}")

        async with httpx.AsyncClient() as client:
            params = {
                "method": "user.gettopartists",
                "user": self.username,
                "api_key": self.api_key,
                "format": "json",
                "period": period,
                "limit": limit
            }

            try:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

                print(f"Last.fm Response Status: {response.status_code}")

                if "error" in data:
                    error_msg = data.get('message', 'Unknown error')
                    error_code = data.get('error', 'Unknown code')
                    print(f"Last.fm API Error {error_code}: {error_msg}")
                    raise ValueError(f"Last.fm API error: {error_msg}")

                artists_data = data.get("topartists", {}).get("artist", [])
                print(f"Found {len(artists_data)} artists from Last.fm")

                artists = []
                for artist_data in artists_data:
                    artists.append({
                        "name": artist_data["name"],
                        "playcount": int(artist_data["playcount"]),
                        "mbid": artist_data.get("mbid", "")  # MusicBrainz ID
                    })

                return artists

            except httpx.HTTPStatusError as e:
                print(f"HTTP Error from Last.fm: {e}")
                print(f"   Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
                raise
            except Exception as e:
                print(f"Unexpected error fetching from Last.fm: {e}")
                raise
