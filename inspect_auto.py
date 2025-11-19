from moviebox_api import MovieAuto
import inspect

def inspect_movie_auto():
    print("Inspecting MovieAuto...")
    try:
        auto = MovieAuto()
        print("Attributes/Methods:")
        for name in dir(auto):
            if not name.startswith('_'):
                attr = getattr(auto, name)
                print(f"- {name}: {type(attr)}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_movie_auto()
