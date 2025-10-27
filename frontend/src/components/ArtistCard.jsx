/**
 * Artist card component for displaying followed artists
 */
import React from 'react';

const ArtistCard = ({ artist, onUnfollow, onRefresh }) => {
  return (
    <div className="bg-gray-800 rounded-lg p-2 sm:p-3 hover:bg-gray-700 transition-colors">
      <div className="flex items-center gap-2 sm:gap-3">
        {artist.image_url && (
          <img
            src={artist.image_url}
            alt={artist.name}
            className="w-10 h-10 sm:w-12 sm:h-12 rounded-full object-cover flex-shrink-0"
          />
        )}
        <div className="flex-1 min-w-0">
          <h3 className="text-sm sm:text-base font-semibold text-white truncate">{artist.name}</h3>
          <a
            href={artist.spotify_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-spotify-green hover:underline hidden sm:inline"
          >
            Spotify
          </a>
        </div>
        <div className="flex gap-1.5 flex-shrink-0">
          <button
            onClick={() => onRefresh(artist.id)}
            className="px-2 py-1 sm:px-3 sm:py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors"
            title="Refresh releases"
          >
            <span className="hidden sm:inline">Refresh</span>
            <span className="sm:hidden">R</span>
          </button>
          <button
            onClick={() => onUnfollow(artist.id)}
            className="px-2 py-1 sm:px-3 sm:py-1.5 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors"
            title="Unfollow artist"
          >
            <span className="hidden sm:inline">Unfollow</span>
            <span className="sm:hidden">X</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ArtistCard;
