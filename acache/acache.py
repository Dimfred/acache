import asyncio
import datetime as dt
from collections import OrderedDict
from functools import wraps

from . import utils


def alru_cache(maxsize=32, make_key=None):
    cache = OrderedDict()
    if make_key is None:
        make_key = utils.make_key

    def deco(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            key = make_key(*args, **kwargs)

            if key not in cache:
                if len(cache) == maxsize:
                    del cache[next(iter(cache))]

                lock = asyncio.Lock()
                cache[key] = [lock, None]

                async with lock:
                    val = await f(*args, **kwargs)
                    cache[key] = [lock, val]
                    return val
            else:
                lock, val = cache[key]
                async with lock:
                    return cache[key][1]

        return wrapper

    return deco


def atime_cache(
    weeks=0,
    days=0,
    hours=0,
    minutes=0,
    seconds=0,
    milliseconds=0,
    microseconds=0,
    timedelta=None,
    make_key=None,
):
    cache = {}
    if make_key is None:
        make_key = utils.make_key

    if timedelta is not None:
        refresh_after = timedelta
    else:
        refresh_after = dt.timedelta(
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds,
            microseconds=microseconds,
        )

    def deco(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            key = make_key(*args, **kwargs)
            if key not in cache:
                cache[key] = (
                    asyncio.Lock(),
                    dt.datetime(year=1970, month=1, day=1),
                    None,
                )

            lock, time, val = cache[key]
            async with lock:
                time_passed = dt.datetime.now() - time
                if time_passed > refresh_after:
                    val = await f(*args, **kwargs)
                    cache[key] = lock, dt.datetime.now(), val

            return val

        return wrapper

    return deco
