from moviebox_api import Session, Search, SubjectType
import asyncio
import sys
import json

# Redirect stdout to file
sys.stdout = open('api_data_test.txt', 'w', encoding='utf-8')

async def main():
    print("--- STARTING DATA TEST ---")
    try:
        session = Session()
        print("Session created")
        
        search = Search(session=session, query="Avatar")
        print("Search object created")
        
        results = await search.get_content_model()
        print("Search results fetched")
        
        # Inspect results
        # Assuming results has 'items' or similar
        print(f"Results type: {type(results)}")
        print(f"Results dir: {dir(results)}")
        
        if hasattr(results, 'items') and results.items:
            first_item = results.items[0]
            print(f"\nFirst Item: {first_item}")
            print(f"Item dir: {dir(first_item)}")
            
            # Get details
            print("\n--- GETTING DETAILS ---")
            details_provider = search.get_item_details(first_item)
            details = await details_provider.get_content_model()
            print(f"Details fetched: {details}")
            print(f"Details dir: {dir(details)}")
            
        else:
            print("No items found or 'items' attribute missing")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
