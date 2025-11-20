import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
    const [query, setQuery] = useState('');
    const [contentType, setContentType] = useState('all');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query, contentType);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="search-container" style={{ width: '100%', maxWidth: '600px', margin: '0 auto 2rem' }}>
            {/* Content Type Filter */}
            <div style={{
                display: 'flex',
                gap: '1rem',
                marginBottom: '1rem',
                justifyContent: 'center',
                flexWrap: 'wrap'
            }}>
                {[
                    { value: 'all', label: 'All' },
                    { value: 'movie', label: 'Movies' },
                    { value: 'series', label: 'TV Series' },
                    { value: 'anime', label: 'Anime' }
                ].map(type => (
                    <label key={type.value} style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        cursor: 'pointer',
                        padding: '0.5rem 1rem',
                        borderRadius: '8px',
                        background: contentType === type.value ? 'var(--accent-primary)' : 'rgba(255,255,255,0.05)',
                        border: `1px solid ${contentType === type.value ? 'var(--accent-primary)' : 'rgba(255,255,255,0.1)'}`,
                        transition: 'all 0.3s ease',
                        fontSize: '0.9rem'
                    }}>
                        <input
                            type="radio"
                            name="contentType"
                            value={type.value}
                            checked={contentType === type.value}
                            onChange={(e) => setContentType(e.target.value)}
                            style={{ display: 'none' }}
                        />
                        <span>{type.label}</span>
                    </label>
                ))}
            </div>

            <div style={{ position: 'relative' }}>
                <input
                    type="text"
                    className="input"
                    placeholder="Search movies, TV series, anime..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    style={{ paddingRight: '3rem', fontSize: '1.1rem', padding: '1rem 1.5rem' }}
                />
                <button
                    type="submit"
                    style={{
                        position: 'absolute',
                        right: '10px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--text-secondary)',
                        cursor: 'pointer'
                    }}
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                </button>
            </div>
        </form>
    );
};

export default SearchBar;
