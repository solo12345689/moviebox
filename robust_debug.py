import sys
import traceback

def log(msg):
    print(msg)
    with open('robust_debug_log.txt', 'a') as f:
        f.write(str(msg) + '\n')

log("Starting robust debug script...")

try:
    log("Importing asyncio...")
    import asyncio
    
    log("Importing moviebox_api...")
    try:
        from moviebox_api import Search, SubjectType, Session
        log("moviebox_api imported successfully")
    except ImportError as e:
        log(f"Failed to import moviebox_api: {e}")
        sys.exit(1)

    async def run_debug():
        try:
            log("Initializing Session...")
            session = Session()
            
            log("Searching for 'Breaking Bad'...")
            search = Search(session=session, query="Breaking Bad", subject_type=SubjectType.TV_SERIES)
            results = await search.get_content_model()
            
            if not results.items:
                log("No results found")
                return
            
            item = results.items[0]
            log(f"Found item: {item.title}")
            
            log("Getting details...")
            details_provider = search.get_item_details(item)
            details = await details_provider.get_content_model()
            
            log(f"Details type: {type(details)}")
            log(f"Details dir: {dir(details)}")
            
            if hasattr(details, 'resData'):
                if hasattr(details.resData, 'resource'):
                    log(f"resData.resource type: {type(details.resData.resource)}")
                    log(f"resData.resource dir: {dir(details.resData.resource)}")
                    if hasattr(details.resData.resource, 'seasons'):
                        log(f"resData.resource.seasons: {details.resData.resource.seasons}")
            
            if hasattr(details, 'dict'):
                d = details.dict()
                if 'resData' in d and 'resource' in d['resData']:
                    log(f"Dict resData.resource keys: {d['resData']['resource'].keys()}")
                    if 'seasons' in d['resData']['resource']:
                        log(f"Dict resData.resource.seasons: {d['resData']['resource']['seasons']}")
                    
        except Exception as e:
            log(f"Error in async execution: {e}")
            log(traceback.format_exc())

    if __name__ == "__main__":
        asyncio.run(run_debug())

except Exception as e:
    log(f"Fatal error: {e}")
    log(traceback.format_exc())
