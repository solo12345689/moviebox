def log(msg):
    with open('import_detailed_log.txt', 'a') as f:
        f.write(str(msg) + '\n')

try:
    with open('import_detailed_log.txt', 'w') as f:
        f.write("Starting imports...\n")
    
    log("Importing asyncio")
    import asyncio
    
    log("Importing moviebox_api.api")
    from moviebox_api.api import Search, DownloadableTVSeriesFilesDetail
    
    log("Importing moviebox_api.utils")
    from moviebox_api.utils import resolve_media_file_to_be_downloaded
    
    log("Importing moviebox_api.models")
    from moviebox_api.models import SubjectType
    
    log("Importing moviebox_api.session")
    from moviebox_api.session import Session
    
    log("All imports successful")

except Exception as e:
    log(f"Import failed: {e}")
    import traceback
    log(traceback.format_exc())
