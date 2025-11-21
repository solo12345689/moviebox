import asyncio
import subprocess
from moviebox_api import Session, Search, SubjectType
from moviebox_api.download import DownloadableTVSeriesFilesDetail, resolve_media_file_to_be_downloaded

def log(msg):
    print(msg)
    with open('mpv_test_log.txt', 'a') as f:
        f.write(str(msg) + '\n')

async def test_mpv():
    with open('mpv_test_log.txt', 'w') as f:
        f.write("Starting mpv test...\n")

    session = Session()
    query = "Naruto SD: Rock Lee & His Ninja Pals"
    log(f"Searching for: {query}")
    
    search = Search(session=session, query=query, subject_type=SubjectType.TV_SERIES)
    results = await search.get_content_model()
    
    if not results.items:
        log("No results found")
        return

    target_item = results.items[0]
    
    files_provider = DownloadableTVSeriesFilesDetail(session=session, item=target_item)
    files_metadata = await files_provider.get_content_model(season=1, episode=1)
    media_file = resolve_media_file_to_be_downloaded("BEST", files_metadata)
    
    log(f"Resolved URL: {media_file.url}")
    
    # Extract headers
    headers = {}
    if hasattr(session, '_headers'):
        headers.update(session._headers)
    if hasattr(session, '_client') and hasattr(session._client, 'headers'):
        headers.update(session._client.headers)
        
    ua = headers.get('User-Agent') or headers.get('user-agent')
    referer = headers.get('Referer') or headers.get('referer')
    
    log(f"UA: {ua}")
    log(f"Referer: {referer}")
    
    # Test 1: Minimal (UA + Referer)
    log("\nTest 1: UA + Referer")
    cmd = ["mpv", str(media_file.url), "--no-video", "--end=1"] # Just try to open and play 1 sec
    if ua:
        cmd.append(f"--user-agent={ua}")
    if referer:
        cmd.append(f"--referrer={referer}")
        
    try:
        subprocess.run(cmd, check=True, timeout=10)
        log("Test 1 SUCCESS")
    except subprocess.CalledProcessError as e:
        log(f"Test 1 FAILED: {e}")
    except Exception as e:
        log(f"Test 1 ERROR: {e}")

    # Test 2: With Origin via http-header-fields
    log("\nTest 2: UA + Referer + Origin")
    cmd = ["mpv", str(media_file.url), "--no-video", "--end=1"]
    if ua:
        cmd.append(f"--user-agent={ua}")
    if referer:
        cmd.append(f"--referrer={referer}")
    
    origin = headers.get('Origin') or headers.get('origin')
    if origin:
        cmd.append(f"--http-header-fields=Origin: {origin}")
        
    try:
        subprocess.run(cmd, check=True, timeout=10)
        log("Test 2 SUCCESS")
    except subprocess.CalledProcessError as e:
        log(f"Test 2 FAILED: {e}")
    except Exception as e:
        log(f"Test 2 ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_mpv())
