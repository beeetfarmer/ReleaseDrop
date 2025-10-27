/**
 * Main App component
 */
import React, { useState, useEffect } from 'react';
import ArtistSearch from './components/ArtistSearch';
import ArtistCard from './components/ArtistCard';
import ReleaseCard from './components/ReleaseCard';
import LastFmImport from './components/LastFmImport';
import ArtistDetailView from './components/ArtistDetailView';
import { artistAPI, releaseAPI, integrationAPI } from './services/api';

function App() {
  const [activeTab, setActiveTab] = useState('releases');
  const [artists, setArtists] = useState([]);
  const [releases, setReleases] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  // Artist detail view
  const [selectedArtist, setSelectedArtist] = useState(null);
  const [artistSearchQuery, setArtistSearchQuery] = useState('');

  // Server availability
  const [jellyfinAvailable, setJellyfinAvailable] = useState(true);
  const [plexAvailable, setPlexAvailable] = useState(true);

  // Filters
  const [showOnlyNew, setShowOnlyNew] = useState(false);
  const [showOnlyNotInJellyfin, setShowOnlyNotInJellyfin] = useState(false);
  const [showOnlyNotInPlex, setShowOnlyNotInPlex] = useState(false);
  const [groupByType, setGroupByType] = useState(true);

  // Expanded groups state for Latest Releases page
  const [expandedGroups, setExpandedGroups] = useState({
    album: true,
    ep: true,
    single: true
  });

  // Load initial data and check server status
  useEffect(() => {
    checkServerStatus();
    loadArtists();
    loadReleases();
    loadStats();
  }, []);

  const checkServerStatus = async () => {
    try {
      const status = await integrationAPI.checkStatus();
      setJellyfinAvailable(status.jellyfin_available);
      setPlexAvailable(status.plex_available);

      if (!status.jellyfin_available && !status.plex_available) {
        console.warn('Neither Jellyfin nor Plex is available');
      } else if (!status.jellyfin_available) {
        console.warn('Jellyfin is not available');
      } else if (!status.plex_available) {
        console.warn('Plex is not available');
      }
    } catch (err) {
      console.error('Failed to check server status:', err);
      // Assume both available if check fails to not block functionality
      setJellyfinAvailable(true);
      setPlexAvailable(true);
    }
  };

  const loadArtists = async () => {
    try {
      const data = await artistAPI.getFollowed();
      setArtists(data);
    } catch (err) {
      console.error('Failed to load artists:', err);
      alert('Failed to load artists. Please check your connection and try again.');
    }
  };

  const loadReleases = async () => {
    setLoading(true);
    try {
      // Fetch ALL releases within RELEASE_MONTHS_BACK period (no limit)
      const data = await releaseAPI.getLatest();
      setReleases(data);
    } catch (err) {
      console.error('Failed to load releases:', err);
      if (err.response?.status === 500) {
        alert('Failed to load releases from Spotify. The Spotify API may be down or your credentials may be invalid.');
      } else {
        alert('Failed to load releases. Please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await releaseAPI.getStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
      // Don't show alert for stats - it's not critical
    }
  };

  const handleUnfollow = async (artistId) => {
    if (!confirm('Are you sure you want to unfollow this artist?')) return;

    try {
      await artistAPI.unfollow(artistId);
      loadArtists();
      loadReleases();
      loadStats();
    } catch (err) {
      alert('Failed to unfollow artist');
    }
  };

  const handleUnfollowAll = async () => {
    if (!confirm(`Are you sure you want to unfollow ALL ${artists.length} artists? This will delete all artist data and releases from your database.`)) return;

    try {
      // Unfollow each artist
      for (const artist of artists) {
        await artistAPI.unfollow(artist.id);
      }
      loadArtists();
      loadReleases();
      loadStats();
      alert('All artists unfollowed successfully');
    } catch (err) {
      alert('Failed to unfollow all artists');
    }
  };

  const handleRefresh = async (artistId) => {
    try {
      const result = await artistAPI.refresh(artistId);
      alert(
        `Found ${result.new_releases} new release(s) for ${result.artist}`
      );
      loadReleases();
      loadStats();
    } catch (err) {
      alert('Failed to refresh artist');
    }
  };

  const handleMarkSeen = async (releaseId) => {
    try {
      await releaseAPI.markSeen(releaseId);

      // Update the release in state without reloading (preserves scroll position)
      setReleases(prevReleases =>
        prevReleases.map(r =>
          r.id === releaseId ? { ...r, is_new: false } : r
        )
      );

      // Update stats
      loadStats();
    } catch (err) {
      console.error('Failed to mark release as seen:', err);
    }
  };

  const handleMarkAllSeen = async () => {
    if (!confirm('Mark all releases as seen?')) return;

    try {
      await releaseAPI.markAllSeen();
      loadReleases();
      loadStats();
    } catch (err) {
      alert('Failed to mark all as seen');
    }
  };

  const handleMarkVisibleSeen = async () => {
    const filteredReleases = getFilteredReleases();
    const newReleases = filteredReleases.filter(r => r.is_new);

    if (newReleases.length === 0) {
      alert('No new releases to mark as seen');
      return;
    }

    if (!confirm(`Mark ${newReleases.length} visible new release(s) as seen?`)) return;

    try {
      // Mark each visible new release as seen
      for (const release of newReleases) {
        await releaseAPI.markSeen(release.id);
      }
      loadReleases();
      loadStats();
      alert(`Marked ${newReleases.length} release(s) as seen`);
    } catch (err) {
      alert('Failed to mark releases as seen');
    }
  };

  const handleJellyfinCheck = (releaseId, result) => {
    // Update the release in state with Jellyfin info
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

  const handlePlexCheck = (releaseId, result) => {
    // Update the release in state with Plex info
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

  const handleCheckAllJellyfin = async () => {
    const filteredReleases = getFilteredReleases();
    if (!confirm(`Check ${filteredReleases.length} visible releases against Jellyfin library? This may take a while.`)) return;

    let checkedCount = 0;
    let foundCount = 0;

    // Don't use setLoading - it hides the releases
    try {
      // Check only the visible/filtered releases
      for (const release of filteredReleases) {
        try {
          const result = await integrationAPI.checkJellyfin(release.id);
          handleJellyfinCheck(release.id, result);
          checkedCount++;
          if (result.in_library) foundCount++;
        } catch (err) {
          console.error(`Failed to check release ${release.id}:`, err);
        }
      }
      alert(`Jellyfin check complete!\nChecked: ${checkedCount}\nFound in library: ${foundCount}`);
    } catch (err) {
      alert('Failed to check Jellyfin library');
    }
  };

  const handleCheckAllPlex = async () => {
    const filteredReleases = getFilteredReleases();
    if (!confirm(`Check ${filteredReleases.length} visible releases against Plex library? This may take a while.`)) return;

    let checkedCount = 0;
    let foundCount = 0;

    // Don't use setLoading - it hides the releases
    try {
      // Check only the visible/filtered releases
      for (const release of filteredReleases) {
        try {
          const result = await integrationAPI.checkPlex(release.id);
          handlePlexCheck(release.id, result);
          checkedCount++;
          if (result.in_library) foundCount++;
        } catch (err) {
          console.error(`Failed to check release ${release.id}:`, err);
        }
      }
      alert(`Plex check complete!\nChecked: ${checkedCount}\nFound in library: ${foundCount}`);
    } catch (err) {
      alert('Failed to check Plex library');
    }
  };

  // Filter and group releases
  const getFilteredReleases = () => {
    let filtered = [...releases];

    if (showOnlyNew) {
      filtered = filtered.filter(r => r.is_new);
    }

    // Handle library filters with smart logic
    // If both filters are active: show releases not in EITHER library
    // If only one filter is active: show releases not in THAT library (but may be in the other)
    if (showOnlyNotInJellyfin && showOnlyNotInPlex) {
      // Not in either library
      filtered = filtered.filter(r => r.in_jellyfin === false && r.in_plex === false);
    } else if (showOnlyNotInJellyfin) {
      // Not in Jellyfin (but may or may not be in Plex)
      filtered = filtered.filter(r => r.in_jellyfin === false);
    } else if (showOnlyNotInPlex) {
      // Not in Plex (but may or may not be in Jellyfin)
      filtered = filtered.filter(r => r.in_plex === false);
    }

    return filtered;
  };

  const getGroupedReleases = () => {
    const filtered = getFilteredReleases();

    if (!groupByType) {
      return { all: filtered };
    }

    return filtered.reduce((groups, release) => {
      const type = release.release_type || 'unknown';
      if (!groups[type]) {
        groups[type] = [];
      }
      groups[type].push(release);
      return groups;
    }, {});
  };

  const releaseGroups = getGroupedReleases();
  const releaseTypeOrder = ['album', 'ep', 'single'];
  const sortedGroupKeys = Object.keys(releaseGroups).sort((a, b) => {
    const indexA = releaseTypeOrder.indexOf(a);
    const indexB = releaseTypeOrder.indexOf(b);
    if (indexA === -1) return 1;
    if (indexB === -1) return -1;
    return indexA - indexB;
  });

  const toggleGroup = (type) => {
    setExpandedGroups(prev => ({ ...prev, [type]: !prev[type] }));
  };

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                ReleaseDrop
              </h1>
              <p className="text-gray-400">
                Track your favorite artists and never miss a release
              </p>
            </div>
            {/* Artist Search Bar - Top Right */}
            {activeTab === 'releases' && (
              <div className="relative w-64 hidden md:block">
                <input
                  type="text"
                  placeholder="Search an artist you follow.."
                  value={artistSearchQuery}
                  onChange={(e) => setArtistSearchQuery(e.target.value)}
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-spotify-green focus:outline-none text-sm"
                />
                {artistSearchQuery && (
                  <div className="absolute z-10 w-full mt-2 bg-gray-800 border border-gray-700 rounded-lg max-h-60 overflow-y-auto">
                    {artists
                      .filter(artist =>
                        artist.name.toLowerCase().includes(artistSearchQuery.toLowerCase())
                      )
                      .slice(0, 10)
                      .map(artist => (
                        <button
                          key={artist.id}
                          onClick={() => {
                            setSelectedArtist(artist);
                            setArtistSearchQuery('');
                          }}
                          className="w-full px-4 py-3 text-left hover:bg-gray-700 transition-colors flex items-center gap-3"
                        >
                          {artist.image_url && (
                            <img
                              src={artist.image_url}
                              alt={artist.name}
                              className="w-10 h-10 rounded-full object-cover"
                            />
                          )}
                          <span className="text-white">{artist.name}</span>
                        </button>
                      ))}
                    {artists.filter(artist =>
                      artist.name.toLowerCase().includes(artistSearchQuery.toLowerCase())
                    ).length === 0 && (
                      <div className="px-4 py-3 text-gray-400">No artists found</div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Stats Bar */}
      {stats && (
        <div className="bg-gray-800 border-b border-gray-700">
          <div className="container mx-auto px-4 py-4">
            <div className="flex gap-6 text-sm">
              <div>
                <span className="text-gray-400">Total Releases:</span>{' '}
                <span className="text-white font-semibold">
                  {stats.total_releases}
                </span>
              </div>
              <div>
                <span className="text-gray-400">New Releases:</span>{' '}
                <span className="text-spotify-green font-semibold">
                  {stats.new_releases}
                </span>
              </div>
              <div>
                <span className="text-gray-400">Followed Artists:</span>{' '}
                <span className="text-white font-semibold">
                  {stats.total_artists}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="container mx-auto px-4">
          <div className="flex gap-4">
            <button
              onClick={() => setActiveTab('releases')}
              className={`px-4 py-3 font-semibold transition-colors border-b-2 ${
                activeTab === 'releases'
                  ? 'text-spotify-green border-spotify-green'
                  : 'text-gray-400 border-transparent hover:text-white'
              }`}
            >
              Latest Releases
            </button>
            <button
              onClick={() => setActiveTab('artists')}
              className={`px-4 py-3 font-semibold transition-colors border-b-2 ${
                activeTab === 'artists'
                  ? 'text-spotify-green border-spotify-green'
                  : 'text-gray-400 border-transparent hover:text-white'
              }`}
            >
              Followed Artists
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {activeTab === 'releases' && (
          <div>
            {!selectedArtist && (
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-white">
                  Latest Releases
                </h2>
                <div className="flex gap-2">
                  <button
                    onClick={handleMarkVisibleSeen}
                    className="px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded transition-colors disabled:opacity-50"
                    disabled={loading}
                  >
                    Mark All Seen
                  </button>
                  {jellyfinAvailable && (
                    <button
                      onClick={handleCheckAllJellyfin}
                      className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded transition-colors disabled:opacity-50"
                      disabled={loading}
                    >
                      Check All JF
                    </button>
                  )}
                  {plexAvailable && (
                    <button
                      onClick={handleCheckAllPlex}
                      className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded transition-colors disabled:opacity-50"
                      disabled={loading}
                    >
                      Check All Plex
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Show artist detail view or all releases */}
            {selectedArtist ? (
              <ArtistDetailView
                artist={selectedArtist}
                onBack={() => setSelectedArtist(null)}
                onJellyfinCheck={handleJellyfinCheck}
                onPlexCheck={handlePlexCheck}
                jellyfinAvailable={jellyfinAvailable}
                plexAvailable={plexAvailable}
              />
            ) : (
              <>
                {/* Filters */}
                <div className="flex flex-wrap gap-3 mb-6">
                  <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showOnlyNew}
                      onChange={(e) => setShowOnlyNew(e.target.checked)}
                      className="w-4 h-4 accent-spotify-green"
                    />
                    Only New Releases
                  </label>
                  {jellyfinAvailable && (
                    <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={showOnlyNotInJellyfin}
                        onChange={(e) => setShowOnlyNotInJellyfin(e.target.checked)}
                        className="w-4 h-4 accent-spotify-green"
                      />
                      Not in Jellyfin
                    </label>
                  )}
                  {plexAvailable && (
                    <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={showOnlyNotInPlex}
                        onChange={(e) => setShowOnlyNotInPlex(e.target.checked)}
                        className="w-4 h-4 accent-spotify-green"
                      />
                      Not in Plex
                    </label>
                  )}
                  <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={groupByType}
                      onChange={(e) => setGroupByType(e.target.checked)}
                      className="w-4 h-4 accent-spotify-green"
                    />
                    Group by Type
                  </label>
                </div>

                {loading ? (
                  <div className="text-center text-gray-400 py-12">
                    Loading releases...
                  </div>
                ) : releases.length === 0 ? (
                  <div className="text-center text-gray-400 py-12">
                    No Latest Release found! Follow some artists and click refresh next to them!
                  </div>
                ) : getFilteredReleases().length === 0 ? (
                  <div className="text-center text-gray-400 py-12">
                    No releases match your filters.
                  </div>
                ) : (
                  <div className="space-y-8">
                    {sortedGroupKeys.map((groupKey) => (
                      <div key={groupKey}>
                        {groupByType && groupKey !== 'all' && (
                          <button
                            onClick={() => toggleGroup(groupKey)}
                            className="flex items-center gap-2 mb-4 hover:opacity-80 transition-opacity"
                          >
                            <span className="text-lg text-gray-400">
                              {expandedGroups[groupKey] ? '▼' : '▶'}
                            </span>
                            <h3 className="text-xl font-bold text-white capitalize flex items-center gap-2">
                              <span className={`px-2 py-1 text-sm rounded ${
                                groupKey === 'album' ? 'bg-purple-600' :
                                groupKey === 'single' ? 'bg-blue-600' :
                                groupKey === 'ep' ? 'bg-green-600' : 'bg-gray-600'
                              }`}>
                                {groupKey}s
                              </span>
                              <span className="text-gray-400 text-sm">({releaseGroups[groupKey].length})</span>
                            </h3>
                          </button>
                        )}
                        {(groupKey === 'all' || !groupByType || expandedGroups[groupKey]) && (
                          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 gap-4">
                            {releaseGroups[groupKey].map((release) => (
                              <ReleaseCard
                                key={release.id}
                                release={release}
                                onMarkSeen={handleMarkSeen}
                                onJellyfinCheck={handleJellyfinCheck}
                                onPlexCheck={handlePlexCheck}
                                jellyfinAvailable={jellyfinAvailable}
                                plexAvailable={plexAvailable}
                              />
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {activeTab === 'artists' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ArtistSearch
                onArtistAdded={() => {
                  loadArtists();
                  loadStats();
                }}
              />
              <LastFmImport
                onImportComplete={() => {
                  loadArtists();
                  loadStats();
                }}
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold text-white">
                  Followed Artists ({artists.length})
                </h2>
                {artists.length > 0 && (
                  <button
                    onClick={handleUnfollowAll}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
                  >
                    Unfollow All
                  </button>
                )}
              </div>

              {artists.length === 0 ? (
                <div className="text-center text-gray-400 py-12 bg-gray-800 rounded-lg">
                  No artists followed yet. Search for artists above or import from Last.fm to get
                  started!
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                  {[...artists].sort((a, b) => a.name.localeCompare(b.name)).map((artist) => (
                    <ArtistCard
                      key={artist.id}
                      artist={artist}
                      onUnfollow={handleUnfollow}
                      onRefresh={handleRefresh}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
