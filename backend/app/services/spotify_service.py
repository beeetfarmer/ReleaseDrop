"""
Spotify API service for artist search and release fetching.
Uses Spotipy library for Spotify Web API integration.
"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from ..config import get_settings
from ..schemas.artist import ArtistSearch

settings = get_settings()


class SpotifyService:
    """Service class for Spotify API operations."""

    def __init__(self):
        """Initialize Spotify client with credentials."""
        auth_manager = SpotifyClientCredentials(
            client_id=settings.spotify_client_id,
            client_secret=settings.spotify_client_secret
        )
        self.client = spotipy.Spotify(auth_manager=auth_manager)

    async def search_artists(self, query: str, limit: int = 10) -> List[ArtistSearch]:
        """
        Search for artists on Spotify.

        Args:
            query: Search query string
            limit: Maximum number of results (default: 10)

        Returns:
            List of ArtistSearch objects
        """
        try:
            results = self.client.search(q=query, type='artist', limit=limit)
            artists = []

            for item in results['artists']['items']:
                artist = ArtistSearch(
                    spotify_id=item['id'],
                    name=item['name'],
                    spotify_url=item['external_urls']['spotify'],
                    image_url=item['images'][0]['url'] if item.get('images') else None,
                    followers=item.get('followers', {}).get('total', 0),
                    genres=item.get('genres', [])
                )
                artists.append(artist)

            return artists

        except Exception as e:
            print(f"Error searching artists: {e}")
            return []

    async def get_artist_releases(
        self,
        artist_id: str,
        months_back: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent releases for an artist from the last N months.

        Args:
            artist_id: Spotify artist ID
            months_back: Number of months to look back (default: 3)

        Returns:
            List of release dictionaries sorted by release date (descending)
        """
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=months_back * 30)

            # Fetch all albums for the artist (exclude compilations)
            all_releases = []
            results = self.client.artist_albums(
                artist_id,
                album_type='album,single',
                limit=50
            )

            # Process all pages of results
            while results:
                for album in results['items']:
                    # Skip compilations and albums where artist appears but isn't primary
                    album_group = album.get('album_group', '')
                    if album_group == 'compilation' or album_group == 'appears_on':
                        continue

                    release_date_str = album['release_date']

                    # Parse release date (can be YYYY, YYYY-MM, or YYYY-MM-DD)
                    try:
                        if len(release_date_str) == 4:  # Year only
                            release_date = datetime.strptime(release_date_str, '%Y')
                        elif len(release_date_str) == 7:  # Year-Month
                            release_date = datetime.strptime(release_date_str, '%Y-%m')
                        else:  # Full date
                            release_date = datetime.strptime(release_date_str, '%Y-%m-%d')
                    except ValueError:
                        continue

                    # Filter by date
                    if release_date >= cutoff_date:
                        release_data = {
                            'spotify_id': album['id'],
                            'name': album['name'],
                            'release_type': album['album_type'],
                            'release_date': album['release_date'],
                            'spotify_url': album['external_urls']['spotify'],
                            'image_url': album['images'][0]['url'] if album.get('images') else None,
                            'total_tracks': album.get('total_tracks', 0)
                        }
                        all_releases.append(release_data)

                # Check if there are more results
                if results['next']:
                    results = self.client.next(results)
                else:
                    break

            # Sort by release date (descending - newest first)
            all_releases.sort(key=lambda x: x['release_date'], reverse=True)

            return all_releases

        except Exception as e:
            print(f"Error fetching artist releases: {e}")
            return []

    async def get_artist_info(self, artist_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about an artist.

        Args:
            artist_id: Spotify artist ID

        Returns:
            Dictionary with artist information or None
        """
        try:
            artist = self.client.artist(artist_id)
            return {
                'spotify_id': artist['id'],
                'name': artist['name'],
                'spotify_url': artist['external_urls']['spotify'],
                'image_url': artist['images'][0]['url'] if artist.get('images') else None,
                'followers': artist.get('followers', {}).get('total', 0),
                'genres': artist.get('genres', [])
            }
        except Exception as e:
            print(f"Error fetching artist info: {e}")
            return None

    async def get_album_tracks(self, album_id: str) -> List[Dict[str, Any]]:
        """
        Get all tracks for a specific album.

        Args:
            album_id: Spotify album ID

        Returns:
            List of track dictionaries
        """
        try:
            results = self.client.album_tracks(album_id, limit=50)
            tracks = []

            while results:
                for track in results['items']:
                    tracks.append({
                        'id': track['id'],
                        'name': track['name'],
                        'track_number': track['track_number'],
                        'duration_ms': track['duration_ms'],
                        'spotify_url': track['external_urls']['spotify']
                    })

                # Check for more tracks
                if results['next']:
                    results = self.client.next(results)
                else:
                    break

            return tracks

        except Exception as e:
            print(f"Error fetching album tracks: {e}")
            return []
