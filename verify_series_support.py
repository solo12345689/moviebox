import asyncio
from backend.api import search, details, session, search_cache

async def verify():
    print("Searching for 'Breaking Bad' (Series)...")
    # Force type='series' to ensure we get series results if possible, or try 'all'
    results = await search(query="Breaking Bad", type="series")
    
    if not results['results']:
        print("No results found.")
        return

    first_item = results['results'][0]
    print(f"First item: {first_item['title']} | Type: {first_item['type']}")
    
    if first_item['type'] != 'series':
        print("ERROR: Item type is not 'series'.")
        # Let's inspect the item object in cache to see why
        cached = search_cache[first_item['id']]
        item = cached['item']
        print(f"Item attributes: {dir(item)}")
        if hasattr(item, 'is_tv_series'):
            print(f"is_tv_series: {item.is_tv_series}")
    else:
        print("Item type is correct.")
        
    print(f"\nFetching details for {first_item['id']}...")
    try:
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
        print(f"Details failed: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(verify())
