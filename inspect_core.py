from moviebox_api.extractor._core import ItemJsonDetailsModel
from typing import get_type_hints, get_args, get_origin
import sys

def log(msg):
    with open("inspect_core.log", "a") as f:
        f.write(str(msg) + "\n")
    print(msg)

log("Inspecting SubjectTrailerModel...")

def unwrap(ann):
    if get_origin(ann) is list:
        return get_args(ann)[0]
    return ann

try:
    if 'resData' in ItemJsonDetailsModel.model_fields:
        ResDataModel = unwrap(ItemJsonDetailsModel.model_fields['resData'].annotation)
        if hasattr(ResDataModel, 'model_fields') and 'subject' in ResDataModel.model_fields:
            SubjectModel = unwrap(ResDataModel.model_fields['subject'].annotation)
            if hasattr(SubjectModel, 'model_fields') and 'trailer' in SubjectModel.model_fields:
                TrailerModel = unwrap(SubjectModel.model_fields['trailer'].annotation)
                # It might be Union[dict, SubjectTrailerModel] or similar
                # Let's inspect it
                log(f"Trailer Annotation: {TrailerModel}")
                
                # Try to find the class
                if get_origin(TrailerModel) is Union:
                    for arg in get_args(TrailerModel):
                        if hasattr(arg, 'model_fields'):
                            TrailerModel = arg
                            break
                
                log(f"TrailerModel: {TrailerModel}")
                if hasattr(TrailerModel, 'model_fields'):
                    log("Fields:")
                    for name, field in TrailerModel.model_fields.items():
                        log(f"  {name}: {field.annotation} (Required: {field.required})")
                else:
                    log("TrailerModel has no model_fields")

except Exception as e:
    log(f"Error: {e}")
