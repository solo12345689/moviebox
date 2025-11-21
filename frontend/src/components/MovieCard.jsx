import React from 'react';

const MovieCard = ({ movie, onClick }) => {
    return (
        <div className="movie-card animate-fade-in" onClick={() => onClick(movie)}>
            {movie.poster_url ? (
                <img
                    src={movie.poster_url}
                    alt={movie.title}
                    loading="lazy"
                />
            ) : (
                <div style={{
                    width: '100%',
                    height: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--text-muted)',
                    background: '#1a1a20'
                }}>
                    No Poster
                </div>
            )}
            <div className="movie-card-overlay">
                <h3 style={{ fontSize: '1.1rem', marginBottom: '0.25rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: 'white' }}>{movie.title}</h3>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>{movie.year || 'Unknown Year'}</p>
            </div>
        </div>
    );
};

export default MovieCard;
