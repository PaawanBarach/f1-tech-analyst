import diskcache as dc

# A persistent on-disk cache
CACHE = dc.Cache("./.cache")

def get_cached_response(query: str):
    return CACHE.get(query)

def set_cached_response(query: str, response: str):
    CACHE.set(query, response, expire=None)  # never expires by default
