"""
Gotify notification service for sending push notifications.
"""
import requests
from typing import Optional
from ..config import get_settings

settings = get_settings()


class GotifyService:
    """Service class for Gotify push notifications."""

    def __init__(self):
        """Initialize Gotify service with configuration."""
        self.base_url = settings.gotify_url.rstrip('/')
        self.app_token = settings.gotify_token

    async def send_notification(
        self,
        title: str,
        message: str,
        priority: int = 5,
        extras: Optional[dict] = None
    ) -> bool:
        """
        Send a push notification via Gotify.

        Args:
            title: Notification title
            message: Notification message body
            priority: Priority level (0-10, default: 5)
            extras: Optional extras dict for images, markdown, etc.

        Returns:
            True if notification was sent successfully, False otherwise
        """
        try:
            url = f"{self.base_url}/message"
            params = {"token": self.app_token}
            data = {
                "title": title,
                "message": message,
                "priority": priority
            }

            # Add extras for images and markdown support
            if extras:
                data["extras"] = extras

            response = requests.post(url, params=params, json=data, timeout=10)
            response.raise_for_status()

            print(f"Gotify notification sent: {title}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error sending Gotify notification: {e}")
            return False

    async def send_release_notification(
        self,
        artist_name: str,
        releases: list,
        priority: int = 7
    ) -> bool:
        """
        Send a formatted notification for new music releases with album covers and links.

        Args:
            artist_name: Name of the artist
            releases: List of release dictionaries
            priority: Priority level (default: 7 for new releases)

        Returns:
            True if notification was sent successfully
        """
        if not releases:
            return False

        # Build notification message with markdown links
        title = f"New Release{'s' if len(releases) > 1 else ''} from {artist_name}"

        message_lines = []
        for release in releases:
            release_type = release.get('release_type', 'release').upper()
            release_name = release.get('name', 'Unknown')
            release_date = release.get('release_date', 'Unknown date')
            spotify_url = release.get('spotify_url', '')

            # Create markdown link to Spotify
            if spotify_url:
                message_lines.append(f"• [{release_type}] [{release_name}]({spotify_url}) ({release_date})")
            else:
                message_lines.append(f"• [{release_type}] {release_name} ({release_date})")

        message = "\n".join(message_lines)

        # Add extras for markdown link support
        extras = {
            "client::display": {
                "contentType": "text/markdown"
            }
        }

        return await self.send_notification(title, message, priority, extras)

    async def test_connection(self) -> bool:
        """
        Test the Gotify connection.

        Returns:
            True if connection is successful
        """
        return await self.send_notification(
            title="ReleaseDrop",
            message="Connection test successful!",
            priority=3
        )
