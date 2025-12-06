from moviebox_api import Session, Search, SubjectType
from moviebox_api.download import DownloadableTVSeriesFilesDetail
import asyncio

async def check_language_info():
    session = Session()
    
    # Search for Naruto which has multiple languages
    search = Search(session=session, query="Naruto", subject_type=SubjectType.TV_SERIES)
    results = await search.get_content_model()
    
    if results.items:
        item = results.items[0]
        print(f"Found: {item.title}")
        print(f"\nItem attributes: {dir(item)}")
        
        # Get downloadable files to see if language info is there
        files_provider = DownloadableTVSeriesFilesDetail(session=session, item=item)
        files_metadata = await files_provider.get_content_model(season=1, episode=1)
        
        print(f"\nFiles metadata attributes: {dir(files_metadata)}")
        print(f"\nFiles metadata: {files_metadata}")
        
        if hasattr(files_metadata, 'files'):
            print(f"\nNumber of files: {len(files_metadata.files)}")
            for i, file in enumerate(files_metadata.files[:3]):  # Show first 3
                print(f"\nFile {i+1} attributes: {dir(file)}")
                print(f"File {i+1}: {file}")

asyncio.run(check_language_info())
