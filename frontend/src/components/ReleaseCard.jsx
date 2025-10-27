/**
 * Release card component for displaying music releases
 */
import React, { useState } from 'react';
import { releaseAPI } from '../services/api';

const ReleaseCard = ({ release, onMarkSeen, onJellyfinCheck, onPlexCheck, jellyfinAvailable = true, plexAvailable = true }) => {
  const [expanded, setExpanded] = useState(false);
  const [loadingTracks, setLoadingTracks] = useState(false);
  const [tracks, setTracks] = useState(release.tracks || null);

  const getReleaseTypeBadge = (type) => {
    const colors = {
      album: 'bg-purple-600',
      single: 'bg-blue-600',
      ep: 'bg-green-600',
    };
    return colors[type] || 'bg-gray-600';
  };

  const handleToggleExpand = async () => {
    // Fetch tracks if not already loaded
    if (!tracks && !loadingTracks) {
      setLoadingTracks(true);
      try {
        const fetchedTracks = await releaseAPI.getTracks(release.id);
        setTracks(fetchedTracks);
      } catch (err) {
        console.error('Failed to fetch tracks:', err);
      } finally {
        setLoadingTracks(false);
      }
    }
    setExpanded(!expanded);
  };

  const getJellyfinStatus = () => {
    if (release.in_jellyfin === null || release.in_jellyfin === undefined) {
      return null;
    }
    if (release.in_jellyfin) {
      const availableCount = release.available_tracks?.length || 0;
      const totalCount = tracks?.length || release.total_tracks;
      const isComplete = availableCount === totalCount;
      return {
        icon: isComplete ? '●' : '◐',
        text: isComplete ? 'In JF' : `JF Partial (${availableCount}/${totalCount})`,
        color: isComplete ? 'text-green-400' : 'text-yellow-400'
      };
    }
    return {
      icon: '●',
      text: 'Not in JF',
      color: 'text-red-400'
    };
  };

  const getPlexStatus = () => {
    if (release.in_plex === null || release.in_plex === undefined) {
      return null;
    }
    if (release.in_plex) {
      const availableCount = release.plex_available_tracks?.length || 0;
      const totalCount = tracks?.length || release.total_tracks;
      const isComplete = availableCount === totalCount;
      return {
        icon: isComplete ? '●' : '◐',
        text: isComplete ? 'In Plex' : `Plex Partial (${availableCount}/${totalCount})`,
        color: isComplete ? 'text-orange-400' : 'text-yellow-400'
      };
    }
    return {
      icon: '●',
      text: 'Not in Plex',
      color: 'text-red-400'
    };
  };

  const jellyfinStatus = jellyfinAvailable ? getJellyfinStatus() : null;
  const plexStatus = plexAvailable ? getPlexStatus() : null;

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden hover:bg-gray-700 transition-colors group">
      <div className="relative">
        {release.image_url && (
          <img
            src={release.image_url}
            alt={release.name}
            className="w-full aspect-square object-cover cursor-pointer"
            onClick={handleToggleExpand}
          />
        )}
        {release.is_new && (
          <span className="absolute top-2 right-2 px-2 py-1 bg-spotify-green text-xs font-bold rounded">
            NEW
          </span>
        )}
        <div className="absolute top-2 left-2 flex gap-1">
          {jellyfinStatus && (
            <span className="text-lg" title={jellyfinStatus.text}>
              {jellyfinStatus.icon}
            </span>
          )}
          {plexStatus && (
            <span className="text-lg" title={plexStatus.text}>
              {plexStatus.icon}
            </span>
          )}
        </div>
      </div>

      <div className="p-3">
        <h3
          className="text-sm font-semibold text-white mb-1 line-clamp-1 cursor-pointer hover:text-spotify-green transition-colors"
          title={release.name}
          onClick={handleToggleExpand}
        >
          {release.name}
        </h3>
        <p className="text-xs text-gray-400 mb-2 line-clamp-1">{release.artist_name}</p>

        <div className="flex items-center gap-1 mb-2 text-xs text-gray-400">
          <span
            className={`px-1.5 py-0.5 ${getReleaseTypeBadge(
              release.release_type
            )} text-white font-semibold rounded uppercase`}
          >
            {release.release_type}
          </span>
          <span>•</span>
          <span>{release.release_date}</span>
        </div>

        <div className="space-y-1">
          {jellyfinStatus && (
            <div className={`text-xs ${jellyfinStatus.color} flex items-center gap-1`}>
              <span>{jellyfinStatus.icon}</span>
              <span>{jellyfinStatus.text}</span>
            </div>
          )}
          {plexStatus && (
            <div className={`text-xs ${plexStatus.color} flex items-center gap-1`}>
              <span>{plexStatus.icon}</span>
              <span>{plexStatus.text}</span>
            </div>
          )}
        </div>
        {(jellyfinStatus || plexStatus) && <div className="mb-2"></div>}

        {expanded && (
          <div className="mb-2 max-h-48 overflow-y-auto bg-gray-900 rounded p-2">
            {loadingTracks ? (
              <div className="text-xs text-gray-400 text-center py-2">Loading tracks...</div>
            ) : tracks && tracks.length > 0 ? (
              <>
                <h4 className="text-xs font-semibold text-white mb-1">Tracks:</h4>
                <div className="space-y-0.5">
                  {tracks.map((track, idx) => {
                    const inJellyfin = release.available_tracks?.includes(track.name);
                    const notInJellyfin = release.missing_tracks?.includes(track.name);
                    const inPlex = release.plex_available_tracks?.includes(track.name);
                    const notInPlex = release.plex_missing_tracks?.includes(track.name);

                    // Determine text color based on availability
                    let textColor = 'text-gray-400';
                    if (inJellyfin || inPlex) {
                      textColor = 'text-green-400';
                    } else if (notInJellyfin || notInPlex) {
                      textColor = 'text-red-400';
                    }

                    return (
                      <div
                        key={track.id || idx}
                        className={`text-xs flex items-start gap-1 ${textColor}`}
                      >
                        <span className="text-gray-500 min-w-[1.5rem]">{track.track_number}.</span>
                        <span className="flex-1">{track.name}</span>
                        {inJellyfin && <span title="In Jellyfin" className="text-green-400">●</span>}
                        {notInJellyfin && !inJellyfin && <span title="Not in Jellyfin" className="text-red-400">●</span>}
                        {inPlex && <span title="In Plex" className="text-orange-400">●</span>}
                        {notInPlex && !inPlex && <span title="Not in Plex" className="text-red-400">●</span>}
                      </div>
                    );
                  })}
                </div>
              </>
            ) : (
              <div className="text-xs text-gray-400 text-center py-2">No track info available</div>
            )}
          </div>
        )}

        <div className="flex flex-col gap-1.5">
          <a
            href={release.spotify_url}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full px-2 py-1.5 bg-spotify-green hover:bg-green-600 text-center text-white text-xs font-semibold rounded transition-colors"
          >
            Listen on Spotify
          </a>

          <div className="flex gap-1.5">
            {release.is_new && (
              <button
                onClick={() => onMarkSeen(release.id)}
                className="flex-1 px-2 py-1.5 bg-gray-600 hover:bg-gray-500 text-white text-xs rounded transition-colors"
              >
                Mark Seen
              </button>
            )}
            <button
              onClick={handleToggleExpand}
              disabled={loadingTracks}
              className="px-2 py-1.5 bg-gray-600 hover:bg-gray-500 text-white text-xs rounded transition-colors disabled:opacity-50"
              title={expanded ? 'Hide tracks' : 'Show tracks'}
            >
              {loadingTracks ? '...' : expanded ? '▼' : '▶'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReleaseCard;
