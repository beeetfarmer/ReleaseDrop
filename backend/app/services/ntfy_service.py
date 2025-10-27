"""
Ntfy notification service for sending push notifications.
"""
import requests
from typing import Optional
from ..config import get_settings

settings = get_settings()


class NtfyService:
    """Service class for ntfy.sh push notifications."""

    def __init__(self):
        """Initialize ntfy service with configuration."""
        self.base_url = settings.ntfy_url.rstrip('/')
        self.topic = settings.ntfy_topic
        self.username = settings.ntfy_username if settings.ntfy_username else None
        self.password = settings.ntfy_password if settings.ntfy_password else None

    async def send_notification(
        self,
        title: str,
        message: str,
        priority: int = 3,
        tags: Optional[list] = None,
        click_url: Optional[str] = None
    ) -> bool:
        """
        Send a push notification via ntfy.

        Args:
            title: Notification title
            message: Notification message body
            priority: Priority level (1-5, default: 3)
            tags: Optional list of tags/emojis
            click_url: Optional URL to open when notification is clicked

        Returns:
            True if notification was sent successfully, False otherwise
        """
        try:
            url = f"{self.base_url}/{self.topic}"

            headers = {
                "Title": title,
                "Priority": str(priority),
            }

            # Add tags if provided
            if tags:
                headers["Tags"] = ",".join(tags)

            # Add click URL if provided
            if click_url:
                headers["Click"] = click_url

            # Add markdown formatting
            headers["Markdown"] = "yes"

            # Add authentication if configured
            auth = None
            if self.username and self.password:
                auth = (self.username, self.password)

            response = requests.post(
                url,
                data=message.encode('utf-8'),
                headers=headers,
                auth=auth,
                timeout=10
            )
            response.raise_for_status()

            print(f"Ntfy notification sent: {title}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error sending ntfy notification: {e}")
            return False

    async def send_release_notification(
        self,
        artist_name: str,
        releases: list,
        priority: int = 4
    ) -> bool:
        """
        Send a formatted notification for new music releases with album covers and links.

        Args:
            artist_name: Name of the artist
            releases: List of release dictionaries
            priority: Priority level (default: 4 for new releases)

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
                message_lines.append(f"• **[{release_type}]** [{release_name}]({spotify_url})")
                message_lines.append(f"  *Released: {release_date}*")
            else:
                message_lines.append(f"• **[{release_type}]** {release_name}")
                message_lines.append(f"  *Released: {release_date}*")

        message = "\n".join(message_lines)

        # Add music note tag
        tags = ["musical_note"]

        # Use first release's Spotify URL as click action
        click_url = releases[0].get('spotify_url') if releases else None

        return await self.send_notification(
            title,
            message,
            priority,
            tags,
            click_url
        )

    async def test_connection(self) -> bool:
        """
        Test the ntfy connection.

        Returns:
            True if connection is successful
        """
        return await self.send_notification(
            title="ReleaseDrop",
            message="Connection test successful!",
            priority=2,
            tags=["musical_note", "white_check_mark"]
        )
