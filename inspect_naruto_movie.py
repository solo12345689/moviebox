from moviebox_api import Session, Search, SubjectType
import asyncio
import sys

def log(msg):
    with open("inspect_naruto_movie.log", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

async def inspect():
    try:
        session = Session()
        query = "Naruto the Movie: Ninja Clash in the Land of Snow"
        log(f"Searching for: {query}")
        
        search = Search(session=session, query=query)
        results = await search.get_content_model()
        
        if results.items:
            item = results.items[0]
            log(f"\nTitle: {item.title}")
            log(f"SubjectType: {item.subjectType}")
            log(f"Is TV Series: {getattr(item, 'is_tv_series', 'N/A')}")
            log(f"Category: {getattr(item, 'category', 'N/A')}")
            log(f"Genre: {getattr(item, 'genre', 'N/A')}")
            
            # Check raw attributes
            log("\nRaw Attributes:")
            for attr in dir(item):
                if not attr.startswith('_') and not callable(getattr(item, attr)):
                    try:
                        val = getattr(item, attr)
                        log(f"{attr}: {val}")
                    except:
                        pass
        else:
            log("No results found.")
    except Exception as e:
        log(f"Error: {e}")

if __name__ == "__main__":
    # Clear log
    with open("inspect_naruto_movie.log", "w") as f:
        f.write("")
    asyncio.run(inspect())
