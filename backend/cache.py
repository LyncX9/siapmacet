import time
import redis

try:
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    r.ping()
except:
    r = None

_memory_cache = {}

def get_cache(key):
    if r:
        return r.get(key)
    v = _memory_cache.get(key)
    if not v:
        return None
    value, exp = v
    if time.time() > exp:
        del _memory_cache[key]
        return None
    return value

def set_cache(key, value, ttl=60):
    if r:
        r.setex(key, ttl, value)
    else:
        _memory_cache[key] = (value, time.time() + ttl)
