import asyncio
from moviebox_api import Session, Search, SubjectType
from moviebox_api.download import (
    DownloadableTVSeriesFilesDetail,
    resolve_media_file_to_be_downloaded
)

def log(msg):
    print(msg)
    with open('stream_resolution_log.txt', 'a') as f:
        f.write(str(msg) + '\n')

async def test_resolve_stream():
    with open('stream_resolution_log.txt', 'w') as f:
        f.write("Starting stream resolution test...\n")

    session = Session()
    query = "Naruto SD: Rock Lee & His Ninja Pals"
    log(f"Searching for: {query}")
    
    # Search as TV Series
    search = Search(session=session, query=query, subject_type=SubjectType.TV_SERIES)
    results = await search.get_content_model()
    
    if not results.items:
        log("No results found")
        return

    log(f"Found {len(results.items)} items")
    if len(results.items) > 0:
        first_item = results.items[0]
        log(f"First item dir: {dir(first_item)}")
        if hasattr(first_item, 'dict'):
            log(f"First item dict: {first_item.dict().keys()}")

    for i, item in enumerate(results.items):
        # Try to get title safely
        title = getattr(item, 'title', 'Unknown Title')
        log(f"{i}: {title}")

    # Assume we want the first one, or match by title
    target_item = results.items[0]
    log(f"\nSelected: {target_item.title}")
    
    # Resolve file for Season 1 Episode 1
    log("Resolving file for S1 E1...")
    files_provider = DownloadableTVSeriesFilesDetail(session=session, item=target_item)
    files_metadata = await files_provider.get_content_model(season=1, episode=1)
    
    media_file = resolve_media_file_to_be_downloaded("BEST", files_metadata)
    
    if media_file:
        log(f"Resolved URL: {media_file.url}")
        log(f"Resolution: {media_file.resolution}")
        log(f"Size: {media_file.size}")
    else:
        log("Failed to resolve media file")

if __name__ == "__main__":
    try:
        asyncio.run(test_resolve_stream())
    except Exception as e:
        log(f"Error: {e}")
