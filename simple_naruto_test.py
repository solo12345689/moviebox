import asyncio
import sys
from moviebox_api import Session, Search, SubjectType
import traceback

async def debug_search():
    try:
        session = Session()
        
        # Search for just "Naruto"
        print("Searching for 'Naruto'...")
        search = Search(session=session, query="Naruto", subject_type=SubjectType.TV_SERIES)
        results = await search.get_content_model()
        
        print(f"\nFound {len(results.items)} results")
        print("\nFirst 10 results:")
        for i, item in enumerate(results.items[:10]):
            title = getattr(item, 'title', 'Unknown')
            print(f"{i+1}. {title}")
        
        await session.close()
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(debug_search())
