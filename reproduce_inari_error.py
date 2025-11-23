from moviebox_api import Session, Search
from moviebox_api.extractor._core import ItemJsonDetailsModel, SubjectTrailerModel
from typing import Optional, Union, get_args, get_origin
import asyncio
import pydantic
from pydantic.fields import FieldInfo
import sys

def log(msg):
    with open("reproduce_patch.log", "a") as f:
        f.write(str(msg) + "\n")
    print(msg)

def unwrap_annotation(annotation):
    # Unwrap Optional/Union to find the class
    origin = get_origin(annotation)
    if origin is Union:
        args = get_args(annotation)
        for arg in args:
            if isinstance(arg, type) and arg is not type(None):
                return arg
    return annotation

def patch_model():
    log("Attempting to patch models...")
    try:
        # 1. Get ResDataModel
        if 'resData' in ItemJsonDetailsModel.model_fields:
            ResDataModel = unwrap_annotation(ItemJsonDetailsModel.model_fields['resData'].annotation)
            log(f"Found ResDataModel: {ResDataModel}")
            
            # 2. Get SubjectModel from ResDataModel
            if hasattr(ResDataModel, 'model_fields') and 'subject' in ResDataModel.model_fields:
                SubjectModel = unwrap_annotation(ResDataModel.model_fields['subject'].annotation)
                log(f"Found SubjectModel: {SubjectModel}")
                
                # 3. Patch trailer in SubjectModel
                if hasattr(SubjectModel, 'model_fields') and 'trailer' in SubjectModel.model_fields:
                    log("Found trailer field in SubjectModel. Patching...")
                    # Allow None
                    SubjectModel.model_fields['trailer'].annotation = Optional[Union[dict, SubjectTrailerModel]]
                    SubjectModel.model_fields['trailer'].required = False
                    SubjectModel.model_fields['trailer'].default = None
                    
                    # Rebuild model if necessary (Pydantic v2 might need this)
                    if hasattr(SubjectModel, 'model_rebuild'):
                        SubjectModel.model_rebuild(force=True)
                    log("Patch applied successfully!")
                    return True
                else:
                    log("trailer field NOT found in SubjectModel")
            else:
                log("subject field NOT found in ResDataModel")
        else:
            log("resData field NOT found in ItemJsonDetailsModel")
            
    except Exception as e:
        log(f"Patch failed: {e}")
        import traceback
        log(traceback.format_exc())
    return False

async def reproduce():
    # Clear log
    with open("reproduce_patch.log", "w") as f:
        f.write("")
        
    patch_model()
    
    try:
        session = Session()
        query = "Inari Kon Kon Koi Iroha"
        log(f"Searching for: {query}")
        
        search = Search(session=session, query=query)
        results = await search.get_content_model()
        
        if results.items:
            item = results.items[0]
            log(f"Found item: {item.title}")
            
            log("Getting details...")
            details_provider = search.get_item_details(item)
            details = await details_provider.get_content_model()
            log("Successfully got details!")
            
            # Try to extract seasons
            seasons = []
            if hasattr(details, 'resData') and hasattr(details.resData, 'resource') and hasattr(details.resData.resource, 'seasons'):
                seasons = details.resData.resource.seasons
            log(f"Seasons found: {len(seasons) if seasons else 0}")
            
        else:
            log("No results found.")
            
    except Exception as e:
        log(f"Caught error: {e}")
        import traceback
        log(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(reproduce())
