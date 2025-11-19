import moviebox_api
import inspect
import pkgutil
import sys

with open('api_info.txt', 'w') as f:
    sys.stdout = f
    print("Package contents:")
    if hasattr(moviebox_api, "__path__"):
        for importer, modname, ispkg in pkgutil.iter_modules(moviebox_api.__path__):
            print(f"Found submodule: {modname} (is_pkg={ispkg})")
    else:
        print("moviebox_api has no __path__")

    print("\nTop level attributes:")
    print(dir(moviebox_api))

    try:
        from moviebox_api import cli
        print("\nCLI module attributes:")
        print(dir(cli))
    except ImportError:
        print("\nCLI module not found directly")
