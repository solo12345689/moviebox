import React, { useState } from 'react';
import SearchBar from './components/SearchBar';
import MovieCard from './components/MovieCard';
import DetailsModal from './components/DetailsModal';
import './styles/index.css';

const API_BASE = 'http://localhost:8000/api';

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

    const handleSearch = async (query) => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/search?query=${encodeURIComponent(query)}`);
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

    const handleDownload = async (item) => {
        try {
            await fetch(`${API_BASE}/download?query=${encodeURIComponent(item.title)}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            // Alert removed, progress handled by WS
        } catch (err) {
            console.error("Download failed", err);
            alert("Failed to start download");
        }
    };

    const handleStream = async (item) => {
        try {
            await fetch(`${API_BASE}/stream?query=${encodeURIComponent(item.title)}`, {
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
            <header style={{ padding: '2rem 0', textAlign: 'center' }}>
                <div className="container">
                    <h1 style={{ marginBottom: '0.5rem' }}>MovieBox</h1>
                    <p style={{ color: 'var(--text-secondary)' }}>Search, Stream, Download</p>
                </div>
            </header>

            <main className="container">
                <SearchBar onSearch={handleSearch} />

                {loading && (
                    <div style={{ textAlign: 'center', padding: '2rem' }}>
                        <div className="spinner" style={{
                            width: '40px', height: '40px',
                            border: '3px solid rgba(255,255,255,0.1)',
                            borderTopColor: 'var(--accent-primary)',
                            borderRadius: '50%',
                            animation: 'spin 1s linear infinite',
                            margin: '0 auto'
                        }}></div>
                        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
                    </div>
                )}

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                    gap: '2rem',
                    paddingBottom: '4rem'
                }}>
                    {results.map((item) => (
                        <MovieCard key={item.id} movie={item} onClick={handleItemClick} />
                    ))}
                </div>

                {results.length === 0 && !loading && (
                    <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: '4rem' }}>
                        <p>Start by searching for a movie or TV show.</p>
                    </div>
                )}
            </main>

            {selectedItem && (
                <DetailsModal
                    item={selectedItem}
                    onClose={() => setSelectedItem(null)}
                    onDownload={handleDownload}
                    onStream={handleStream}
                    progress={downloadProgress}
                />
            )}

            {detailsLoading && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    background: 'rgba(0,0,0,0.5)', zIndex: 2000,
                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                    <div className="spinner" style={{
                        width: '40px', height: '40px',
                        border: '3px solid rgba(255,255,255,0.1)',
                        borderTopColor: 'var(--accent-primary)',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                    }}></div>
                </div>
            )}
        </div>
    );
}

export default App;
