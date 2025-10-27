# Integrations Guide

Complete guide for setting up and using ReleaseDrop integrations.

## Overview

ReleaseDrop integrates with:
- **Gotify / Ntfy** - Push notifications for new releases
- **Last.fm** - Import your top artists automatically
- **Jellyfin** - Check which albums are in your media server
- **Plex** - Check which albums are in your media server

All integrations are optional. The core artist tracking functionality works without them.

## Notification Services

### Gotify Integration

**Setup:**

1. **Install Gotify:**
   - Follow [Gotify installation guide](https://gotify.net/docs/install)
   - Or use Docker: `docker run -p 8080:80 gotify/server`

2. **Create Application:**
   - Login to Gotify web UI
   - Apps → Create Application
   - Copy the application token

3. **Configure `.env`:**
   ```env
   GOTIFY_URL=http://your-gotify-server:8080
   GOTIFY_TOKEN=your_app_token_here
   ```

4. **Test Connection:**
   - Use the API endpoint: `POST /api/integrations/gotify/test`
   - Or check in the web UI after following an artist

### Ntfy Integration

**Setup:**

1. **Choose Server:**
   - Use public server: `https://ntfy.sh` (free)
   - Or self-host: Follow [ntfy installation guide](https://docs.ntfy.sh/install/)

2. **Choose Topic:**
   - Pick a unique topic name (e.g., `releasedrop-yourname`)
   - Subscribe in ntfy mobile app or web UI

3. **Configure `.env`:**
   ```env
   NTFY_URL=https://ntfy.sh
   NTFY_TOPIC=your_unique_topic_name
   # Optional - for private/protected topics:
   NTFY_USERNAME=your_username
   NTFY_PASSWORD=your_password
   ```

4. **Subscribe to Topic:**
   - Mobile: Install ntfy app → Subscribe to your topic
   - Web: Visit `https://ntfy.sh/your_topic_name`
   - Desktop: Use ntfy desktop app

5. **Test Connection:**
   - Use the API endpoint: `POST /api/integrations/ntfy/test`
   - You should receive a test notification


## Last.fm Integration

### Setup

1. **Get API Key:**
   - Go to https://www.last.fm/api/account/create
   - Fill in the application form
   - Copy your API key

2. **Configure `.env`:**
   ```env
   LASTFM_API_KEY=your_api_key_here
   LASTFM_USERNAME=your_lastfm_username
   ```

3. **Restart backend**

### Usage

1. Go to **Followed Artists** tab
2. Find the **Import from Last.fm** panel
3. Select time period (7 days to all time)
4. Choose number of artists (1-200)
5. Click **Import Top Artists**

## Jellyfin Integration

### Setup

1. **Get API Key:**
   - Jellyfin Dashboard → API Keys → Create new
   - Name it "ReleaseDrop"

2. **Configure `.env`:**
   ```env
   JELLYFIN_URL=http://your-jellyfin-server:8096
   JELLYFIN_API_KEY=your_api_key_here
   ```

3. **Restart backend**

### Usage

- **Check JF** - Check single album
- **Check All JF** - Check all visible albums
- **▶** - View track availability

### Matching Logic

- Direct match (100% confidence)
- Similarity match (85%+ confidence)
- Track-level matching (90% threshold)

## Plex Integration

### Setup

1. **Get Plex Token:**
   - Follow [Plex's authentication guide](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)

2. **Configure `.env`:**
   ```env
   PLEX_URL=http://your-plex-server:32400
   PLEX_TOKEN=your_plex_token
   ```

3. **Restart backend**

### Usage

Same as Jellyfin, but using **Check Plex** buttons.

## Combined Usage

Use filters to find albums:
- **Not in Jellyfin** - Missing from Jellyfin
- **Not in Plex** - Missing from Plex
- **Both** - Missing from both libraries
