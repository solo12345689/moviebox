import React from 'react';

const MovieCard = ({ movie, onClick }) => {
    return (
        <div className="card animate-fade-in" onClick={() => onClick(movie)} style={{ cursor: 'pointer' }}>
            <div style={{ position: 'relative', paddingTop: '150%', backgroundColor: '#27272a' }}>
                {movie.poster_url ? (
                    <img
                        src={movie.poster_url}
                        alt={movie.title}
                        style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover'
                        }}
                    />
                ) : (
                    <div style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--text-secondary)'
                    }}>
                        No Poster
                    </div>
                )}
                <div className="card-overlay" style={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    background: 'linear-gradient(to top, rgba(0,0,0,0.9), transparent)',
                    padding: '1rem',
                    paddingTop: '2rem'
                }}>
                    <h3 style={{ fontSize: '1rem', marginBottom: '0.25rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{movie.title}</h3>
                    <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{movie.year || 'Unknown Year'}</p>
                </div>
            </div>
        </div>
    );
};

export default MovieCard;
