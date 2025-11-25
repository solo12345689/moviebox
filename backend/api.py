from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Any
from moviebox_api import Session, Search, SubjectType, MovieAuto, TVSeriesDetails
from moviebox_api.download import (
    MediaFileDownloader, 
    DownloadableMovieFilesDetail, 
    DownloadableTVSeriesFilesDetail,
    resolve_media_file_to_be_downloaded
)
from moviebox_api.extractor._core import ItemJsonDetailsModel
from moviebox_api.extractor.models.json import SubjectModel, SubjectTrailerModel
from typing import Optional, Union, get_args, get_origin
import pydantic
import asyncio
import uuid
import json

# --- Monkeypatch for Pydantic Validation Error ---
def unwrap_annotation(annotation):
    origin = get_origin(annotation)
    if origin is Union:
        args = get_args(annotation)
        for arg in args:
            if isinstance(arg, type) and arg is not type(None):
                return arg
    return annotation

def patch_moviebox_models():
    try:
        # Patch SubjectModel directly since we imported it
        if hasattr(SubjectModel, 'model_fields') and 'trailer' in SubjectModel.model_fields:
            # Replace FieldInfo object to allow None
            from pydantic.fields import FieldInfo
            SubjectModel.model_fields['trailer'] = FieldInfo(annotation=Optional[Union[dict, SubjectTrailerModel]], default=None)
            
            if hasattr(SubjectModel, 'model_rebuild'):
                SubjectModel.model_rebuild(force=True)
            
            # Rebuild parents
            # We need to find ResDataModel to rebuild it
            if 'resData' in ItemJsonDetailsModel.model_fields:
                ResDataModel = unwrap_annotation(ItemJsonDetailsModel.model_fields['resData'].annotation)
                if hasattr(ResDataModel, 'model_rebuild'):
                    ResDataModel.model_rebuild(force=True)
            
            if hasattr(ItemJsonDetailsModel, 'model_rebuild'):
                ItemJsonDetailsModel.model_rebuild(force=True)
                
            print("Successfully patched SubjectModel.trailer and rebuilt models")
    except Exception as e:
        print(f"Failed to patch models: {e}")
        import traceback
        traceback.print_exc()

# Apply patch immediately
patch_moviebox_models()

router = APIRouter()

# Global session with bypass headers
import random

# Create session with anti-detection headers
session = Session()

# Add residential-looking headers to bypass cloud IP detection
if hasattr(session, '_client') and hasattr(session._client, 'headers'):
    # Realistic mobile User-Agents (rotate between them)
    mobile_user_agents = [
        'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36'
    ]
    
    # Generate a random residential IP (for X-Forwarded-For)
    # Using common residential IP ranges
    residential_ip = f"{random.choice([49, 103, 106, 117, 122])}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    session._client.headers.update({
        'User-Agent': random.choice(mobile_user_agents),
        'X-Forwarded-For': residential_ip,
        'X-Real-IP': residential_ip,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    })
    print(f"[BYPASS] Using residential IP: {residential_ip}")

# Monkeypatch httpx Response to handle encoding errors
import httpx

original_text = httpx.Response.text

@property
def patched_text(self):
    """
    Patched text property that handles encoding errors gracefully.
    Tries multiple encodings and uses 'replace' error handling.
    """
    if not hasattr(self, '_content'):
        return ""
    
    # Try multiple encodings
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings_to_try:
        try:
            return self._content.decode(encoding, errors='replace')
        except (UnicodeDecodeError, AttributeError):
            continue
    
    # Fallback: decode with utf-8 and replace errors
    return self._content.decode('utf-8', errors='replace')

# Apply the monkeypatch
httpx.Response.text = patched_text
print("[BYPASS] Applied encoding error handling monkeypatch")

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
                # Determine item type more accurately
                item_type = "movie"  # default
                
                # Check explicit subjectType from item if available
                if hasattr(item, 'subjectType'):
                    if item.subjectType == SubjectType.TV_SERIES:
                        item_type = "series"
                    elif item.subjectType == SubjectType.MOVIES:
                        item_type = "movie"
                
                # Refine based on content_type filter
                if content_type.lower() == "anime":
                    item_type = "anime"
                elif content_type.lower() == "series":
                    item_type = "series"
                elif content_type.lower() == "movie":
                    item_type = "movie"
                
                # Fallback to attributes if still default or ambiguous
                if item_type == "movie" and getattr(item, 'is_tv_series', False):
                    item_type = "series"
                
                # Check category and genre for Anime/Series detection
                category = str(getattr(item, 'category', '')).lower()
                genres = getattr(item, 'genre', [])
                if genres:
                    genres = [str(g).lower() for g in genres]
                
                if 'anime' in category or 'anime' in genres:
                    if item_type == "movie":
                        item_type = "anime_movie"
                    else:
                        item_type = "anime"
                elif 'series' in category or 'tv' in category:
                    item_type = "series"
                
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

async def warmup_session():
    """Warm up the session by performing a dummy search"""
    print("Warming up session...")
    try:
        # Perform a lightweight search
        search_instance = Search(session=session, query="test")
        await search_instance.get_content_model()
        print("Session warmed up successfully.")
    except Exception as e:
        print(f"Warmup failed: {e}")

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
async def stream(query: str, id: Optional[str] = None, content_type: str = "all", season: Optional[int] = None, episode: Optional[int] = None, mode: str = "play"):
    try:
        # 1. Determine SubjectType
        subject_type = SubjectType.ALL
        if content_type.lower() == "movie" or content_type.lower() == "anime_movie":
            subject_type = SubjectType.MOVIES
        elif content_type.lower() == "series":
            subject_type = SubjectType.TV_SERIES
        elif content_type.lower() == "anime":
            subject_type = SubjectType.TV_SERIES

        # 2. Search for the item to get the full object
        # We need the item object to use Downloadable...FilesDetail
        search_instance = Search(session=session, query=query, subject_type=subject_type)
        results = await search_instance.get_content_model()
        
        if not results.items:
            raise HTTPException(status_code=404, detail="Content not found")
            
        # 3. Find the correct item
        target_item = None
        if id:
            # Try to match by ID if provided
            for item in results.items:
                # Check both 'id' and 'subjectId' attributes
                item_id = getattr(item, 'id', getattr(item, 'subjectId', None))
                if str(item_id) == str(id):
                    target_item = item
                    break
        
        # Fallback: use the first item if ID match fails or not provided
        if not target_item:
            target_item = results.items[0]
            
        # 4. Resolve Media File with encoding error handling
        media_file = None
        quality_options = ["BEST", "WORST", "720P", "480P", "360P"]
        
        for quality in quality_options:
            try:
                if season is not None and episode is not None:
                    # TV Series / Anime
                    files_provider = DownloadableTVSeriesFilesDetail(session=session, item=target_item)
                    files_metadata = await files_provider.get_content_model(season=season, episode=episode)
                    media_file = resolve_media_file_to_be_downloaded(quality, files_metadata)
                else:
                    # Movie
                    files_provider = DownloadableMovieFilesDetail(session=session, item=target_item)
                    files_metadata = await files_provider.get_content_model()
                    media_file = resolve_media_file_to_be_downloaded(quality, files_metadata)
                
                # If we got a media file, break out of the loop
                if media_file and media_file.url:
                    print(f"[SUCCESS] Resolved media file with quality: {quality}")
                    break
                    
            except UnicodeDecodeError as e:
                print(f"[ENCODING ERROR] Quality {quality} failed with encoding error: {e}")
                # Try next quality option
                continue
            except Exception as e:
                print(f"[ERROR] Quality {quality} failed: {e}")
                # Try next quality option
                continue
             
        if not media_file or not media_file.url:
            raise HTTPException(status_code=404, detail="Playable stream URL not found")

        # Return URL if mode is 'url'
        if mode == "url":
            # Return a proxy URL that routes through our backend
            # This bypasses 403 Forbidden errors from streaming providers
            from urllib.parse import quote
            proxy_url = f"/api/proxy-stream?url={quote(str(media_file.url))}"
            return {"status": "success", "url": proxy_url, "title": target_item.title, "direct_url": str(media_file.url)}

        # 5. Launch MPV
        import subprocess
        import shutil
        
        if not shutil.which("mpv"):
            raise HTTPException(status_code=500, detail="mpv player not found. Please install mpv to stream.")
            
        # Extract headers from session
        headers = {}
        if hasattr(session, '_headers'):
            headers.update(session._headers)
        if hasattr(session, '_client') and hasattr(session._client, 'headers'):
            headers.update(session._client.headers)
            
        # Construct mpv command
        cmd = ["mpv", str(media_file.url), f"--title={target_item.title}"]
        
        # Case-insensitive header map
        headers_lower = {k.lower(): v for k, v in headers.items()}
        
        # Add User-Agent
        if "user-agent" in headers_lower:
            cmd.append(f"--user-agent={headers_lower['user-agent']}")
            
        # Add Referer
        if "referer" in headers_lower:
            cmd.append(f"--referrer={headers_lower['referer']}")
            
        # Add other headers via http-header-fields
        other_headers = []
        allowed_headers = ["origin", "cookie", "authorization"]
        
        for k, v in headers.items():
            if k.lower() in allowed_headers:
                # Escape commas if present (though unlikely for these)
                # mpv might not support escaping, so better to skip if comma present?
                # Or just hope for the best. Origin/Cookie usually don't have commas (Cookie uses semicolon).
                other_headers.append(f"{k}: {v}")
        
        if other_headers:
            cmd.append(f"--http-header-fields={','.join(other_headers)}")
        
        # Log the command
        with open("stream_debug.log", "a") as f:
            f.write(f"Launching command: {cmd}\n")
            f.write(f"URL: {media_file.url}\n")

        # Run non-blocking, redirect output to file
        outfile = open("mpv_output.log", "w")
        subprocess.Popen(cmd, stdout=outfile, stderr=subprocess.STDOUT)
        
        return {"status": "streaming", "message": f"Streaming {target_item.title}..."}

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        with open("stream_error.log", "a") as f:
            f.write(f"Stream error: {e}\n")
            f.write(f"Traceback:\n{error_details}\n")
        print(f"Stream error: {e}")
        
        # If mode is 'url', return a JSON error response instead of raising
        if mode == "url":
            return {"status": "error", "message": str(e), "details": error_details}
        
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/proxy-stream")
async def proxy_stream(url: str):
    """
    Proxy endpoint that streams video content with proper headers.
    This bypasses 403 Forbidden errors from streaming providers.
    """
    try:
        import httpx
        
        # Extract headers from session
        headers = {}
        if hasattr(session, '_headers'):
            headers.update(session._headers)
        if hasattr(session, '_client') and hasattr(session._client, 'headers'):
            headers.update(session._client.headers)
        
        # Ensure we have a User-Agent
        if 'User-Agent' not in headers and 'user-agent' not in headers:
            headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        # Stream the content from the source
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            async with client.stream('GET', url, headers=headers) as response:
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Failed to fetch stream: {response.status_code}"
                    )
                
                # Get content type from response
                content_type = response.headers.get('content-type', 'video/mp4')
                
                # Stream the response
                async def generate():
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        yield chunk
                
                return StreamingResponse(
                    generate(),
                    media_type=content_type,
                    headers={
                        'Accept-Ranges': 'bytes',
                        'Content-Type': content_type,
                    }
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy stream error: {str(e)}")

