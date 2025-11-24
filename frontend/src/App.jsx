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
