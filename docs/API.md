# API Reference

Complete API documentation for ReleaseDrop backend.

## Base URL

```
http://localhost:8619
```

## Interactive Documentation

FastAPI provides automatic interactive API documentation:
- **Swagger UI**: http://localhost:8619/docs
- **ReDoc**: http://localhost:8619/redoc

## Authentication

Currently, the API does not require authentication.
---

## Artists Endpoints

### Search Artists

Search for artists on Spotify.

**Endpoint:** `GET /artists/search`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | Yes | Artist name to search for |
| limit | integer | No | Number of results (default: 10, max: 50) |

**Example Request:**
```bash
curl "http://localhost:8619/artists/search?query=ITZY&limit=5"
```

**Example Response:**
```json
[
  {
    "spotify_id": "2KC9Qb60EaY0kW4eH68vr3",
    "name": "ITZY",
    "spotify_url": "https://open.spotify.com/artist/2KC9Qb60EaY0kW4eH68vr3",
    "image_url": "https://i.scdn.co/image/...",
    "followers": 5000000,
    "genres": ["k-pop", "pop"]
  }
]
```

---

### Follow Artist

Add an artist to your follow list.

**Endpoint:** `POST /artists/follow`

**Request Body:**
```json
{
  "spotify_id": "2KC9Qb60EaY0kW4eH68vr3",
  "name": "ITZY",
  "spotify_url": "https://open.spotify.com/artist/2KC9Qb60EaY0kW4eH68vr3",
  "image_url": "https://i.scdn.co/image/..."
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8619/artists/follow" \
  -H "Content-Type: application/json" \
  -d '{
    "spotify_id": "2KC9Qb60EaY0kW4eH68vr3",
    "name": "ITZY",
    "spotify_url": "https://open.spotify.com/artist/2KC9Qb60EaY0kW4eH68vr3",
    "image_url": "https://i.scdn.co/image/..."
  }'
```

**Response:**
```json
{
  "id": 1,
  "spotify_id": "2KC9Qb60EaY0kW4eH68vr3",
  "name": "ITZY",
  "spotify_url": "https://open.spotify.com/artist/2KC9Qb60EaY0kW4eH68vr3",
  "image_url": "https://i.scdn.co/image/...",
  "added_at": "2025-10-18T12:00:00"
}
```

---

### Get Followed Artists

Get all artists you're following.

**Endpoint:** `GET /artists/followed`

**Example Request:**
```bash
curl "http://localhost:8619/artists/followed"
```

**Example Response:**
```json
[
  {
    "id": 1,
    "spotify_id": "2KC9Qb60EaY0kW4eH68vr3",
    "name": "ITZY",
    "spotify_url": "https://open.spotify.com/artist/2KC9Qb60EaY0kW4eH68vr3",
    "image_url": "https://i.scdn.co/image/...",
    "added_at": "2025-10-18T12:00:00"
  }
]
```

---

### Unfollow Artist

Remove an artist from your follow list.

**Endpoint:** `DELETE /artists/{artist_id}`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| artist_id | integer | Yes | Database ID of the artist |

**Example Request:**
```bash
curl -X DELETE "http://localhost:8619/artists/1"
```

**Response:**
```json
{
  "message": "Unfollowed ITZY"
}
```

---

### Refresh Artist Releases

Manually check for new releases from a specific artist.

**Endpoint:** `POST /artists/{artist_id}/refresh`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| artist_id | integer | Yes | Database ID of the artist |

**Example Request:**
```bash
curl -X POST "http://localhost:8619/artists/1/refresh"
```

**Response:**
```json
{
  "artist": "ITZY",
  "new_releases": 2,
  "releases": [
    {
      "name": "CHECKMATE",
      "release_type": "album",
      "release_date": "2025-10-15"
    }
  ]
}
```

---

### Get Artist Releases

Get all releases for a specific artist.

**Endpoint:** `GET /artists/{artist_id}/releases`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| artist_id | integer | Yes | Database ID of the artist |

**Example Request:**
```bash
curl "http://localhost:8619/artists/1/releases"
```

**Response:**
```json
{
  "artist_id": 1,
  "artist_name": "ITZY",
  "release_months_back": 3,
  "releases": [
    {
      "id": 1,
      "spotify_id": "abc123",
      "name": "CHECKMATE",
      "release_type": "album",
      "release_date": "2025-10-15",
      "spotify_url": "https://open.spotify.com/album/...",
      "image_url": "https://i.scdn.co/image/...",
      "total_tracks": 12,
      "is_new": true
    }
  ]
}
```

---

## Releases Endpoints

### Get All Releases

Get all releases with optional filtering.

**Endpoint:** `GET /releases/`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| only_new | boolean | No | Show only new releases (default: false) |
| artist_id | integer | No | Filter by artist ID |

**Example Request:**
```bash
curl "http://localhost:8619/releases/?only_new=true"
```

**Response:**
```json
[
  {
    "id": 1,
    "spotify_id": "abc123",
    "name": "CHECKMATE",
    "artist_name": "ITZY",
    "release_type": "album",
    "release_date": "2025-10-15",
    "spotify_url": "https://open.spotify.com/album/...",
    "image_url": "https://i.scdn.co/image/...",
    "total_tracks": 12,
    "is_new": true,
    "in_jellyfin": true,
    "in_plex": false
  }
]
```

---

### Get Latest Releases

Get the most recent releases across all followed artists.

**Endpoint:** `GET /releases/latest`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| limit | integer | No | Number of releases to return (1-100, default: 20) |

**Example Request:**
```bash
curl "http://localhost:8619/releases/latest?limit=50"
```

---

### Mark Release as Seen

Mark a release as seen (removes "NEW" badge).

**Endpoint:** `POST /releases/{release_id}/mark-seen`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| release_id | integer | Yes | Database ID of the release |

**Example Request:**
```bash
curl -X POST "http://localhost:8619/releases/1/mark-seen"
```

**Response:**
```json
{
  "message": "Release marked as seen"
}
```

---

### Mark All Releases as Seen

Mark all releases as seen.

**Endpoint:** `POST /releases/mark-all-seen`

**Example Request:**
```bash
curl -X POST "http://localhost:8619/releases/mark-all-seen"
```

**Response:**
```json
{
  "message": "Marked 15 releases as seen"
}
```

---

### Get Release Statistics

Get statistics about your releases.

**Endpoint:** `GET /releases/stats`

**Example Request:**
```bash
curl "http://localhost:8619/releases/stats"
```

**Response:**
```json
{
  "total_releases": 150,
  "new_releases": 25,
  "total_artists": 47,
  "by_type": {
    "albums": 50,
    "singles": 75,
    "eps": 25
  }
}
```

---

### Get Release Tracks

Fetch tracks for a specific release from Spotify.

**Endpoint:** `GET /releases/{release_id}/tracks`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| release_id | integer | Yes | Database ID of the release |

**Example Request:**
```bash
curl "http://localhost:8619/releases/1/tracks"
```

**Response:**
```json
[
  {
    "track_number": 1,
    "name": "SNEAKERS",
    "duration_ms": 180000,
    "preview_url": "https://p.scdn.co/mp3-preview/..."
  }
]
```

---

## Integrations Endpoints

### Check Integration Status

Check which integrations are available.

**Endpoint:** `GET /integrations/status`

**Example Request:**
```bash
curl "http://localhost:8619/integrations/status"
```

**Response:**
```json
{
  "jellyfin_available": true,
  "plex_available": true,
  "lastfm_available": true
}
```

---

### Import from Last.fm

Import top artists from Last.fm.

**Endpoint:** `POST /integrations/lastfm/import`

**Request Body:**
```json
{
  "period": "overall",
  "limit": 50
}
```

**Periods:**
- `7day` - Last 7 days
- `1month` - Last month
- `3month` - Last 3 months
- `6month` - Last 6 months
- `12month` - Last year
- `overall` - All time

**Example Request:**
```bash
curl -X POST "http://localhost:8619/integrations/lastfm/import" \
  -H "Content-Type: application/json" \
  -d '{
    "period": "overall",
    "limit": 50
  }'
```

**Response:**
```json
{
  "total_artists": 50,
  "new_artists": 23,
  "existing_artists": 27,
  "artists_added": ["ITZY", "TWICE", "Red Velvet"]
}
```

---

### Check Release in Jellyfin

Check if a release is in your Jellyfin library.

**Endpoint:** `POST /integrations/jellyfin/check/{release_id}`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| release_id | integer | Yes | Database ID of the release |

**Example Request:**
```bash
curl -X POST "http://localhost:8619/integrations/jellyfin/check/1"
```

**Response:**
```json
{
  "release_id": 1,
  "in_library": true,
  "match_type": "exact",
  "match_confidence": 1.0,
  "available_tracks": ["Track 1", "Track 2", "Track 3"],
  "missing_tracks": []
}
```

---

### Check Release in Plex

Check if a release is in your Plex library.

**Endpoint:** `POST /integrations/plex/check/{release_id}`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| release_id | integer | Yes | Database ID of the release |

**Example Request:**
```bash
curl -X POST "http://localhost:8619/integrations/plex/check/1"
```

**Response:**
```json
{
  "release_id": 1,
  "in_library": true,
  "match_type": "similar",
  "match_confidence": 0.92,
  "available_tracks": ["Track 1", "Track 2"],
  "missing_tracks": ["Track 3"]
}
```

---

## Health Endpoints

### Root

Get API information.

**Endpoint:** `GET /`

**Response:**
```json
{
  "message": "ReleaseDrop API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

### Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "releasedrop"
}
```

---

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request
```json
{
  "detail": "Artist is already being followed"
}
```

### 404 Not Found
```json
{
  "detail": "Artist not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

The API does not currently implement rate limiting, but Spotify's API has its own rate limits:
- **Too Many Requests**: Wait a few seconds and retry
- **Typical limits**: ~100 requests per minute

