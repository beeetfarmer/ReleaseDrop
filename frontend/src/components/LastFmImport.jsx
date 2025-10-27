/**
 * Last.fm import component for automatically importing top artists
 */
import React, { useState } from 'react';
import { integrationAPI } from '../services/api';

const LastFmImport = ({ onImportComplete }) => {
  const [period, setPeriod] = useState('overall');
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const periods = [
    { value: '7day', label: 'Last 7 Days' },
    { value: '1month', label: 'Last Month' },
    { value: '3month', label: 'Last 3 Months' },
    { value: '6month', label: 'Last 6 Months' },
    { value: '12month', label: 'Last Year' },
    { value: 'overall', label: 'All Time' },
  ];

  const handleImport = async () => {
    setLoading(true);
    setResult(null);

    try {
      const data = await integrationAPI.importLastFm(period, limit);
      setResult(data);
      if (onImportComplete) {
        onImportComplete(data);
      }
    } catch (err) {
      console.error('Failed to import Last.fm artists:', err);
      alert('Failed to import artists from Last.fm. Check your API key and username in settings.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-red-600 rounded-full flex items-center justify-center">
          <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M10.584 17.21l-3.597-3.44L8.38 12.24l2.204 2.107 4.155-4.156 1.392 1.528z"/>
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">Import from Last.fm</h3>
          <p className="text-sm text-gray-400">Automatically add your top artists</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Time Period
          </label>
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="w-full bg-gray-700 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-spotify-green"
            disabled={loading}
          >
            {periods.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Number of Artists
          </label>
          <input
            type="number"
            min="1"
            max="200"
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value))}
            className="w-full bg-gray-700 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-spotify-green"
            disabled={loading}
          />
        </div>
      </div>

      <button
        onClick={handleImport}
        disabled={loading}
        className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Importing...' : 'Import Top Artists'}
      </button>

      {result && (
        <div className="mt-4 p-4 bg-gray-700 rounded">
          <h4 className="text-white font-semibold mb-2">Import Complete!</h4>
          <div className="text-sm text-gray-300 space-y-1">
            <p>Total artists from Last.fm: {result.total_artists}</p>
            <p className="text-spotify-green">New artists added: {result.new_artists}</p>
            <p className="text-gray-400">Already following: {result.existing_artists}</p>
          </div>
          {result.artists_added.length > 0 && (
            <div className="mt-3">
              <p className="text-xs text-gray-400 mb-1">Artists added:</p>
              <div className="text-xs text-gray-300 max-h-32 overflow-y-auto">
                {result.artists_added.join(', ')}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LastFmImport;
