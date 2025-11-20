from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional, Any
from moviebox_api import Session, Search, SubjectType, MovieAuto, TVSeriesDetails
from moviebox_api.download import (
    MediaFileDownloader, 
    DownloadableMovieFilesDetail, 
    DownloadableTVSeriesFilesDetail,
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
async def search(query: str, page: int = 1, content_type: str = "all"):
    try:
        subject_type = SubjectType.ALL
        if content_type.lower() == "movie":
            subject_type = SubjectType.MOVIES
        elif content_type.lower() == "series":
            subject_type = SubjectType.TV_SERIES
        elif content_type.lower() == "anime":
            # moviebox_api doesn't have ANIME type, so use TV_SERIES
            subject_type = SubjectType.TV_SERIES
            
        search_instance = Search(session=session, query=query, page=page, subject_type=subject_type)
        results_model = await search_instance.get_content_model()
        
        items = []
        if hasattr(results_model, 'items'):
            for item in results_model.items:
                # Generate a temporary ID for this item
                item_id = str(uuid.uuid4())
                # Determine item type more accurately
                item_type = "movie"  # default
                if content_type.lower() == "anime":
                    item_type = "anime"
                elif content_type.lower() == "series" or getattr(item, 'is_tv_series', False):
                    item_type = "series"
                elif content_type.lower() == "movie":
                    item_type = "movie"
                # For 'all', try to infer from item attributes
                elif hasattr(item, 'category'):
                    category = str(getattr(item, 'category', '')).lower()
                    if 'series' in category or 'tv' in category:
                        item_type = "series"
                    elif 'anime' in category:
                        item_type = "anime"
                
                search_cache[item_id] = {
                    "item": item,
                    "search_instance": search_instance,
                    "type": item_type
                }
                
                # Try multiple possible poster field names
                poster_url = None
                
                # First try 'cover' field which is the correct one
                if hasattr(item, 'cover') and item.cover:
                    cover = item.cover
                    # The cover is likely a Pydantic model with a 'url' attribute
                    if hasattr(cover, 'url'):
                        poster_url = str(cover.url)
                    elif isinstance(cover, str):
                        poster_url = cover
                
                # Fallback to other possible field names
                if not poster_url:
                    for field_name in ['boxCover', 'cover_url', 'poster_url', 'image_url', 'poster', 'image']:
                        if hasattr(item, field_name):
                            value = getattr(item, field_name)
                            if value:
                                # Try to extract URL if it's an object
                                if hasattr(value, 'url'):
                                    poster_url = str(value.url)
                                else:
                                    poster_url = str(value)
                                break
                
                items.append({
                    "id": item_id,
                    "title": getattr(item, 'title', 'Unknown'),
                    "year": getattr(item, 'year', None),
                    "poster_url": poster_url,
                    "type": item_type
                })
        
        return {"results": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug/search")
async def debug_search(query: str):
    """Debug endpoint to see raw search result structure"""
    try:
        search_instance = Search(session=session, query=query)
        results_model = await search_instance.get_content_model()
        
        if hasattr(results_model, 'items') and results_model.items:
            item = results_model.items[0]
            # Return all attributes
            item_dict = {}
            for attr in dir(item):
                if not attr.startswith('_'):
                    try:
                        value = getattr(item, attr)
                        # Skip methods
                        if not callable(value):
                            item_dict[attr] = str(value)
                    except:
                        pass
            return {"first_item_attributes": item_dict}
        return {"error": "No results"}
    except Exception as e:
        return {"error": str(e)}

@router.get("/details/{item_id}")
async def details(item_id: str):
    if item_id not in search_cache:
        raise HTTPException(status_code=404, detail="Item not found in cache. Please search again.")
    
    cached = search_cache[item_id]
    item = cached["item"]
    search_instance = cached["search_instance"]
    item_type = cached.get("type", "movie")
    
    try:
        # Use the search instance to get details for this item
        details_provider = search_instance.get_item_details(item)
        details_model = await details_provider.get_content_model()
        
        response = {
            "title": getattr(details_model, 'title', getattr(item, 'title', 'Unknown')),
            "year": getattr(details_model, 'year', getattr(item, 'year', None)),
            "plot": getattr(details_model, 'plot', "No plot available"),
            "rating": getattr(details_model, 'rating', None),
            "trailer": getattr(details_model, 'trailer', None),
            "type": item_type
        }
        
        # Extract seasons for TV series and anime
        if item_type in ["series", "anime"]:
            seasons_data = []
            try:
                # Try multiple paths to find season data
                seasons_list = None
                
                # Path 1: details_model.resData.resource.seasons
                if hasattr(details_model, 'resData'):
                    if hasattr(details_model.resData, 'resource') and hasattr(details_model.resData.resource, 'seasons'):
                        seasons_list = details_model.resData.resource.seasons
                    elif hasattr(details_model.resData, 'seasons'):
                        seasons_list = details_model.resData.seasons
                
                # Path 2: details_model.resource.seasons (fallback)
                elif hasattr(details_model, 'resource') and hasattr(details_model.resource, 'seasons'):
                    seasons_list = details_model.resource.seasons
                
                # Path 3: details_model.seasons
                elif hasattr(details_model, 'seasons'):
                    seasons_list = details_model.seasons
                
                # Path 4: Try to get from dict representation
                elif hasattr(details_model, 'dict'):
                    try:
                        model_dict = details_model.dict()
                        if 'resData' in model_dict:
                            if 'resource' in model_dict['resData'] and 'seasons' in model_dict['resData']['resource']:
                                seasons_list = model_dict['resData']['resource']['seasons']
                            elif 'seasons' in model_dict['resData']:
                                seasons_list = model_dict['resData']['seasons']
                        elif 'resource' in model_dict and 'seasons' in model_dict['resource']:
                            seasons_list = model_dict['resource']['seasons']
                    except:
                        pass
                
                # Extract season data
                if seasons_list:
                    for season in seasons_list:
                        # Handle both object and dict formats
                        if isinstance(season, dict):
                            season_num = season.get('se', season.get('season_number', 0))
                            max_ep = season.get('maxEp', season.get('max_episodes', season.get('episode_count', 0)))
                        else:
                            season_num = getattr(season, 'se', getattr(season, 'season_number', 0))
                            max_ep = getattr(season, 'maxEp', getattr(season, 'max_episodes', getattr(season, 'episode_count', 0)))
                        
                        if season_num and max_ep:
                            seasons_data.append({
                                "season_number": season_num,
                                "max_episodes": max_ep,
                            })
            except Exception as e:
                # Log error but don't fail the entire request
                print(f"Error extracting seasons: {e}")
            
            response["seasons"] = seasons_data
            
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def download_task(query: str, season: Optional[int] = None, episode: Optional[int] = None):
    try:
        # 1. Search
        await manager.broadcast({"status": "searching", "message": f"Searching for {query}..."})
        
        subject_type = SubjectType.ALL
        if season is not None:
             subject_type = SubjectType.TV_SERIES
             
        search_instance = Search(session=session, query=query, subject_type=subject_type)
        results = await search_instance.get_content_model()
        
        if not results.items:
            await manager.broadcast({"status": "error", "message": "No results found"})
            return

        item = results.items[0]
        
        # 2. Get Files
        await manager.broadcast({"status": "resolving", "message": "Resolving files..."})
        
        media_file = None
        filename = item
        
        if season is not None and episode is not None:
             # TV Series
             files_provider = DownloadableTVSeriesFilesDetail(session=session, item=item)
             files_metadata = await files_provider.get_content_model(season=season, episode=episode)
             media_file = resolve_media_file_to_be_downloaded("BEST", files_metadata)
             # For filename, we might need to adjust or let downloader handle it
        else:
             # Movie
             files_provider = DownloadableMovieFilesDetail(session=session, item=item)
             files_metadata = await files_provider.get_content_model()
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
        
        if season is not None and episode is not None:
            await downloader.run(
                media_file=media_file, 
                filename=item, 
                progress_hook=progress_hook,
                season=season,
                episode=episode
            )
        else:
            await downloader.run(media_file=media_file, filename=item, progress_hook=progress_hook)
            
        await manager.broadcast({"status": "completed", "message": "Download complete!"})

    except Exception as e:
        print(f"Download failed: {e}")
        await manager.broadcast({"status": "error", "message": f"Download failed: {str(e)}"})

@router.post("/download")
async def download(query: str, season: Optional[int] = None, episode: Optional[int] = None):
    # Start background task
    asyncio.create_task(download_task(query, season, episode))
    return {"status": "started", "message": f"Download started for {query}"}

@router.post("/stream")
async def stream(query: str, season: Optional[int] = None, episode: Optional[int] = None):
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
        # Use Popen with stdin pipe to auto-confirm if prompted
        
        cmd = ["moviebox"]
        if season is not None and episode is not None:
            cmd.extend(["download-series", query, "-s", str(season), "-e", str(episode)])
        else:
            cmd.extend(["download-movie", query])
            
        cmd.extend(["--stream-via", "mpv", "--no-caption"])
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            text=True
        )
        # Send 'y' to confirm selection
        try:
            process.stdin.write("y\n")
            process.stdin.flush()
        except Exception:
            pass
        
        return {"status": "streaming", "message": "Stream launched in external player"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
