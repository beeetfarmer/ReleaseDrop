# Usage Guide

How to use all features of ReleaseDrop.

## Following Artists

### Search and Follow

1. Go to the **Followed Artists** tab
2. Type an artist name in the search box
3. Click **Search**
4. Browse the search results
5. Click **Follow** on any artist you want to track

The app will immediately fetch their latest releases when you click "refresh" next to the artist(from the last 3 months by default) or you can wait for the scheduler to automatically fetch the latest releases for all the artists awt the configured time in the env.

### Quick Artist Search (Latest Releases Page)

On the **Latest Releases** tab, there's a search box in the top-right corner:

1. Start typing an artist name
2. A dropdown will appear with matching followed artists
3. Click an artist to view all their releases

This is useful for quickly jumping to a specific artist's releases.

## Viewing Releases

### Latest Releases Tab

Shows all recent releases from your followed artists, organized by type.

#### Release Information

Each release card shows:
- Album artwork
- Release name
- Artist name
- Release date
- Release type (Album/EP/Single)
- "NEW" badge for unseen releases

#### Release Actions

Each release has these buttons:

- **Listen on Spotify** - Opens the release in Spotify
- **Mark Seen** - Removes the "NEW" badge
- **▶** - View track list
- **Check JF** - Check if it's in your Jellyfin library
- **Check Plex** - Check if it's in your Plex library

### Artist Detail View

Click any artist (from the search dropdown) to see:

1. **Latest Releases Section** - Releases from the last N months
2. **All Releases Section** - Complete discography

Both sections are grouped by release type and can be collapsed/expanded.

**Available Actions:**
- **Back to All** - Return to main releases view
- **Refresh** - Manually fetch new releases for this artist
- **Check All JF** - Check all releases against Jellyfin
- **Check All Plex** - Check all releases against Plex

## Filtering Releases

Use the checkboxes above the releases to filter:

### Only New Releases
Shows only releases you haven't marked as seen yet.

### Not in Jellyfin
Shows only releases that are NOT in your Jellyfin library (perfect for finding music to download).

### Not in Plex
Shows only releases that are NOT in your Plex library.

### Combining Filters

- **Not in Jellyfin + Not in Plex**: Shows releases in neither library
- **Not in Jellyfin only**: Shows releases not in Jellyfin (may or may not be in Plex)
- **Not in Plex only**: Shows releases not in Plex (may or may not be in Jellyfin)

### Group by Type
Organizes releases into collapsible sections (Albums, EPs, Singles).

## Library Integration

### Checking Jellyfin/Plex

#### Single Release
1. Find a release card
2. Click **Check JF** or **Check Plex**
3. Wait for the check to complete
4. The button will update with the status:
   - **In JF/Plex** - Complete album found
   - **Partial (X/Y)** - Some tracks found
   - **Not in JF/Plex** - Album not found

#### All Releases
1. Click **Check All JF** or **Check All Plex** at the top
2. Confirm the action
3. Wait for all releases to be checked (this may take a few minutes)
4. An alert will show the summary

### Track-Level Details

After checking a release against Jellyfin/Plex:

1. Click the **▶** button on the release card
2. The track list will expand
3. Tracks are color-coded

## Managing Followed Artists

### Refreshing an Artist

To manually check for new releases from a specific artist:

1. Go to **Followed Artists** tab
2. Find the artist card
3. Click **Refresh**
4. A popup will show how many new releases were found

### Unfollowing an Artist

To stop tracking an artist:

1. Go to **Followed Artists** tab
2. Find the artist card
3. Click **Unfollow**
4. Confirm the action

**Note:** This will also delete all their releases from your database.

### Unfollow All Artists

To remove all followed artists at once:

1. Go to **Followed Artists** tab
2. Click **Unfollow All** at the top
3. Confirm the action (this cannot be undone!)

## Last.fm Integration

### Importing Top Artists

Automatically follow your most-played artists from Last.fm:

1. Go to **Followed Artists** tab
2. Find the **Import from Last.fm** panel
3. Select a time period:
   - Last 7 Days
   - Last Month
   - Last 3 Months
   - Last 6 Months
   - Last Year
   - All Time
4. Choose how many artists to import (1-200)
5. Click **Import Top Artists**
6. Wait for the import to complete
7. A summary will show how many artists were added

**Note:** Artists you're already following will be skipped.

## Marking Releases as Seen

### Single Release
Click the **Mark Seen** button on any release card.

### All Visible Releases
Click **Mark All Seen** at the top to mark all currently visible releases (respects your active filters).

## Notifications

### Gotify Push Notifications

ReleaseDrop automatically sends notifications when:
- New releases are found during the daily check
- The notification includes:
  - Artist name
  - Release type
  - Release name (clickable link to Spotify)
  - Release date

### Daily Automated Checks

The app automatically checks for new releases daily at the configured time (default: 09:00).

To change this time, edit `RELEASE_CHECK_TIME` in your `.env` file.

## Statistics

The stats bar at the top shows:
- **Total Releases** - All releases in your database
- **New Releases** - Releases you haven't marked as seen
- **Followed Artists** - Number of artists you're tracking

## Tips & Best Practices

### For Best Performance

1. **Don't follow too many artists at once** - Start with your favorites
2. **Use the Last.fm import** - Quick way to bulk-add artists
3. **Check libraries in batches** - Use filters to check specific groups
4. **Mark releases as seen regularly** - Keeps the interface clean

### Managing Large Collections

1. **Use filters effectively** - Narrow down what you're looking for
2. **Focus on new releases** - Enable "Only New Releases" filter

### Finding Music to Download

1. Enable **"Not in Jellyfin"** or **"Not in Plex"** filter
2. Optionally enable **"Only New Releases"**
3. Click **Check All JF/Plex** to scan your library
4. Browse the filtered results
5. Click **Listen on Spotify** to preview before downloading

### Discovering New Music

1. Import your Last.fm top artists
2. Let the app run for a week
3. Check the **Latest Releases** tab regularly
4. Explore new releases from artists you already like

## Keyboard Shortcuts

Currently, the app uses mouse/touch interactions only. Keyboard shortcuts may be added in future updates.

## Mobile Usage

The app is fully responsive and works on mobile devices:
- Tap to expand/collapse sections
- Swipe to scroll through releases
- All features work on touch screens