import pickle
import os
from pathlib import Path
from src.cache import cache
from src.utils import logger

def migrate_pkl_to_sqlite():
    print("🚀 STARTING CACHE MIGRATION: PKL -> SQLite")
    cache_dir = Path(".cache")
    if not cache_dir.exists():
        print("ℹ️ No .cache directory found. Skipping migration.")
        return

    pkl_files = list(cache_dir.glob("*.pkl"))
    if not pkl_files:
        print("ℹ️ No .pkl files found in .cache. Skipping migration.")
        return

    print(f"📦 Found {len(pkl_files)} pickle files to migrate.")
    
    count = 0
    for pkl_file in pkl_files:
        key = pkl_file.stem
        try:
            with open(pkl_file, 'rb') as f:
                data = pickle.load(f)
                cache.set(key, data)
                count += 1
                # Optional: pkl_file.unlink() # Delete after migration?
        except Exception as e:
            logger.error("Migration failed for file", file=str(pkl_file), error=str(e))

    print(f"✅ Successfully migrated {count} entries to SQLite.")
    print("⚠️ You may now safely delete the .cache directory.")

if __name__ == "__main__":
    migrate_pkl_to_sqlite()
