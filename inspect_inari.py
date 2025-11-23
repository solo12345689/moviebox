from moviebox_api import Session, Search, SubjectType
import asyncio
import sys
import json

def log(msg):
    with open("inspect_inari.log", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

async def inspect():
    try:
        session = Session()
        query = "Inari Kon Kon Koi Iroha"
        log(f"Searching for: {query}")
        
        search = Search(session=session, query=query)
        results = await search.get_content_model()
        
        if results.items:
            item = results.items[0]
            log(f"\nTitle: {item.title}")
            log(f"SubjectType: {item.subjectType}")
            
            # Get details
            details_provider = search.get_item_details(item)
            details = await details_provider.get_content_model()
            
            log("\n--- Details Structure ---")
            # Dump relevant parts of details to see where seasons might be
            if hasattr(details, 'dict'):
                d = details.dict()
                # Prune large fields for log readability if needed, but for now dump keys
                log(f"Top level keys: {list(d.keys())}")
                
                if 'resData' in d:
                    log(f"resData keys: {list(d['resData'].keys())}")
                    if 'resource' in d['resData']:
                        res = d['resData']['resource']
                        if isinstance(res, dict):
                            log(f"resData.resource keys: {list(res.keys())}")
                            if 'seasons' in res:
                                log(f"Seasons found in resData.resource: {res['seasons']}")
                            else:
                                log("No seasons in resData.resource")
                        else:
                            log(f"resData.resource is type: {type(res)}")
                
                if 'seasons' in d:
                    log(f"Seasons found in root: {d['seasons']}")
            
            # Also check raw attributes of details object
            if hasattr(details, 'seasons'):
                log(f"details.seasons: {details.seasons}")
            
            if hasattr(details, 'resData'):
                if hasattr(details.resData, 'resource'):
                    if hasattr(details.resData.resource, 'seasons'):
                        log(f"details.resData.resource.seasons: {details.resData.resource.seasons}")

        else:
            log("No results found.")
    except Exception as e:
        log(f"Error: {e}")
        import traceback
        log(traceback.format_exc())

if __name__ == "__main__":
    # Clear log
    with open("inspect_inari.log", "w") as f:
        f.write("")
    asyncio.run(inspect())
