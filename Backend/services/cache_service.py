import json
import redis

from config.settings import settings

# --------------------------------------------------
# Redis Client
# --------------------------------------------------

redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)

DEFAULT_TTL_SECONDS = 240

try:
    print(f"[REDIS] PING: {redis_client.ping()}")
    print(f"[REDIS] VERSION: {redis_client.info()['redis_version']}")
except Exception as e:
    print(f"[REDIS ERROR] Connection failed: {e}")


# --------------------------------------------------
# Keys
# --------------------------------------------------

def _events_key(user_id: str) -> str:
    return f"calendar:events:{user_id}"


# --------------------------------------------------
# Read Cache
# --------------------------------------------------

def get_cached_events(user_id: str):
    """
    Returns cached events or None on cache miss.
    """

    try:
        key = _events_key(user_id)
        raw = redis_client.get(key)

        if raw is None:
            print(f"[REDIS MISS] key={key}")
            return None

        print(f"[REDIS HIT] key={key}")

        return json.loads(raw)

    except Exception as e:
        print(f"[REDIS ERROR] get failed: {e}")
        return None


# --------------------------------------------------
# Write Cache
# --------------------------------------------------

def set_cached_events(
    user_id: str,
    events: list,
    ttl: int = DEFAULT_TTL_SECONDS
):
    """
    Store events in Redis.
    """

    try:
        key = _events_key(user_id)

        redis_client.set(
            key,
            json.dumps(events),
            ex=ttl
        )

        print(
            f"[REDIS SET] key={key} "
            f"events={len(events)} "
            f"ttl={ttl}s"
        )

    except Exception as e:
        print(f"[REDIS ERROR] set failed: {e}")


# --------------------------------------------------
# Delete Cache
# --------------------------------------------------

def invalidate_events_cache(user_id: str):
    """
    Remove cached events.
    """

    try:
        key = _events_key(user_id)

        deleted = redis_client.delete(key)

        print(
            f"[REDIS INVALIDATE] key={key} "
            f"deleted={deleted}"
        )

    except Exception as e:
        print(f"[REDIS ERROR] invalidate failed: {e}")


# --------------------------------------------------
# Force Refresh
# --------------------------------------------------

def refresh_events_cache(db, user_id: str):
    """
    Refetch from Google and repopulate cache.
    """

    from services.calendar_service import fetch_events_live

    invalidate_events_cache(user_id)

    try:
        print(
            f"[REDIS REFRESH] Fetching fresh events "
            f"for user={user_id}"
        )

        fresh_events = fetch_events_live(
            db=db,
            user_id=user_id
        )

        set_cached_events(
            user_id=user_id,
            events=fresh_events
        )

        print(
            f"[REDIS REFRESH SUCCESS] "
            f"events={len(fresh_events)}"
        )

        return fresh_events

    except Exception as e:
        print(f"[REDIS ERROR] refresh fetch failed: {e}")
        return None