
import asyncio
from moviebox.search import Search
from moviebox.models import SubjectType
import aiohttp

async def inspect_search():
    query = "Naruto"
    print(f"Searching for: {query}")
    
    async with aiohttp.ClientSession() as session:
        # Search for TV Series
        search = Search(session=session, query=query, subject_type=SubjectType.TV_SERIES)
        results = await search.get_content_model()
        
        print(f"\nFound {len(results.items)} results:")
        for item in results.items:
            print(f"- Title: {item.title}")
            print(f"  ID: {item.id}")
            print("-" * 20)

if __name__ == "__main__":
    asyncio.run(inspect_search())
