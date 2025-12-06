import asyncio
import sys
from moviebox_api import Session, Search, SubjectType
from moviebox_api.download import DownloadableTVSeriesFilesDetail, resolve_media_file_to_be_downloaded

async def explore_sources():
    session = Session()
    
    # Redirect output to file
    output_file = open("explore_sources_output.txt", "w", encoding="utf-8")
    sys.stdout = output_file
    sys.stderr = output_file
    
    try:
        # Search for Naruto
        search = Search(session=session, query="Naruto", subject_type=SubjectType.TV_SERIES)
        results = await search.get_content_model()
        
        if not results.items:
            print("No results found")
            return
        
        item = results.items[0]
        print(f"Found: {item.title}")
        print(f"Item ID: {getattr(item, 'id', getattr(item, 'subjectId', 'N/A'))}")
        
        # Get files for Season 1, Episode 1
        files_provider = DownloadableTVSeriesFilesDetail(session=session, item=item)
        files_metadata = await files_provider.get_content_model(season=1, episode=1)
        
        print(f"\n=== Available Files ===")
        print(f"Files metadata type: {type(files_metadata)}")
        
        # Check all attributes
        print(f"\nAttributes: {dir(files_metadata)}")
        
        # Check if files_metadata has multiple sources
        if hasattr(files_metadata, 'files'):
            print(f"\nNumber of files: {len(files_metadata.files)}")
            for i, file in enumerate(files_metadata.files):
                print(f"\nFile {i+1}:")
                print(f"  URL: {file.url}")
                print(f"  Attributes: {dir(file)}")
        elif hasattr(files_metadata, 'qualities'):
            print(f"\nQualities available: {files_metadata.qualities}")
        
        # Try different quality options
        print(f"\n=== Testing Quality Options ===")
        quality_options = ["BEST", "WORST", "720p", "480p", "360p", "1080p"]
        
        for quality in quality_options:
            try:
                media_file = resolve_media_file_to_be_downloaded(quality, files_metadata)
                if media_file:
                    print(f"\n{quality}:")
                    print(f"  URL: {media_file.url}")
                    print(f"  Attributes: {dir(media_file)}")
            except Exception as e:
                print(f"\n{quality}: Error - {e}")
    
    finally:
        output_file.close()

if __name__ == "__main__":
    asyncio.run(explore_sources())
