import asyncio
import sys
import os
from moviebox_api import MovieBox, SubjectType

# Add backend to path to import session
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

async def debug_tv_details():
    print("Initializing MovieBox...")
    # Create a new session for debugging
    mb = MovieBox()
    
    print("Searching for 'Breaking Bad'...")
    search_results = await mb.search("Breaking Bad", SubjectType.TV_SERIES)
    
    if not search_results.items:
        print("No results found!")
        return

    # Get the first result
    item = search_results.items[0]
    print(f"Found: {item.title} (ID: {item.id})")
    
    print("Fetching details...")
    details = await mb.get_details(item.id)
    
    print("\n--- Details Model Inspection ---")
    print(f"Type: {type(details)}")
    print(f"Dir: {dir(details)}")
    
    if hasattr(details, 'seasons'):
        print(f"\ndetails.seasons type: {type(details.seasons)}")
        print(f"details.seasons: {details.seasons}")
    else:
        print("\ndetails.seasons: Not found")
        
    if hasattr(details, 'resource'):
        print(f"\ndetails.resource type: {type(details.resource)}")
        if hasattr(details.resource, 'seasons'):
            print(f"details.resource.seasons: {details.resource.seasons}")
        else:
            print("details.resource.seasons: Not found")
    else:
        print("\ndetails.resource: Not found")
        
    # Try dict conversion
    try:
        if hasattr(details, 'dict'):
            d = details.dict()
            print("\n--- Dict Representation (Partial) ---")
            # Print keys to avoid spamming
            print(f"Keys: {d.keys()}")
            if 'seasons' in d:
                print(f"dict['seasons']: {d['seasons']}")
            if 'resource' in d and 'seasons' in d['resource']:
                print(f"dict['resource']['seasons']: {d['resource']['seasons']}")
    except Exception as e:
        print(f"Error converting to dict: {e}")

if __name__ == "__main__":
    asyncio.run(debug_tv_details())
