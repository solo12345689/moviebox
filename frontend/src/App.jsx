import React, { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import MovieCard from './components/MovieCard';
import DetailsModal from './components/DetailsModal';
import './styles/index.css';

// Auto-detect local server IP
const detectLocalServer = async (onProgress) => {
    // Try common local IP patterns
    const hostname = window.location.hostname;

    // If already on a local IP (and not localhost), use it
    if (hostname.match(/^192\.168\.|^10\.|^172\.(1[6-9]|2[0-9]|3[01])\./)) {
        return `http://${hostname}:8000`;
    }

    // Try to ping the backend on common local IPs
    const subnets = [
        '192.168.0',
        '192.168.1',
        '192.168.31',
        '192.168.100',
        '10.0.0'
    ];

    // Scan in chunks to avoid overwhelming the network but faster than sequential
    const checkIP = async (ip) => {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 300); // 300ms timeout

            const response = await fetch(`http://${ip}:8000/api/health`, {
                method: 'GET',
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            if (response.ok) {
                return `http://${ip}:8000`;
            }
        } catch (e) {
            // Ignore errors
        }
        return null;
    };

    for (const subnet of subnets) {
        if (onProgress) onProgress(`Scanning ${subnet}.x...`);

        // Scan 255 IPs in chunks of 20
        const ips = Array.from({ length: 255 }, (_, i) => `${subnet}.${i + 1}`);
        const chunkSize = 20;

        for (let i = 0; i < ips.length; i += chunkSize) {
            const chunk = ips.slice(i, i + chunkSize);
            const promises = chunk.map(ip => checkIP(ip));
            const results = await Promise.all(promises);
            const found = results.find(url => url);
            if (found) {
                console.log(`Found local server at ${found}`);
                return found;
            }
        }
    }

    // Fallback to localhost
    return 'http://localhost:8000';
};

// Define available backends
const BACKENDS = {
    local: null, // Will be set dynamically
    cloud: 'https://moviebox-3xxv.onrender.com'
};

function App() {
    // State for server selection (persist in localStorage)
    const [serverMode, setServerMode] = useState(() => {
        return localStorage.getItem('moviebox_server_mode') || 'cloud';
    });

    const [localServerURL, setLocalServerURL] = useState(() => {
        return localStorage.getItem('moviebox_local_ip') || 'http://localhost:8000';
    });

    const [scanningStatus, setScanningStatus] = useState('');
    const [showManualIP, setShowManualIP] = useState(false);
    const [manualIPInput, setManualIPInput] = useState('');

    // Auto-detect local server on mount
    useEffect(() => {
        // Only scan if we don't have a saved IP or if explicitly requested
        const savedIP = localStorage.getItem('moviebox_local_ip');
        if (!savedIP || savedIP === 'http://localhost:8000') {
            setScanningStatus('Scanning network...');
            detectLocalServer((status) => setScanningStatus(status)).then(url => {
                setLocalServerURL(url);
                BACKENDS.local = url;
                setScanningStatus('');
                if (url !== 'http://localhost:8000') {
                    localStorage.setItem('moviebox_local_ip', url);
                }
            });
        } else {
            BACKENDS.local = savedIP;
        }
    }, []);

    const API_BASE = serverMode === 'local' ? localServerURL : BACKENDS[serverMode];

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
            let url = `${API_BASE}/api/download?`;
            if (item.id) {
                url += `id=${encodeURIComponent(item.id)}&`;
            }
            url += `query=${encodeURIComponent(item.title)}`;
            if (season && episode) {
                url += `&season=${season}&episode=${episode}`;
            }

            // Start download in background
            fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            }).catch(err => console.error("Download failed", err));

            // Show brief notification
            alert('Download started');
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

            // Always stream on server (laptop MPV)
            await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            alert('Streaming started on server (MPV)');
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

                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        {scanningStatus && (
                            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', animation: 'pulse 1.5s infinite' }}>
                                {scanningStatus}
                            </span>
                        )}

                        <button
                            onClick={() => setShowManualIP(true)}
                            style={{
                                background: 'transparent',
                                border: 'none',
                                color: 'var(--text-muted)',
                                cursor: 'pointer',
                                padding: '0.5rem',
                                display: 'flex',
                                alignItems: 'center'
                            }}
                            title="Configure Server IP"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="12" cy="12" r="3"></circle>
                                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                            </svg>
                        </button>

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
                        onLanguageChange={(newLanguage) => {
                            // Extract base title and search for new language version
                            const baseTitle = selectedItem.title.replace(/\[.*?\]/g, '').trim();
                            const searchQuery = `${baseTitle} [${newLanguage}]`;
                            setSelectedItem(null); // Close modal
                            handleSearch(searchQuery, selectedItem.type); // Trigger search
                        }}
                        progress={downloadProgress}
                        serverMode={serverMode}
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

            {/* Manual IP Configuration Modal */}
            {showManualIP && (
                <div className="modal-backdrop" onClick={() => setShowManualIP(false)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '400px', padding: '2rem' }}>
                        <h3 style={{ marginTop: 0 }}>Configure Server IP</h3>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                            If auto-detection fails, enter your computer's local IP address manually.
                            (e.g., 192.168.31.232)
                        </p>

                        <div style={{ marginBottom: '1.5rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Server IP Address</label>
                            <input
                                type="text"
                                className="input-glass"
                                placeholder="192.168.x.x"
                                value={manualIPInput}
                                onChange={(e) => setManualIPInput(e.target.value)}
                                style={{ width: '100%', padding: '0.8rem' }}
                            />
                        </div>

                        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                            <button
                                className="btn"
                                onClick={() => setShowManualIP(false)}
                                style={{ background: 'transparent', border: '1px solid var(--border-glass)' }}
                            >
                                Cancel
                            </button>
                            <button
                                className="btn btn-primary"
                                onClick={() => {
                                    if (manualIPInput) {
                                        let url = manualIPInput.trim();

                                        // Add http:// if missing
                                        if (!url.startsWith('http')) {
                                            url = 'http://' + url;
                                        }

                                        // Fix common mistake: using frontend port 5173 instead of backend 8000
                                        if (url.includes(':5173')) {
                                            url = url.replace(':5173', ':8000');
                                            alert('Corrected port from 5173 to 8000 (Backend API)');
                                        }
                                        // If no port specified, add :8000
                                        else if ((url.match(/:/g) || []).length < 2) {
                                            // Check if there's a port (http: counts as one colon)
                                            url = url + ':8000';
                                        }

                                        setLocalServerURL(url);
                                        BACKENDS.local = url;
                                        localStorage.setItem('moviebox_local_ip', url);
                                        setServerMode('local');
                                        setShowManualIP(false);

                                        // Test connection immediately
                                        fetch(`${url}/api/health`)
                                            .then(res => {
                                                if (res.ok) alert(`Successfully connected to ${url}`);
                                                else throw new Error(res.statusText);
                                            })
                                            .catch(err => {
                                                alert(`Saved ${url}, but connection failed: ${err.message}. \n\nCheck Windows Firewall!`);
                                            });
                                    }
                                }}
                            >
                                Save & Connect
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;
