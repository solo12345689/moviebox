import sys
import os
import asyncio
import traceback

# Add current directory to sys.path
sys.path.append(os.getcwd())

try:
    from backend.api import search, details, session, search_cache
    from moviebox_api import SubjectType
except ImportError as e:
    print(f"Import Error: {e}")
    traceback.print_exc()
    sys.exit(1)

async def verify():
    print("Starting verification...")
    try:
        print("Searching for 'Breaking Bad' (Series)...")
        # Force type='series'
        results = await search(query="Breaking Bad", type="series")
        
        if not results['results']:
            print("No results found.")
            return

        first_item = results['results'][0]
        print(f"First item: {first_item['title']} | Type: {first_item['type']}")
        
        if first_item['type'] != 'series':
            print("ERROR: Item type is not 'series'.")
            cached = search_cache[first_item['id']]
            item = cached['item']
            print(f"Item attributes: {dir(item)}")
        else:
            print("Item type is correct.")
            
        print(f"\nFetching details for {first_item['id']}...")
        # We need to get the item from cache to pass to details logic if we were calling api.details
        # But api.details does:
        # cached = search_cache[item_id]
        # item = cached["item"]
        # search_instance = cached["search_instance"]
        # details_provider = search_instance.get_item_details(item)
        # details_model = await details_provider.get_content_model()
        
        # Let's simulate this to inspect details_model
        if first_item['id'] in search_cache:
            cached = search_cache[first_item['id']]
            item = cached["item"]
            search_instance = cached["search_instance"]
            print(f"Item class: {type(item)}")
            
            details_provider = search_instance.get_item_details(item)
            details_model = await details_provider.get_content_model()
            
            print(f"Details Model Type: {type(details_model)}")
            print(f"Details Model Dir: {dir(details_model)}")
            try:
                print(f"Details Model Dict: {details_model.dict()}")
            except:
                pass
                
            if hasattr(details_model, 'resource'):
                print(f"Resource Dir: {dir(details_model.resource)}")
                if hasattr(details_model.resource, 'seasons'):
                     print(f"Seasons in resource: {len(details_model.resource.seasons)}")
                     if len(details_model.resource.seasons) > 0:
                         print(f"First Season Dir: {dir(details_model.resource.seasons[0])}")

        det = await details(first_item['id'])
        print(f"Details Title: {det['title']}")
        print(f"Details Type: {det.get('type')}")
        
        if 'seasons' in det:
            print(f"Seasons found: {len(det['seasons'])}")
            for s in det['seasons'][:3]:
                print(f"  Season {s['season_number']}: {s['max_episodes']} episodes")
        else:
            print("ERROR: No 'seasons' field in details.")
            
    except Exception as e:
        print(f"Verification failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(verify())
