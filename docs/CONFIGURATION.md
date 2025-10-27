# Configuration Guide

Detailed configuration options for ReleaseDrop.

## Environment Variables

All configuration is done through the `.env` file in the project root.

### Required Settings

#### Spotify API
```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```
Get these from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).

#### Database (Docker)
```env
POSTGRES_DB=releasedrop
POSTGRES_USER=releasedrop
POSTGRES_PASSWORD=change_this_secure_password
```
PostgreSQL database credentials. Used by Docker Compose.

### Optional Settings

#### Notifications

**Note:** Notifications are completely optional. Without them, the app works fine but you won't receive push alerts when new releases are found.

Choose **Gotify** or **Ntfy** (or both, or neither) for notifications:

**Option 1: Gotify**
```env
GOTIFY_URL=http://your-gotify-server:port
GOTIFY_TOKEN=your_app_token
```
Your Gotify server URL and application token.

**Option 2: Ntfy** (Simpler alternative)
```env
NTFY_URL=https://ntfy.sh
NTFY_TOPIC=your_unique_topic_name
NTFY_USERNAME=  # Optional, for private topics
NTFY_PASSWORD=  # Optional, for private topics
```
Ntfy notifications using the public ntfy.sh server or your own instance.

---

## Complete Environment Variables Reference

### Core Application

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SPOTIFY_CLIENT_ID` | Yes | - | Spotify API Client ID from developer dashboard |
| `SPOTIFY_CLIENT_SECRET` | Yes | - | Spotify API Client Secret from developer dashboard |
| `POSTGRES_DB` | Yes (Docker) | `releasedrop` | PostgreSQL database name |
| `POSTGRES_USER` | Yes (Docker) | `releasedrop` | PostgreSQL username |
| `POSTGRES_PASSWORD` | Yes (Docker) | - | PostgreSQL password (use a strong password!) |
| `RELEASE_CHECK_TIME` | No | `09:00` | Daily check time in 24-hour format (HH:MM) |
| `RELEASE_MONTHS_BACK` | No | `3` | How many months back to fetch releases (1-12 recommended) |
| `TIMEZONE` | No | `UTC` | Timezone for scheduling (e.g., `America/New_York`, `Europe/London`) |

### Notification Services

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOTIFY_URL` | No | Empty | Gotify server URL (e.g., `http://gotify.example.com:8080`) |
| `GOTIFY_TOKEN` | No | Empty | Gotify application token for sending notifications |
| `NTFY_URL` | No | Empty | Ntfy server URL (e.g., `https://ntfy.sh` or self-hosted) |
| `NTFY_TOPIC` | No | Empty | Ntfy topic name (must be unique if using public server) |
| `NTFY_USERNAME` | No | Empty | Ntfy username for authenticated topics (optional) |
| `NTFY_PASSWORD` | No | Empty | Ntfy password for authenticated topics (optional) |

**Note:** You can configure both Gotify and Ntfy, or just one, or neither. If neither is configured, the app still works but won't send push notifications.

### Integration Services

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JELLYFIN_URL` | No | Empty | Jellyfin server URL (e.g., `http://jellyfin.local:8096`) |
| `JELLYFIN_API_KEY` | No | Empty | Jellyfin API key from Dashboard → API Keys |
| `PLEX_URL` | No | Empty | Plex server URL (e.g., `http://plex.local:32400`) |
| `PLEX_TOKEN` | No | Empty | Plex authentication token (X-Plex-Token) |
| `LASTFM_API_KEY` | No | Empty | Last.fm API key for importing top artists |
| `LASTFM_USERNAME` | No | Empty | Your Last.fm username |

---

## Configuration Examples

### Minimal Configuration (Required Only)

```env
# Database
POSTGRES_DB=releasedrop
POSTGRES_USER=releasedrop
POSTGRES_PASSWORD=my_secure_password_123

# Spotify
SPOTIFY_CLIENT_ID=abc123xyz789
SPOTIFY_CLIENT_SECRET=def456uvw012
```

This minimal setup allows:
- Following artists
- Viewing releases
- All filtering features
- No push notifications
- No library checking
- No Last.fm import

### Basic Setup with Notifications

```env
# Database
POSTGRES_DB=releasedrop
POSTGRES_USER=releasedrop
POSTGRES_PASSWORD=my_secure_password_123

# Spotify
SPOTIFY_CLIENT_ID=abc123xyz789
SPOTIFY_CLIENT_SECRET=def456uvw012

# Ntfy Notifications
NTFY_URL=https://ntfy.sh
NTFY_TOPIC=myapp-releases-xyz
```

### Full-Featured Setup

```env
# Database
POSTGRES_DB=releasedrop
POSTGRES_USER=releasedrop
POSTGRES_PASSWORD=my_secure_password_123

# Spotify
SPOTIFY_CLIENT_ID=abc123xyz789
SPOTIFY_CLIENT_SECRET=def456uvw012

# Gotify Notifications
GOTIFY_URL=http://gotify.example.com:8080
GOTIFY_TOKEN=AbCdEfGhIjK

# Jellyfin Integration
JELLYFIN_URL=http://jellyfin.local:8096
JELLYFIN_API_KEY=1234567890abcdef

# Plex Integration
PLEX_URL=http://plex.local:32400
PLEX_TOKEN=xyz789abc123

# Last.fm Integration
LASTFM_API_KEY=lastfm_key_here
LASTFM_USERNAME=my_lastfm_user

# Settings
RELEASE_CHECK_TIME=07:00
RELEASE_MONTHS_BACK=6
TIMEZONE=America/New_York
```

---

## Getting API Keys

### Spotify
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app
3. Copy Client ID and Client Secret

### Gotify
1. Install Gotify server: [Installation Guide](https://gotify.net/docs/install)
2. Create an application in Gotify web UI
3. Copy the app token

### Ntfy
1. Use public server `https://ntfy.sh` or [self-host](https://docs.ntfy.sh/install/)
2. Choose a unique topic name
3. Subscribe in ntfy app

### Jellyfin
1. Go to Jellyfin Dashboard → API Keys
2. Create new key named "ReleaseDrop"
3. Copy the generated key

### Plex
1. Follow [Plex's X-Plex-Token guide](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)
2. Copy your token

### Last.fm
1. Go to [Last.fm API Account](https://www.last.fm/api/account/create)
2. Fill in application details
3. Copy the API key

---

## Timezone Reference

Use standard timezone names from the [tz database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

**Common Examples:**
- `UTC` - Coordinated Universal Time
- `America/New_York` - Eastern Time (US)
- `America/Los_Angeles` - Pacific Time (US)
- `America/Chicago` - Central Time (US)
- `Europe/London` - UK
- `Europe/Paris` - Central European Time
- `Asia/Tokyo` - Japan
- `Australia/Sydney` - Australian Eastern Time
