import os
import shutil

def clear_cache():
    for root, dirs, files in os.walk('.'):
        for d in dirs:
            if d == '__pycache__':
                path = os.path.join(root, d)
                print(f"Removing: {path}")
                shutil.rmtree(path)

if __name__ == "__main__":
    clear_cache()