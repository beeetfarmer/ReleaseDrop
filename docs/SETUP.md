# Setup Guide

Complete installation and configuration guide for ReleaseDrop using Docker.

## Prerequisites

Before you begin, ensure you have the following:

**Required:**
1. **Docker** - [Install Docker](https://docs.docker.com/get-docker/)
2. **Docker Compose** - [Install Docker Compose](https://docs.docker.com/compose/install/)
3. **Spotify Developer Account** - For API access

**Optional:**
4. **Gotify or Ntfy Server** - For push notifications (app works without this)
5. **Jellyfin/Plex Server** - For library integration
6. **Last.fm API Key** - For importing top artists

## Getting API Credentials

### Spotify API

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click **Create an App**
4. Fill in the application details:
   - App Name: ReleaseDrop
   - App Description: Artist release tracker
5. Click **Create**
6. Copy your **Client ID** and **Client Secret**

### Gotify

1. Set up a Gotify server using their [installation guide](https://gotify.net/docs/install)
2. Access your Gotify web interface
3. Go to **Apps**
4. Click **Create Application**
5. Name it "ReleaseDrop"
6. Copy the generated **App Token**

### Ntfy (Alternative to Gotify)

1. Use the public server at `https://ntfy.sh` or [self-host](https://docs.ntfy.sh/install/)
2. Choose a unique topic name (e.g., `releasedrop-yourname`)
3. Subscribe to the topic in the ntfy app
4. No token needed for public server

### Jellyfin API Key (Optional)

1. Log into your Jellyfin web interface
2. Go to **Dashboard → API Keys**
3. Click **+** to create a new API key
4. Name it "ReleaseDrop"
5. Copy the generated key

### Plex Token (Optional)

1. Follow [Plex's guide](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) to find your authentication token
2. Copy the token

### Last.fm API Key (Optional)

1. Go to [Last.fm API Account Creation](https://www.last.fm/api/account/create)
2. Fill in the application form
3. Copy your **API Key**

## Installation Steps

### 1. Download required files

- Download the docker-compose.yml and .env.docker.example files from the repository

### 2. Configure Environment

```bash
# Copy the Docker environment template
cp .env.docker.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

### 3. Edit .env File

Update the following required variables:

```env
# Spotify API Credentials (REQUIRED)
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here

# Gotify Notification Service (OPTIONAL - choose one or skip both)
GOTIFY_URL=http://your-gotify-server:port
GOTIFY_TOKEN=your_gotify_app_token_here

# OR Ntfy Notification Service (OPTIONAL - choose one or skip both)
NTFY_URL=https://ntfy.sh
NTFY_TOPIC=your-unique-topic-name

# Database (PostgreSQL - handled by Docker)
POSTGRES_DB=releasedrop
POSTGRES_USER=releasedrop
POSTGRES_PASSWORD=change_this_secure_password

# Last.fm Integration (Optional)
LASTFM_API_KEY=your_lastfm_api_key_here
LASTFM_USERNAME=your_lastfm_username_here

# Jellyfin Integration (Optional)
JELLYFIN_URL=http://your-jellyfin-server:8096
JELLYFIN_API_KEY=your_jellyfin_api_key_here

# Plex Integration (Optional)
PLEX_URL=http://your-plex-server:32400
PLEX_TOKEN=your-plex-token

# Application Settings
RELEASE_CHECK_TIME=09:00
RELEASE_MONTHS_BACK=3
TIMEZONE=America/New_York
```

## Running the Application

```bash
# Start all services
docker-compose up -d
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8619

## First Time Setup

After starting the application:

1. **Open the frontend**: http://localhost:3000
2. **Follow an artist**:
   - Go to "Followed Artists" tab
   - Search for an artist (e.g., "ABC")
   - Click "Follow" and then refresh next to the artist to manually refresh latest release (or wait for the scheduler to auto-fetch the new releases at configured time)
3. **Check Latest Releases** tab to see their recent music