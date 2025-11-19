from moviebox_api import Search, MovieAuto
import asyncio
import sys

# Redirect stdout to file to ensure we capture it
sys.stdout = open('api_test_output.txt', 'w')
sys.stderr = sys.stdout

async def main():
    print("--- INSPECTING SEARCH ---")
    try:
        print(help(Search))
    except Exception as e:
        print(f"Error inspecting Search: {e}")

    print("\n--- TESTING MOVIEAUTO ---")
    try:
        auto = MovieAuto()
        print(f"MovieAuto methods: {dir(auto)}")
    except Exception as e:
        print(f"Error with MovieAuto: {e}")

if __name__ == "__main__":
    asyncio.run(main())
