# Rely on appdirs to set up a cache for the poked app
#
# The cache is stored in the user's cache directory, which is
# platform-specific.  On Linux, it's in ~/.cache/poked.
#
# The cache is a directory containing a file for each query, named
# after the query's hash.  The file contains the query's result, in
# JSON format.

import hashlib
import json
import os

import appdirs

CACHE_DIR = "poked"


def get_cache_filename(query):
    """Return the filename for the given query in the cache directory"""
    # Hash the query to get a unique filename
    hash = hashlib.sha256(query.encode("utf-8")).hexdigest()
    return os.path.join(appdirs.user_cache_dir(CACHE_DIR), hash)


def get_cached_query(query):
    """Return the cached result for the given query, or None if not cached"""
    filename = get_cache_filename(query)
    if not os.path.exists(filename):
        return None

    with open(filename, "r") as f:
        # Attempt to load the JSON and return it.
        # If it fails, we must clear it from the cache.
        try:
            return json.load(f)
        except json.decoder.JSONDecodeError:
            os.remove(filename)
            return None


def cache_query(query, result):
    """Cache the result for the given query"""
    filename = get_cache_filename(query)
    os.makedirs(appdirs.user_cache_dir(CACHE_DIR), exist_ok=True)
    with open(filename, "w") as f:
        json.dump(result, f)


def clear_cache(query=None):
    """Clear the cache, or just the given query if specified"""
    if query is None:
        os.remove(appdirs.user_cache_dir(CACHE_DIR))
    else:
        filename = get_cache_filename(query)
        if os.path.exists(filename):
            os.remove(filename)
