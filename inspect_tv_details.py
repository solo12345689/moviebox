import asyncio
import sys
from moviebox_api import Search, SubjectType
from moviebox_api.session import ClientSession
import json

async def inspect_tv_series():
    with open('inspection_result.txt', 'w') as f:
        def log(msg):
            print(msg)
            f.write(str(msg) + '\n')
            
        session = ClientSession()
        
        # Search for a TV series
        log("Searching for 'Breaking Bad'...")
        search = Search(session=session, query="Breaking Bad", subject_type=SubjectType.TV_SERIES)
        results = await search.get_content_model()
        
        if not results.items:
            log("No results found")
            return
        
        item = results.items[0]
        log(f"\nFound: {item.title}")
        log(f"Item type: {type(item)}")
        log(f"Item attributes: {[attr for attr in dir(item) if not attr.startswith('_')]}")
        
        # Get details
        log("\n--- Getting Details ---")
        details_provider = search.get_item_details(item)
        details_model = await details_provider.get_content_model()
        
        log(f"\nDetails Model Type: {type(details_model)}")
        log(f"Details Model attributes: {[attr for attr in dir(details_model) if not attr.startswith('_')]}")
        
        # Try to access dict/json representation
        try:
            if hasattr(details_model, 'dict'):
                details_dict = details_model.dict()
                log(f"\nDetails Dict Keys: {details_dict.keys()}")
                # log(f"\nFull Details Dict:")
                # log(json.dumps(details_dict, indent=2, default=str))
        except Exception as e:
            log(f"Error getting dict: {e}")
        
        # Check for resource attribute
        if hasattr(details_model, 'resource'):
            log(f"\n--- Resource Attribute ---")
            log(f"Resource type: {type(details_model.resource)}")
            log(f"Resource attributes: {[attr for attr in dir(details_model.resource) if not attr.startswith('_')]}")
            
            if hasattr(details_model.resource, 'seasons'):
                log(f"\nSeasons found: {len(details_model.resource.seasons)}")
                if len(details_model.resource.seasons) > 0:
                    season = details_model.resource.seasons[0]
                    log(f"First season type: {type(season)}")
                    log(f"First season attributes: {[attr for attr in dir(season) if not attr.startswith('_')]}")
                    
                    # Try to print season details
                    if hasattr(season, 'dict'):
                        log(f"First season dict: {season.dict()}")
                    else:
                        log(f"Season se: {getattr(season, 'se', 'N/A')}")
                        log(f"Season maxEp: {getattr(season, 'maxEp', 'N/A')}")
        
        # Check for seasons attribute directly
        if hasattr(details_model, 'seasons'):
            log(f"\n--- Direct Seasons Attribute ---")
            log(f"Seasons: {details_model.seasons}")

if __name__ == "__main__":
    asyncio.run(inspect_tv_series())
