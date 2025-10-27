/**
 * Artist search component for finding and following artists
 */
import React, { useState } from 'react';
import { artistAPI } from '../services/api';

const ArtistSearch = ({ onArtistAdded }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await artistAPI.search(query);
      setResults(data);
    } catch (err) {
      setError('Failed to search artists');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async (artist) => {
    try {
      await artistAPI.follow({
        spotify_id: artist.spotify_id,
        name: artist.name,
        spotify_url: artist.spotify_url,
        image_url: artist.image_url,
      });

      // Remove from results
      setResults(results.filter((a) => a.spotify_id !== artist.spotify_id));

      // Notify parent component
      if (onArtistAdded) {
        onArtistAdded();
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to follow artist');
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-2xl font-bold text-white mb-4">Search artist on Spotify</h2>

      <form onSubmit={handleSearch} className="mb-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for an artist..."
            className="flex-1 px-4 py-2 bg-gray-700 text-white rounded focus:outline-none focus:ring-2 focus:ring-spotify-green"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-spotify-green hover:bg-green-600 text-white font-semibold rounded transition-colors disabled:opacity-50"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {error && (
        <div className="mb-4 p-3 bg-red-600 text-white rounded">{error}</div>
      )}

      {results.length > 0 && (
        <div className="space-y-2">
          {results.map((artist) => (
            <div
              key={artist.spotify_id}
              className="flex items-center gap-4 p-3 bg-gray-700 rounded hover:bg-gray-600 transition-colors"
            >
              {artist.image_url && (
                <img
                  src={artist.image_url}
                  alt={artist.name}
                  className="w-12 h-12 rounded-full object-cover"
                />
              )}
              <div className="flex-1">
                <h3 className="text-white font-semibold">{artist.name}</h3>
                {artist.genres && artist.genres.length > 0 && (
                  <p className="text-sm text-gray-400">
                    {artist.genres.slice(0, 3).join(', ')}
                  </p>
                )}
              </div>
              <button
                onClick={() => handleFollow(artist)}
                className="px-4 py-2 bg-spotify-green hover:bg-green-600 text-white text-sm font-semibold rounded transition-colors"
              >
                Follow
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ArtistSearch;
