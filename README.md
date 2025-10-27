# ReleaseDrop

A full-stack web application to track your favorite artists and get notified of their latest releases. Automatically checks for new music daily and integrates with your Jellyfin and Plex media servers.


## Features

- **Track Artists** - Follow your favorite artists
- **Automatic Release Detection** - Daily checks for new music from followed artists
- **Push Notifications** - Get notified via Gotify or Ntfy when new music drops (optional)
- **Library Integration** - Check if releases are in your Jellyfin/Plex library (optional)
- **Track Details** - View all tracks and their availability
- **Smart Filters** - Filter by release type, library status, and more
- **Last.fm Import** - Automatically import your top artists (optional)

## Quick Start

```bash
# 1. Create new folder
mkdir releasedrop
cd releasedrop

#Download the docker-compose.yml and example.env
wget https://github.com/beeetfarmer/ReleaseDrop/blob/main/docker-compose.yml
wget https://github.com/beeetfarmer/ReleaseDrop/blob/main/.env.docker.example

cp .env.docker.example .env
# Edit .env with atleast your Spotify credentials

# 2. Start
docker-compose up -d

# Access: http://localhost:3000
```

## Integrations
- **Spotify API** - Music data and artist information
- **Gotify / Ntfy** - Push notifications (choose one or both)
- **Jellyfin** - Media server integration (optional)
- **Plex** - Media server integration (optional)
- **Last.fm** - Top artists import (optional)

## Documentation

### Getting Started
- [Setup Guide](docs/SETUP.md) - Detailed installation and configuration

### User Guides
- [Usage Guide](docs/USAGE.md) - How to use all features
- [Configuration](docs/CONFIGURATION.md) - Environment variables and settings
- [Integrations](docs/INTEGRATIONS.md) - Last.fm, Jellyfin, and Plex setup

### Reference
- [API Reference](docs/API.md) - API endpoints documentation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Need help?** Check the docs or [open an issue](https://github.com/beeetfarmer/releasedrop/issues).
