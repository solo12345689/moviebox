import React, { useState } from 'react';
import SearchBar from './components/SearchBar';
import MovieCard from './components/MovieCard';
import DetailsModal from './components/DetailsModal';
import './styles/index.css';

const API_BASE = '/api';

function App() {
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedItem, setSelectedItem] = useState(null);
    const [detailsLoading, setDetailsLoading] = useState(false);

    const [downloadProgress, setDownloadProgress] = useState(null);

    React.useEffect(() => {
        const ws = new WebSocket('ws://localhost:8000/api/ws');

        ws.onopen = () => {
            console.log('Connected to WebSocket');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('WS Message:', data);
                if (data.status === 'downloading') {
                    setDownloadProgress(data.progress);
                } else if (data.status === 'completed') {
                    setDownloadProgress(null);
                    alert('Download Complete!');
                } else if (data.status === 'error') {
                    setDownloadProgress(null);
                    alert(`Error: ${data.message}`);
                }
            } catch (e) {
                console.error('WS Error:', e);
            }
        };

        return () => {
            ws.close();
        };
    }, []);

    const handleSearch = async (query, type = 'all') => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/search?query=${encodeURIComponent(query)}&content_type=${type}`);
            const data = await res.json();
            setResults(data.results || []);
        } catch (err) {
            console.error("Search failed", err);
        } finally {
            setLoading(false);
        }
    };

    const handleItemClick = async (item) => {
        setDetailsLoading(true);
        try {
            const res = await fetch(`${API_BASE}/details/${item.id}`);
            const details = await res.json();
            setSelectedItem({ ...item, ...details });
        } catch (err) {
            console.error("Failed to get details", err);
        } finally {
            setDetailsLoading(false);
        }
    };

    const handleDownload = async (item, season = null, episode = null) => {
        try {
            let url = `${API_BASE}/download?query=${encodeURIComponent(item.title)}`;
            if (season && episode) {
                url += `&season=${season}&episode=${episode}`;
            }
            await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            // Alert removed, progress handled by WS
        } catch (err) {
            console.error("Download failed", err);
            alert("Failed to start download");
        }
    };

    const handleStream = async (item, season = null, episode = null) => {
        try {
            let url = `${API_BASE}/stream?query=${encodeURIComponent(item.title)}`;
            if (item.id) {
                url += `&id=${encodeURIComponent(item.id)}`;
            }
            if (item.type) {
                url += `&content_type=${encodeURIComponent(item.type)}`;
            } else if (season) {
                url += `&content_type=series`;
            }

            if (season && episode) {
                url += `&season=${season}&episode=${episode}`;
            }

            await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            alert(`Stream launching for ${item.title}`);
        } catch (err) {
            console.error("Stream failed", err);
            alert("Failed to start stream");
        }
    };

    return (
        <div className="app">
            <header className="glass-panel" style={{ position: 'sticky', top: 0, zIndex: 50, padding: '1.5rem 0', marginBottom: '2rem', borderBottom: '1px solid var(--border-glass)', borderTop: 'none', borderLeft: 'none', borderRight: 'none' }}>
                <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                        <h1 style={{ fontSize: '2rem', margin: 0 }}>MovieBox</h1>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Cinematic Discovery</p>
                    </div>
                    {/* Placeholder for future user menu or settings */}
                </div>
            </header>

            <main className="container">
                <SearchBar onSearch={handleSearch} />

                {loading && (
                    <div style={{ textAlign: 'center', padding: '4rem' }}>
                        <div className="spinner" style={{
                            width: '50px', height: '50px',
                            border: '3px solid rgba(255,255,255,0.1)',
                            borderTopColor: 'var(--primary)',
                            borderRadius: '50%',
                            animation: 'spin 1s linear infinite',
                            margin: '0 auto'
                        }}></div>
                        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
                    </div>
                )}

                <div className="movie-card-grid" style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
                    gap: '2rem',
                    paddingBottom: '4rem'
                }}>
                    {results.map((item) => (
                        <MovieCard key={item.id} movie={item} onClick={handleItemClick} />
                    ))}
                </div>

                {results.length === 0 && !loading && (
                    <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '4rem', padding: '2rem', border: '1px dashed var(--border-glass)', borderRadius: 'var(--radius-md)' }}>
                        <p style={{ fontSize: '1.2rem' }}>Start by searching for a movie or TV show.</p>
                    </div>
                )}
            </main>

            {
                selectedItem && (
                    <DetailsModal
                        item={selectedItem}
                        onClose={() => setSelectedItem(null)}
                        onDownload={handleDownload}
                        onStream={handleStream}
                        progress={downloadProgress}
                    />
                )
            }

            {
                detailsLoading && (
                    <div className="modal-backdrop">
                        <div className="spinner" style={{
                            width: '50px', height: '50px',
                            border: '3px solid rgba(255,255,255,0.1)',
                            borderTopColor: 'var(--primary)',
                            borderRadius: '50%',
                            animation: 'spin 1s linear infinite'
                        }}></div>
                    </div>
                )
            }
        </div >
    );
}

export default App;
