import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

try:
    from api import search
    print("Successfully imported search function")
    
    # Test the search function directly
    async def test_search():
        try:
            result = await search(query="inception", content_type="all")
            print(f"Search successful! Results: {len(result.get('results', []))}")
            return result
        except Exception as e:
            print(f"Search failed with error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # Run the test
    result = asyncio.run(test_search())
    if result:
        print(f"\nFirst few results:")
        for item in result.get('results', [])[:3]:
            print(f"  - {item.get('title')} ({item.get('year')})")
    
except ImportError as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
