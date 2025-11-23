from moviebox_api.extractor._core import ItemJsonDetailsModel
from moviebox_api.extractor.models.json import SubjectModel, SubjectTrailerModel
from typing import Optional, Union, get_args, get_origin
import pydantic

def log(msg):
    with open("debug_patch.log", "a") as f:
        f.write(str(msg) + "\n")
    print(msg)

def unwrap_annotation(annotation):
    origin = get_origin(annotation)
    if origin is Union:
        args = get_args(annotation)
        for arg in args:
            if isinstance(arg, type) and arg is not type(None):
                return arg
    return annotation

def check_trailer_field():
    if hasattr(SubjectModel, 'model_fields') and 'trailer' in SubjectModel.model_fields:
        field = SubjectModel.model_fields['trailer']
        log(f"Current Trailer Annotation: {field.annotation}")
        # log(f"Current Trailer Required: {field.required}") # This crashed
        log(f"FieldInfo dir: {dir(field)}")
    else:
        log("Trailer field not found!")

def patch_moviebox_models():
    try:
        log("Applying patch...")
        if hasattr(SubjectModel, 'model_fields') and 'trailer' in SubjectModel.model_fields:
            # Allow None for trailer
            SubjectModel.model_fields['trailer'].annotation = Optional[Union[dict, SubjectTrailerModel]]
            SubjectModel.model_fields['trailer'].required = False
            SubjectModel.model_fields['trailer'].default = None
            
            if hasattr(SubjectModel, 'model_rebuild'):
                SubjectModel.model_rebuild(force=True)
            
            # Rebuild parents
            if 'resData' in ItemJsonDetailsModel.model_fields:
                ResDataModel = unwrap_annotation(ItemJsonDetailsModel.model_fields['resData'].annotation)
                if hasattr(ResDataModel, 'model_rebuild'):
                    ResDataModel.model_rebuild(force=True)
            
            if hasattr(ItemJsonDetailsModel, 'model_rebuild'):
                ItemJsonDetailsModel.model_rebuild(force=True)
                
            log("Patch applied.")
    except Exception as e:
        log(f"Failed to patch models: {e}")

log("--- Before Patch ---")
check_trailer_field()

patch_moviebox_models()

log("--- After Patch ---")
check_trailer_field()

# Test Validation
log("--- Testing Validation ---")
try:
    # Create a dummy SubjectModel with None trailer
    # We need to populate other required fields to test strictly 'trailer'
    # But let's just try to instantiate SubjectModel directly if possible
    
    # We don't know all required fields, so let's just see if the annotation changed
    pass
except Exception as e:
    log(f"Validation test failed: {e}")
