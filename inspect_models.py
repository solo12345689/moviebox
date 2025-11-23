import sys
from moviebox_api.extractor.models.json import SubjectTrailerModel

def log(msg):
    with open("inspect_models.log", "a") as f:
        f.write(str(msg) + "\n")
    print(msg)

# Try to import SubjectModel
try:
    from moviebox_api.extractor.models.json import SubjectModel
    log(f"SubjectModel found: {SubjectModel}")
except ImportError:
    log("SubjectModel NOT found in moviebox_api.extractor.models.json")
    # Try to find it in _core or via traversal
    from moviebox_api.extractor._core import ItemJsonDetailsModel
    from typing import get_args, get_origin
    
    def unwrap(ann):
        if get_origin(ann) is list:
            return get_args(ann)[0]
        return ann
        
    if 'resData' in ItemJsonDetailsModel.model_fields:
        ResDataModel = unwrap(ItemJsonDetailsModel.model_fields['resData'].annotation)
        if hasattr(ResDataModel, 'model_fields') and 'subject' in ResDataModel.model_fields:
            SubjectModel = unwrap(ResDataModel.model_fields['subject'].annotation)
            log(f"SubjectModel found via traversal: {SubjectModel}")
            log(f"Module: {SubjectModel.__module__}")
