import asyncio
import sys
from moviebox_api import Session, Search, SubjectType

async def debug_search():
    session = Session()
    
    # Test 1: Search for "Naruto [Japanese]"
    print("=== Test 1: Searching for 'Naruto [Japanese]' ===")
    search = Search(session=session, query="Naruto [Japanese]", subject_type=SubjectType.TV_SERIES)
    results = await search.get_content_model()
    
    print(f"Found {len(results.items)} results:")
    for i, item in enumerate(results.items[:5]):  # Show first 5
        print(f"{i+1}. {item.title}")
    
    # Test 2: Search for just "Naruto"
    print("\n=== Test 2: Searching for 'Naruto' ===")
    search2 = Search(session=session, query="Naruto", subject_type=SubjectType.TV_SERIES)
    results2 = await search2.get_content_model()
    
    print(f"Found {len(results2.items)} results:")
    for i, item in enumerate(results2.items[:10]):  # Show first 10
        print(f"{i+1}. {item.title}")
    
    await session.close()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(debug_search())
