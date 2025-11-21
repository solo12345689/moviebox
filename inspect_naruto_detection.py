import asyncio
from moviebox_api import Session, Search, SubjectType

def log(msg):
    print(msg)
    with open('naruto_detection_log.txt', 'a', encoding='utf-8') as f:
        f.write(str(msg) + '\n')

async def inspect_item():
    with open('naruto_detection_log.txt', 'w', encoding='utf-8') as f:
        f.write("Starting inspection...\n")

    session = Session()
    query = "Naruto: Shippuden [Hindi] S1-S15"
    log(f"Searching for: {query}")
    
    # Try searching as ALL first to see what we get naturally
    search = Search(session=session, query=query)
    results = await search.get_content_model()
    
    if not results.items:
        log("No results found")
        return

    # Find the specific item
    target_item = None
    for item in results.items:
        if "Naruto: Shippuden" in item.title:
            target_item = item
            break
            
    if not target_item:
        log("Target item not found in results")
        # Print top 3 for context
        for i, item in enumerate(results.items[:3]):
            log(f"{i}: {item.title} (Type: {type(item)})")
        return

    log(f"\nSelected: {target_item.title}")
    log(f"Raw Item Data: {target_item.dict()}")
    
    # Check specific attributes used for detection
    log(f"\nDetection Attributes:")
    log(f"is_tv_series: {getattr(target_item, 'is_tv_series', 'N/A')}")
    log(f"category: {getattr(target_item, 'category', 'N/A')}")
    log(f"subjectId: {getattr(target_item, 'subjectId', 'N/A')}")
    log(f"id: {getattr(target_item, 'id', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(inspect_item())
