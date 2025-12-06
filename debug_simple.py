
import sys

with open("debug_output.txt", "w") as f:
    f.write("Starting script...\n")
    try:
        import moviebox
        f.write(f"Successfully imported moviebox: {moviebox}\n")
    except ImportError as e:
        f.write(f"Failed to import moviebox: {e}\n")
    except Exception as e:
        f.write(f"Unexpected error: {e}\n")
    f.write("Script finished.\n")
