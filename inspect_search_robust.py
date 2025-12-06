
import asyncio
import sys
from moviebox.search import Search
from moviebox.models import SubjectType
import aiohttp

async def inspect_search():
    query = "Naruto"
    print(f"Searching for: {query}", flush=True)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Search for TV Series
            print("Initializing search...", flush=True)
            search = Search(session=session, query=query, subject_type=SubjectType.TV_SERIES)
            print("Fetching results...", flush=True)
            results = await search.get_content_model()
            
            print(f"\nFound {len(results.items)} results:", flush=True)
            for item in results.items:
                print(f"- Title: {item.title}", flush=True)
                print(f"  ID: {item.id}", flush=True)
                print("-" * 20, flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(inspect_search())
