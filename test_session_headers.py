import asyncio
from moviebox_api import Session

# Test if headers are being set correctly
session = Session()

print("Testing Session headers...")
print(f"Session type: {type(session)}")
print(f"Has _client: {hasattr(session, '_client')}")

if hasattr(session, '_client'):
    print(f"Client type: {type(session._client)}")
    print(f"Has headers: {hasattr(session._client, 'headers')}")
    
    if hasattr(session._client, 'headers'):
        print(f"\nCurrent headers:")
        for key, value in session._client.headers.items():
            print(f"  {key}: {value}")
