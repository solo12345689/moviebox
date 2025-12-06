import asyncio
import httpx

async def test_server_access():
    # Test URL from the exploration (BEST quality)
    test_url = "https://valiw.hakunaymatata.com/resource/0bfd300e33c89d9b673dd13bb04ecac4.mp4?auth_key=1764068014-0-0-b633fd7a1d96c4328d3f189df6d55f12"
    
    print(f"Testing access to: {test_url[:80]}...")
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            # Try HEAD request first (faster)
            response = await client.head(test_url)
            print(f"HEAD Response: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("\n✅ SUCCESS! This server is accessible from cloud IPs!")
            else:
                print(f"\n❌ FAILED with status code: {response.status_code}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_server_access())
