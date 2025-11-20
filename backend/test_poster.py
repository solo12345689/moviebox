from moviebox_api import Session, Search
import asyncio
import sys

async def main():
    session = Session()
    search = Search(session=session, query="Avatar")
    results = await search.get_content_model()
    
    if results.items:
        item = results.items[0]
        print("First item attributes:")
        print(dir(item))
        print("\nFirst item dict (if available):")
        if hasattr(item, '__dict__'):
            for key, value in item.__dict__.items():
                print(f"  {key}: {value}")
        
        # Check common poster field names
        poster_fields = ['poster_url', 'poster', 'image_url', 'image', 'cover_url', 'cover', 'boxCover']
        print("\nChecking poster fields:")
        for field in poster_fields:
            if hasattr(item, field):
                print(f"  {field}: {getattr(item, field)}")

if __name__ == "__main__":
    asyncio.run(main())
