/**
 * Artist detail view showing all releases from an artist
 * Split into two expandable sections: latest releases and all releases
 * Both sections are grouped by release type
 */
import React, { useState, useEffect } from 'react';
import ReleaseCard from './ReleaseCard';
import { artistAPI, integrationAPI } from '../services/api';

const ArtistDetailView = ({ artist, onBack, onJellyfinCheck, onPlexCheck, jellyfinAvailable = true, plexAvailable = true }) => {
  const [releases, setReleases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [releaseMonthsBack, setReleaseMonthsBack] = useState(3);
  const [checkingJellyfin, setCheckingJellyfin] = useState(false);
  const [checkingPlex, setCheckingPlex] = useState(false);

  // Expandable section states
  const [latestSectionExpanded, setLatestSectionExpanded] = useState(true);
  const [allReleasesSectionExpanded, setAllReleasesSectionExpanded] = useState(true);

  // Expanded groups state for latest section
  const [latestExpandedGroups, setLatestExpandedGroups] = useState({
    album: true,
    ep: true,
    single: true
  });

  // Expanded groups state for all releases section
  const [allExpandedGroups, setAllExpandedGroups] = useState({
    album: true,
    ep: true,
    single: true
  });

  useEffect(() => {
    loadArtistReleases();
  }, [artist]);

  const loadArtistReleases = async () => {
    setLoading(true);
    try {
      const data = await artistAPI.getReleases(artist.id);
      setReleases(data.releases);
      setReleaseMonthsBack(data.release_months_back);
    } catch (err) {
      console.error('Failed to load artist releases:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await artistAPI.refresh(artist.id);
      await loadArtistReleases();
      alert('Releases refreshed successfully!');
    } catch (err) {
      alert('Failed to refresh releases');
    } finally {
      setRefreshing(false);
    }
  };

  const handleCheckAllJellyfin = async () => {
    if (!confirm(`Check all ${releases.length} releases by ${artist.name} against Jellyfin library? This may take a while.`)) return;

    setCheckingJellyfin(true);
    let checkedCount = 0;
    let foundCount = 0;

    try {
      // Check each release individually
      for (const release of releases) {
        try {
          const result = await integrationAPI.checkJellyfin(release.id);
          // Update the release in state
          setReleases(prevReleases =>
            prevReleases.map(r =>
              r.id === release.id
                ? {
                    ...r,
                    in_jellyfin: result.in_library,
                    jellyfin_match_type: result.match_type,
                    jellyfin_match_confidence: result.match_confidence,
                    available_tracks: result.available_tracks,
                    missing_tracks: result.missing_tracks
                  }
                : r
            )
          );
          checkedCount++;
          if (result.in_library) foundCount++;
        } catch (err) {
          console.error(`Failed to check release ${release.id}:`, err);
        }
      }
      alert(`Jellyfin check complete!\nChecked: ${checkedCount}\nFound in library: ${foundCount}`);
    } catch (err) {
      alert('Failed to check Jellyfin library');
    } finally {
      setCheckingJellyfin(false);
    }
  };

  const handleCheckAllPlex = async () => {
    if (!confirm(`Check all ${releases.length} releases by ${artist.name} against Plex library? This may take a while.`)) return;

    setCheckingPlex(true);
    let checkedCount = 0;
    let foundCount = 0;

    try {
      // Check each release individually
      for (const release of releases) {
        try {
          const result = await integrationAPI.checkPlex(release.id);
          // Update the release in state
          setReleases(prevReleases =>
            prevReleases.map(r =>
              r.id === release.id
                ? {
                    ...r,
                    in_plex: result.in_library,
                    plex_match_type: result.match_type,
                    plex_match_confidence: result.match_confidence,
                    plex_available_tracks: result.available_tracks,
                    plex_missing_tracks: result.missing_tracks
                  }
                : r
            )
          );
          checkedCount++;
          if (result.in_library) foundCount++;
        } catch (err) {
          console.error(`Failed to check release ${release.id}:`, err);
        }
      }
      alert(`Plex check complete!\nChecked: ${checkedCount}\nFound in library: ${foundCount}`);
    } catch (err) {
      alert('Failed to check Plex library');
    } finally {
      setCheckingPlex(false);
    }
  };

  const handleJellyfinCheckSingle = (releaseId, result) => {
    setReleases(prevReleases =>
      prevReleases.map(r =>
        r.id === releaseId
          ? {
              ...r,
              in_jellyfin: result.in_library,
              jellyfin_match_type: result.match_type,
              jellyfin_match_confidence: result.match_confidence,
              available_tracks: result.available_tracks,
              missing_tracks: result.missing_tracks
            }
          : r
      )
    );
  };

  const handlePlexCheckSingle = (releaseId, result) => {
    setReleases(prevReleases =>
      prevReleases.map(r =>
        r.id === releaseId
          ? {
              ...r,
              in_plex: result.in_library,
              plex_match_type: result.match_type,
              plex_match_confidence: result.match_confidence,
              plex_available_tracks: result.available_tracks,
              plex_missing_tracks: result.missing_tracks
            }
          : r
      )
    );
  };

  // Calculate cutoff date for "latest" releases
  const cutoffDate = new Date();
  cutoffDate.setMonth(cutoffDate.getMonth() - releaseMonthsBack);

  // Split releases into latest and all
  const latestReleases = releases.filter(r => new Date(r.release_date) >= cutoffDate);
  const allReleases = releases;

  // Group latest releases by type
  const groupedLatestReleases = latestReleases.reduce((groups, release) => {
    const type = release.release_type || 'unknown';
    if (!groups[type]) {
      groups[type] = [];
    }
    groups[type].push(release);
    return groups;
  }, {});

  // Group all releases by type
  const groupedAllReleases = allReleases.reduce((groups, release) => {
    const type = release.release_type || 'unknown';
    if (!groups[type]) {
      groups[type] = [];
    }
    groups[type].push(release);
    return groups;
  }, {});

  const releaseTypeOrder = ['album', 'ep', 'single'];

  const sortedLatestGroupKeys = Object.keys(groupedLatestReleases).sort((a, b) => {
    const indexA = releaseTypeOrder.indexOf(a);
    const indexB = releaseTypeOrder.indexOf(b);
    if (indexA === -1) return 1;
    if (indexB === -1) return -1;
    return indexA - indexB;
  });

  const sortedAllGroupKeys = Object.keys(groupedAllReleases).sort((a, b) => {
    const indexA = releaseTypeOrder.indexOf(a);
    const indexB = releaseTypeOrder.indexOf(b);
    if (indexA === -1) return 1;
    if (indexB === -1) return -1;
    return indexA - indexB;
  });

  const toggleLatestGroup = (type) => {
    setLatestExpandedGroups(prev => ({ ...prev, [type]: !prev[type] }));
  };

  const toggleAllGroup = (type) => {
    setAllExpandedGroups(prev => ({ ...prev, [type]: !prev[type] }));
  };

  if (loading) {
    return (
      <div className="text-center text-gray-400 py-12">
        Loading releases...
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {artist.image_url && (
            <img
              src={artist.image_url}
              alt={artist.name}
              className="w-20 h-20 rounded-full object-cover"
            />
          )}
          <div>
            <h2 className="text-3xl font-bold text-white">{artist.name}</h2>
            <p className="text-gray-400">{releases.length} release(s)</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <button
            onClick={onBack}
            className="px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded transition-colors"
          >
            Back to All
          </button>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors disabled:opacity-50"
          >
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
          {jellyfinAvailable && (
            <button
              onClick={handleCheckAllJellyfin}
              disabled={checkingJellyfin}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded transition-colors disabled:opacity-50"
            >
              {checkingJellyfin ? 'Checking...' : 'Check All JF'}
            </button>
          )}
          {plexAvailable && (
            <button
              onClick={handleCheckAllPlex}
              disabled={checkingPlex}
              className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded transition-colors disabled:opacity-50"
            >
              {checkingPlex ? 'Checking...' : 'Check All Plex'}
            </button>
          )}
        </div>
      </div>

      {/* Latest Releases Section (Last N Months) */}
      <div className="border border-gray-700 rounded-lg bg-gray-800">
        <button
          onClick={() => setLatestSectionExpanded(!latestSectionExpanded)}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-750 transition-colors"
        >
          <h3 className="text-2xl font-bold text-white">
            Latest Releases (Last {releaseMonthsBack} Months)
            <span className="text-gray-400 text-lg ml-2">({latestReleases.length})</span>
          </h3>
          <span className="text-2xl text-gray-400">
            {latestSectionExpanded ? '▼' : '▶'}
          </span>
        </button>

        {latestSectionExpanded && (
          <div className="px-6 pb-6 space-y-6">
            {sortedLatestGroupKeys.length === 0 ? (
              <p className="text-gray-400 text-center py-8">No releases in this period</p>
            ) : (
              sortedLatestGroupKeys.map((groupKey) => (
                <div key={groupKey}>
                  <button
                    onClick={() => toggleLatestGroup(groupKey)}
                    className="flex items-center gap-2 mb-4 hover:opacity-80 transition-opacity"
                  >
                    <span className="text-lg text-gray-400">
                      {latestExpandedGroups[groupKey] ? '▼' : '▶'}
                    </span>
                    <h4 className="text-xl font-bold text-white capitalize flex items-center gap-2">
                      <span className={`px-2 py-1 text-sm rounded ${
                        groupKey === 'album' ? 'bg-purple-600' :
                        groupKey === 'single' ? 'bg-blue-600' :
                        groupKey === 'ep' ? 'bg-green-600' : 'bg-gray-600'
                      }`}>
                        {groupKey}s
                      </span>
                      <span className="text-gray-400 text-sm">
                        ({groupedLatestReleases[groupKey].length})
                      </span>
                    </h4>
                  </button>

                  {latestExpandedGroups[groupKey] && (
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 gap-4">
                      {groupedLatestReleases[groupKey].map((release) => (
                        <ReleaseCard
                          key={release.id}
                          release={release}
                          onMarkSeen={() => {}}
                          onJellyfinCheck={handleJellyfinCheckSingle}
                          onPlexCheck={handlePlexCheckSingle}
                          jellyfinAvailable={jellyfinAvailable}
                          plexAvailable={plexAvailable}
                        />
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* All Releases Section (Ever) */}
      <div className="border border-gray-700 rounded-lg bg-gray-800">
        <button
          onClick={() => setAllReleasesSectionExpanded(!allReleasesSectionExpanded)}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-750 transition-colors"
        >
          <h3 className="text-2xl font-bold text-white">
            All Releases
            <span className="text-gray-400 text-lg ml-2">({allReleases.length})</span>
          </h3>
          <span className="text-2xl text-gray-400">
            {allReleasesSectionExpanded ? '▼' : '▶'}
          </span>
        </button>

        {allReleasesSectionExpanded && (
          <div className="px-6 pb-6 space-y-6">
            {sortedAllGroupKeys.length === 0 ? (
              <p className="text-gray-400 text-center py-8">No releases found</p>
            ) : (
              sortedAllGroupKeys.map((groupKey) => (
                <div key={groupKey}>
                  <button
                    onClick={() => toggleAllGroup(groupKey)}
                    className="flex items-center gap-2 mb-4 hover:opacity-80 transition-opacity"
                  >
                    <span className="text-lg text-gray-400">
                      {allExpandedGroups[groupKey] ? '▼' : '▶'}
                    </span>
                    <h4 className="text-xl font-bold text-white capitalize flex items-center gap-2">
                      <span className={`px-2 py-1 text-sm rounded ${
                        groupKey === 'album' ? 'bg-purple-600' :
                        groupKey === 'single' ? 'bg-blue-600' :
                        groupKey === 'ep' ? 'bg-green-600' : 'bg-gray-600'
                      }`}>
                        {groupKey}s
                      </span>
                      <span className="text-gray-400 text-sm">
                        ({groupedAllReleases[groupKey].length})
                      </span>
                    </h4>
                  </button>

                  {allExpandedGroups[groupKey] && (
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 gap-4">
                      {groupedAllReleases[groupKey].map((release) => (
                        <ReleaseCard
                          key={release.id}
                          release={release}
                          onMarkSeen={() => {}}
                          onJellyfinCheck={handleJellyfinCheckSingle}
                          onPlexCheck={handlePlexCheckSingle}
                          jellyfinAvailable={jellyfinAvailable}
                          plexAvailable={plexAvailable}
                        />
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {releases.length === 0 && (
        <div className="text-center text-gray-400 py-12">
          No releases found for this artist.
        </div>
      )}
    </div>
  );
};

export default ArtistDetailView;
