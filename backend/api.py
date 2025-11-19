from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional, Any
from moviebox_api import Session, Search, SubjectType, MovieAuto
from moviebox_api.download import (
    MediaFileDownloader, 
    DownloadableMovieFilesDetail, 
    resolve_media_file_to_be_downloaded
)
import asyncio
import uuid
import json

router = APIRouter()

# Global session
session = Session()

# Simple in-memory cache: {uuid: item_object}
search_cache = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

class SearchResultItem(BaseModel):
    id: str
    title: str
    year: Optional[str] = None
    poster_url: Optional[str] = None
    type: str

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.get("/search", response_model=dict)
async def search(query: str, page: int = 1):
    try:
        search_instance = Search(session=session, query=query, page=page)
        results_model = await search_instance.get_content_model()
        
        items = []
        if hasattr(results_model, 'items'):
            for item in results_model.items:
                # Generate a temporary ID for this item
                item_id = str(uuid.uuid4())
                search_cache[item_id] = {
                    "item": item,
                    "search_instance": search_instance # Keep reference to search instance if needed
                }
                
                items.append({
                    "id": item_id,
                    "title": getattr(item, 'title', 'Unknown'),
                    "year": getattr(item, 'year', None),
                    "poster_url": getattr(item, 'poster_url', None),
                    "type": "movie" # Placeholder, need to detect type
                })
        
        return {"results": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/details/{item_id}")
async def details(item_id: str):
    if item_id not in search_cache:
        raise HTTPException(status_code=404, detail="Item not found in cache. Please search again.")
    
    cached = search_cache[item_id]
    item = cached["item"]
    search_instance = cached["search_instance"]
    
    try:
        # Use the search instance to get details for this item
        details_provider = search_instance.get_item_details(item)
        details_model = await details_provider.get_content_model()
        
        return {
            "title": getattr(details_model, 'title', getattr(item, 'title', 'Unknown')),
            "year": getattr(details_model, 'year', getattr(item, 'year', None)),
            "plot": getattr(details_model, 'plot', "No plot available"),
            "rating": getattr(details_model, 'rating', None),
            "trailer": getattr(details_model, 'trailer', None),
            # Add more fields as discovered
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def download_task(query: str):
    try:
        # 1. Search
        await manager.broadcast({"status": "searching", "message": f"Searching for {query}..."})
        search_instance = Search(session=session, query=query)
        results = await search_instance.get_content_model()
        
        if not results.items:
            await manager.broadcast({"status": "error", "message": "No results found"})
            return

        item = results.items[0]
        
        # 2. Get Files
        await manager.broadcast({"status": "resolving", "message": "Resolving files..."})
        # Assuming movie for now
        files_provider = DownloadableMovieFilesDetail(session=session, item=item)
        files_metadata = await files_provider.get_content_model()
        
        # 3. Resolve Quality
        media_file = resolve_media_file_to_be_downloaded("BEST", files_metadata)
        
        # 4. Download
        downloader = MediaFileDownloader()
        
        def progress_hook(progress):
            # progress is likely a dict or object. inspect it.
            # If it's from throttlebuster, it might be complex.
            # Let's assume it has percentage or similar.
            # We'll send the whole thing as string or dict if possible.
            try:
                # Convert to dict if it's an object
                data = progress if isinstance(progress, dict) else str(progress)
                # If it's a string, try to parse? 
                # Or just send as message.
                asyncio.run_coroutine_threadsafe(
                    manager.broadcast({"status": "downloading", "progress": data}),
                    asyncio.get_event_loop()
                )
            except Exception as e:
                print(f"Progress error: {e}")

        await manager.broadcast({"status": "started", "message": f"Starting download: {item.title}"})
        await downloader.run(media_file=media_file, filename=item, progress_hook=progress_hook)
        await manager.broadcast({"status": "completed", "message": "Download complete!"})

    except Exception as e:
        print(f"Download failed: {e}")
        await manager.broadcast({"status": "error", "message": f"Download failed: {str(e)}"})

@router.post("/download")
async def download(query: str):
    # Start background task
    asyncio.create_task(download_task(query))
    return {"status": "started", "message": f"Download started for {query}"}

@router.post("/stream")
async def stream(query: str):
    # For streaming, we might need to use the CLI wrapper or spawn mpv directly.
    # moviebox-api CLI uses mpv.
    # We can try to spawn mpv here.
    import subprocess
    import shutil
    try:
        if not shutil.which("mpv"):
            raise HTTPException(status_code=500, detail="mpv player not found. Please install mpv to stream.")

        # This is a hacky way to stream, assuming mpv is in path.
        # And assuming we can just run the cli command.
        # Better: use the library to get the stream URL and pass to mpv.
        # But getting stream URL might be complex.
        
        # Let's try to use the CLI command via subprocess for now as a fallback.
        subprocess.Popen(["moviebox", "download-movie", query, "--stream"])
        return {"status": "streaming", "message": "Stream launched in external player"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
