import json
import redis

from config.settings import settings

# Single shared Redis client for the app.
# decode_responses=True so we get str back instead of bytes.
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)

DEFAULT_TTL_SECONDS = 240  
print("PING:", redis_client.ping())
print("VERSION:", redis_client.info()["redis_version"])

def _events_key(user_id: str) -> str:
    return f"calendar:events:{user_id}"


def get_cached_events(user_id: str):
    """
    Returns cached raw Google event list for this user, or None on
    cache miss / Redis being unreachable. Never raises — cache is
    best-effort, callers should always have a live-fetch fallback.
    """
    try:
        raw = redis_client.get(_events_key(user_id))
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as e:
        print(f"[cache] get failed, falling back to live fetch: {e}")
        return None


def set_cached_events(user_id: str, events: list, ttl: int = DEFAULT_TTL_SECONDS):
    """
    Store the raw Google event list for this user. Best-effort —
    failures are logged and swallowed so a Redis outage never breaks
    the actual calendar operation.
    """
    try:
        redis_client.set(
            _events_key(user_id),
            json.dumps(events),
            ex=ttl
        )
    except Exception as e:
        print(f"[cache] set failed, continuing without cache: {e}")


def invalidate_events_cache(user_id: str):
    """
    Drop the cached event list for this user. Called before a
    refresh (create/reschedule/delete) so stale data never lingers
    even for the split second before the fresh fetch completes.
    """
    try:
        redis_client.delete(_events_key(user_id))
    except Exception as e:
        print(f"[cache] invalidate failed: {e}")


def refresh_events_cache(db, user_id: str):
    """
    Force a fresh fetch from Google Calendar and repopulate the
    cache. Call this right after create/reschedule/delete succeeds,
    so the NEXT read (validator step, frontend poll, next chat turn)
    gets fresh data without hitting Google again itself.

    Imported lazily to avoid a circular import with calendar_service.
    """
    from services.calendar_service import fetch_events_live

    invalidate_events_cache(user_id)

    try:
        fresh_events = fetch_events_live(db=db, user_id=user_id)
        set_cached_events(user_id, fresh_events)
        return fresh_events
    except Exception as e:
        # Live refetch failed (e.g. transient Google API error) —
        # cache stays empty, next get_events() call will retry live.
        print(f"[cache] refresh fetch failed: {e}")
        return None