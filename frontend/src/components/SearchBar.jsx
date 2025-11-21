import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
    const [query, setQuery] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query, 'all');
        }
    };

    return (
        <form onSubmit={handleSubmit} className="search-container">
            <div style={{ position: 'relative' }}>
                <input
                    type="text"
                    className="input-glass"
                    placeholder="Search movies, TV series, anime..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    style={{ paddingRight: '3rem' }}
                />
                <button
                    type="submit"
                    style={{
                        position: 'absolute',
                        right: '15px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        padding: '5px'
                    }}
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                </button>
            </div>
        </form>
    );
};

export default SearchBar;
