import React from 'react';

const DetailsModal = ({ item, onClose, onDownload, onStream, progress }) => {
    const [selectedSeason, setSelectedSeason] = React.useState(null);
    const [selectedEpisode, setSelectedEpisode] = React.useState(1);

    React.useEffect(() => {
        if (item && item.seasons && item.seasons.length > 0) {
            setSelectedSeason(item.seasons[0]);
            setSelectedEpisode(1);
        }
    }, [item]);

    if (!item) return null;

    const handleStreamClick = () => {
        if (item.type === 'series' || item.type === 'anime') {
            if (!selectedSeason) {
                alert("Please select a season");
                return;
            }
            onStream(item, selectedSeason.season_number, selectedEpisode);
        } else {
            onStream(item);
        }
    };

    const handleDownloadClick = () => {
        if (item.type === 'series' || item.type === 'anime') {
            if (!selectedSeason) {
                alert("Please select a season");
                return;
            }
            onDownload(item, selectedSeason.season_number, selectedEpisode);
        } else {
            onDownload(item);
        }
    };

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            backdropFilter: 'blur(5px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '20px'
        }} onClick={onClose}>
            <div className="card animate-fade-in" style={{
                maxWidth: '800px',
                width: '100%',
                maxHeight: '90vh',
                overflowY: 'auto',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative'
            }} onClick={e => e.stopPropagation()}>

                <button onClick={onClose} style={{
                    position: 'absolute',
                    top: '10px',
                    right: '10px',
                    background: 'rgba(0,0,0,0.5)',
                    border: 'none',
                    color: 'white',
                    width: '30px',
                    height: '30px',
                    borderRadius: '50%',
                    cursor: 'pointer',
                    zIndex: 10
                }}>×</button>

                <div className="modal-content-layout">
                    {/* Cover Image Area */}
                    <div style={{ height: '300px', position: 'relative' }}>
                        {item.poster_url && (
                            <img src={item.poster_url} alt={item.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        )}
                        <div style={{
                            position: 'absolute',
                            bottom: 0,
                            left: 0,
                            right: 0,
                            background: 'linear-gradient(to top, var(--bg-secondary), transparent)',
                            height: '100px'
                        }}></div>
                    </div>

                    <div style={{ padding: '2rem' }}>
                        <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{item.title}</h2>
                        <div style={{ display: 'flex', gap: '1rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                            <span>{item.year}</span>
                            <span>{item.rating || 'N/A'}</span>
                            <span style={{ textTransform: 'capitalize' }}>{item.type}</span>
                        </div>

                        <p style={{ lineHeight: '1.6', marginBottom: '2rem', color: '#d1d5db' }}>
                            {item.plot || 'No plot available.'}
                        </p>

                        {(item.type === 'series' || item.type === 'anime') && (
                            <div style={{ marginBottom: '2rem', background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '8px' }}>
                                <h3 style={{ marginBottom: '1rem', fontSize: '1.2rem' }}>Select Episode</h3>
                                {item.seasons && item.seasons.length > 0 ? (
                                    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                            <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Season</label>
                                            <select
                                                value={selectedSeason ? selectedSeason.season_number : ''}
                                                onChange={(e) => {
                                                    const season = item.seasons.find(s => s.season_number === parseInt(e.target.value));
                                                    setSelectedSeason(season);
                                                    setSelectedEpisode(1);
                                                }}
                                                style={{
                                                    padding: '0.5rem',
                                                    background: 'var(--bg-primary)',
                                                    color: 'white',
                                                    border: '1px solid rgba(255,255,255,0.1)',
                                                    borderRadius: '4px',
                                                    minWidth: '100px'
                                                }}
                                            >
                                                {item.seasons.map(s => (
                                                    <option key={s.season_number} value={s.season_number}>
                                                        Season {s.season_number}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>

                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                            <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Episode</label>
                                            <select
                                                value={selectedEpisode}
                                                onChange={(e) => setSelectedEpisode(parseInt(e.target.value))}
                                                style={{
                                                    padding: '0.5rem',
                                                    background: 'var(--bg-primary)',
                                                    color: 'white',
                                                    border: '1px solid rgba(255,255,255,0.1)',
                                                    borderRadius: '4px',
                                                    minWidth: '100px'
                                                }}
                                            >
                                                {selectedSeason && Array.from({ length: selectedSeason.max_episodes }, (_, i) => i + 1).map(ep => (
                                                    <option key={ep} value={ep}>
                                                        Episode {ep}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>
                                    </div>
                                ) : (
                                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>
                                        Season information not available. You can still stream or download, and the first episode will be selected.
                                    </p>
                                )}
                            </div>
                        )}

                        {progress ? (
                            <div style={{ marginBottom: '1rem' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                    <span>Downloading...</span>
                                    <span>{typeof progress === 'object' ? (progress.percentage || '0%') : progress}</span>
                                </div>
                                <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', overflow: 'hidden' }}>
                                    <div style={{
                                        width: typeof progress === 'object' ? (progress.percentage || '0%') : '0%',
                                        height: '100%',
                                        background: 'var(--accent-primary)',
                                        transition: 'width 0.3s ease'
                                    }}></div>
                                </div>
                                {typeof progress === 'object' && (
                                    <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                                        {progress.speed && <span>{progress.speed} </span>}
                                        {progress.eta && <span>• ETA: {progress.eta}</span>}
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div style={{ display: 'flex', gap: '1rem' }}>
                                <button className="btn btn-primary" onClick={handleStreamClick}>
                                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '8px' }}>
                                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                                    </svg>
                                    Stream Now
                                </button>
                                <button className="btn" style={{ background: 'rgba(255,255,255,0.1)', color: 'white' }} onClick={handleDownloadClick}>
                                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '8px' }}>
                                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                        <polyline points="7 10 12 15 17 10"></polyline>
                                        <line x1="12" y1="15" x2="12" y2="3"></line>
                                    </svg>
                                    Download
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DetailsModal;
