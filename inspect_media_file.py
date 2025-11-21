import asyncio
from moviebox_api import Session, Search, SubjectType
from moviebox_api.download import DownloadableTVSeriesFilesDetail, resolve_media_file_to_be_downloaded

def log(msg):
    print(msg)
    with open('inspect_media_log.txt', 'a') as f:
        f.write(str(msg) + '\n')

async def inspect_media_file():
    with open('inspect_media_log.txt', 'w') as f:
        f.write("Starting inspection...\n")

    session = Session()
    query = "Naruto SD: Rock Lee & His Ninja Pals"
    log(f"Searching for: {query}")
    
    search = Search(session=session, query=query, subject_type=SubjectType.TV_SERIES)
    results = await search.get_content_model()
    
    if not results.items:
        log("No results found")
        return

    target_item = results.items[0]
    log(f"Selected: {target_item.title}")
    
    files_provider = DownloadableTVSeriesFilesDetail(session=session, item=target_item)
    files_metadata = await files_provider.get_content_model(season=1, episode=1)
    media_file = resolve_media_file_to_be_downloaded("BEST", files_metadata)
    
    log(f"Resolved URL: {media_file.url}")
    log(f"MediaFile dir: {dir(media_file)}")
    if hasattr(media_file, 'headers'):
        log(f"Headers: {media_file.headers}")
    
    log(f"Session dir: {dir(session)}")
    
    # Try to find headers in session private attributes
    headers = {}
    if hasattr(session, '_headers'):
        headers.update(session._headers)
    
    if hasattr(session, '_client') and hasattr(session._client, 'headers'):
        headers.update(session._client.headers)
        
    log(f"Found headers (private): {headers}")
    
    # Check cookies
    cookies = {}
    if hasattr(session, '_cookies'):
        cookies.update(session._cookies)
    if hasattr(session, 'cookies'):
        cookies.update(session.cookies)
        
    log(f"Found cookies: {cookies}")

    # Test URL with requests
    import requests
    try:
        log("Testing URL with requests...")
        # Test 1: With extracted headers
        if headers:
            # Convert httpx headers to dict if needed
            headers_dict = dict(headers)
            r = requests.head(media_file.url, headers=headers_dict)
            log(f"With Extracted headers: {r.status_code}")
        
        # Test 2: With Referer
        ref_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://moviebox.com/" 
        }
        r = requests.head(media_file.url, headers=ref_headers)
        log(f"With Referer: {r.status_code}")
            
    except Exception as e:
        log(f"Requests test failed: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(inspect_media_file())
    except Exception as e:
        log(f"Fatal error: {e}")
        import traceback
        log(traceback.format_exc())
