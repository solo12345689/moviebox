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
            if (selectedSeason && selectedEpisode) {
                onStream({ ...item, type: item.type }, selectedSeason.season_number, selectedEpisode);
            } else {
                alert('Please select a season and episode');
            }
        } else {
            onStream({ ...item, type: 'movie' });
        }
    };

    const handleDownloadClick = () => {
        if (item.type === 'series' || item.type === 'anime') {
            if (selectedSeason && selectedEpisode) {
                onDownload(item, selectedSeason.season_number, selectedEpisode);
            } else {
                alert('Please select a season and episode');
            }
        } else {
            onDownload(item);
        }
    };

    return (
        <div className="modal-backdrop" onClick={onClose}>
            <div className="modal-content animate-fade-in" onClick={e => e.stopPropagation()}>

                <button onClick={onClose} style={{
                    position: 'absolute',
                    top: '15px',
                    right: '15px',
                    background: 'rgba(0,0,0,0.5)',
                    border: 'none',
                    color: 'white',
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    cursor: 'pointer',
                    zIndex: 20,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.2rem'
                }}>×</button>

                {/* Poster Side */}
                <div style={{
                    flex: '0 0 40%',
                    position: 'relative',
                    minHeight: '300px'
                }}>
                    {item.poster_url ? (
                        <img src={item.poster_url} alt={item.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                        <div style={{ width: '100%', height: '100%', background: '#1a1a20', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>No Poster</div>
                    )}
                    <div style={{
                        position: 'absolute',
                        inset: 0,
                        background: 'linear-gradient(to right, transparent 80%, var(--bg-surface) 100%)'
                    }}></div>
                    <div style={{
                        position: 'absolute',
                        inset: 0,
                        background: 'linear-gradient(to top, var(--bg-surface) 0%, transparent 50%)'
                    }}></div>
                </div>

                {/* Content Side */}
                <div style={{
                    flex: '1',
                    padding: '2.5rem',
                    overflowY: 'auto',
                    display: 'flex',
                    flexDirection: 'column'
                }}>
                    <h2 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', lineHeight: 1.1 }}>{item.title}</h2>

                    <div style={{ display: 'flex', gap: '1rem', color: 'var(--text-muted)', marginBottom: '2rem', fontSize: '0.95rem', alignItems: 'center' }}>
                        <span style={{ background: 'rgba(255,255,255,0.1)', padding: '2px 8px', borderRadius: '4px' }}>{item.year}</span>
                        <span>{item.rating || 'N/A'}</span>
                        <span style={{ textTransform: 'capitalize', color: 'var(--primary)' }}>{item.type}</span>
                    </div>

                    <p style={{ lineHeight: '1.7', marginBottom: '2.5rem', color: 'var(--text-dim)', fontSize: '1.05rem' }}>
                        {item.plot || 'No plot available.'}
                    </p>

                    <div style={{ marginTop: 'auto' }}>
                        {(item.type === 'series' || item.type === 'anime') && (
                            <div style={{ marginBottom: '2rem', background: 'var(--bg-glass-light)', padding: '1.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)' }}>
                                <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Select Episode</h3>
                                {item.seasons && item.seasons.length > 0 ? (
                                    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                            <label style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Season</label>
                                            <select
                                                value={selectedSeason ? selectedSeason.season_number : ''}
                                                onChange={(e) => {
                                                    const season = item.seasons.find(s => s.season_number === parseInt(e.target.value));
                                                    setSelectedSeason(season);
                                                    setSelectedEpisode(1);
                                                }}
                                                className="input-glass"
                                                style={{ padding: '0.5rem 1rem', minWidth: '120px' }}
                                            >
                                                {item.seasons.map(s => (
                                                    <option key={s.season_number} value={s.season_number} style={{ background: 'var(--bg-surface)' }}>
                                                        Season {s.season_number}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>

                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                            <label style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Episode</label>
                                            <select
                                                value={selectedEpisode}
                                                onChange={(e) => setSelectedEpisode(parseInt(e.target.value))}
                                                className="input-glass"
                                                style={{ padding: '0.5rem 1rem', minWidth: '120px' }}
                                            >
                                                {selectedSeason && Array.from({ length: selectedSeason.max_episodes }, (_, i) => i + 1).map(ep => (
                                                    <option key={ep} value={ep} style={{ background: 'var(--bg-surface)' }}>
                                                        Episode {ep}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>
                                    </div>
                                ) : (
                                    <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: 0 }}>
                                        Season information not available.
                                    </p>
                                )}
                            </div>
                        )}

                        {progress ? (
                            <div style={{ marginBottom: '1rem', background: 'var(--bg-glass-light)', padding: '1.5rem', borderRadius: 'var(--radius-md)' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-main)' }}>
                                    <span>Downloading...</span>
                                    <span>{typeof progress === 'object' ? (progress.percentage || '0%') : progress}</span>
                                </div>
                                <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                                    <div style={{
                                        width: typeof progress === 'object' ? (progress.percentage || '0%') : '0%',
                                        height: '100%',
                                        background: 'var(--primary)',
                                        transition: 'width 0.3s ease'
                                    }}></div>
                                </div>
                                {typeof progress === 'object' && (
                                    <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                        {progress.speed && <span>{progress.speed} </span>}
                                        {progress.eta && <span>• ETA: {progress.eta}</span>}
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div style={{ display: 'flex', gap: '1rem' }}>
                                <button className="btn btn-primary" onClick={handleStreamClick} style={{ flex: 1 }}>
                                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                                    </svg>
                                    Stream Now
                                </button>
                                <button className="btn btn-glass" onClick={handleDownloadClick} style={{ flex: 1 }}>
                                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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
