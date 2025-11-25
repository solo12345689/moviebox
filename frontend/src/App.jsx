import React, { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import MovieCard from './components/MovieCard';
import DetailsModal from './components/DetailsModal';
import './styles/index.css';

// Define available backends
const BACKENDS = {
    local: 'http://localhost:8000',
    cloud: 'https://moviebox-3xxv.onrender.com'
};

function App() {
    // State for server selection (persist in localStorage)
    const [serverMode, setServerMode] = useState(() => {
        return localStorage.getItem('moviebox_server_mode') || 'cloud';
    });

    const API_BASE = BACKENDS[serverMode];

    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedItem, setSelectedItem] = useState(null);
    const [detailsLoading, setDetailsLoading] = useState(false);
    const [downloadProgress, setDownloadProgress] = useState(null);

    // Update localStorage when mode changes
    useEffect(() => {
        localStorage.setItem('moviebox_server_mode', serverMode);
    }, [serverMode]);

    const toggleServer = () => {
        setServerMode(prev => prev === 'cloud' ? 'local' : 'cloud');
    };

    React.useEffect(() => {
        // WebSocket URL needs to match the current API_BASE
        // Replace http/https with ws/wss
        const wsUrl = API_BASE.replace(/^http/, 'ws') + '/api/ws';

        let ws;
        try {
            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log('Connected to WebSocket at', wsUrl);
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
        } catch (err) {
            console.error("WebSocket connection failed", err);
        }

        return () => {
            if (ws) ws.close();
        };
    }, [API_BASE]); // Re-connect when API_BASE changes

    const handleSearch = async (query, type = 'all') => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/api/search?query=${encodeURIComponent(query)}&content_type=${type}`);
            const data = await res.json();
            setResults(data.results || []);
        } catch (err) {
            console.error("Search failed", err);
            alert(`Failed to connect to ${serverMode} server. Try switching servers.`);
        } finally {
            setLoading(false);
        }
    };

    const handleItemClick = async (item) => {
        setDetailsLoading(true);
        try {
            const res = await fetch(`${API_BASE}/api/details/${item.id}`);
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
            let url = `${API_BASE}/api/download?query=${encodeURIComponent(item.title)}`;
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
            let url = `${API_BASE}/api/stream?query=${encodeURIComponent(item.title)}`;
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

            // Check for Android/Capacitor
            const isAndroid = /Android/i.test(navigator.userAgent) && window.Capacitor;

            if (isAndroid) {
                // Request URL mode
                url += `&mode=url`;
                const res = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await res.json();

                if (data.status === 'success' && data.url) {
                    // The backend returns a relative proxy URL like "/api/proxy-stream?url=..."
                    // We need to construct the full URL using API_BASE
                    const streamUrl = data.url.startsWith('http') ? data.url : `${API_BASE}${data.url}`;
                    const intentUrl = `intent:${streamUrl}#Intent;package=is.xyz.mpv;type=video/*;scheme=http;end`;
                    window.location.href = intentUrl;
                } else if (data.status === 'error') {
                    // Show detailed error message from backend
                    alert(`Stream Error: ${data.message}\n\nPlease check if:\n1. Backend server is running\n2. Content is available\n3. Season/Episode exists`);
                    console.error("Stream error details:", data.details);
                } else {
                    alert("Failed to resolve stream URL for Android");
                }
            } else {
                // Default behavior (launch on server)
                await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                alert(`Stream launching for ${item.title}`);
            }
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

                    <button
                        onClick={toggleServer}
                        style={{
                            background: 'rgba(255, 255, 255, 0.1)',
                            border: '1px solid var(--border-glass)',
                            color: 'var(--text-primary)',
                            padding: '0.5rem 1rem',
                            borderRadius: '20px',
                            cursor: 'pointer',
                            fontSize: '0.8rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                        }}
                    >
                        <span style={{
                            width: '8px',
                            height: '8px',
                            borderRadius: '50%',
                            background: serverMode === 'cloud' ? '#10b981' : '#f59e0b',
                            display: 'inline-block'
                        }}></span>
                        {serverMode === 'cloud' ? 'Cloud Server' : 'Local Server'}
                    </button>
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
                        <p style={{ fontSize: '0.9rem', marginTop: '1rem', opacity: 0.7 }}>
                            Connected to: {API_BASE}
                        </p>
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
