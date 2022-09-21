import asyncio

import pytest

from acache import alru_cache, attl_cache

counter = 0


@pytest.fixture
def reset_counter():
    global counter

    counter = 0


@pytest.mark.asyncio
async def test_okay_alru_cache_base(reset_counter):
    @alru_cache(2)
    async def cached(a):
        global counter

        counter += 1

        return counter

    # first time
    assert 1 == (await cached(0))
    # jupp it's cached
    assert 1 == (await cached(0))
    # new obj
    assert 2 == (await cached(1))
    # jupp it's cached
    assert 2 == (await cached(1))
    # yo still cached
    assert 1 == (await cached(0))
    # should kick out 1
    assert 3 == (await cached(2))
    # jupp kicked out
    assert 4 == (await cached(1))
    # jupp kicked out
    assert 5 == (await cached(0))


@pytest.mark.asyncio
async def test_okay_alru_cache_with_class(reset_counter):
    @alru_cache(2)
    async def cached(a):
        global counter

        counter += 1

        return counter

    class A:
        pass

    a = A()
    assert 1 == (await cached(a))
    assert 1 == (await cached(a))
    assert 1 == (await cached(A()))


@pytest.mark.asyncio
async def test_okay_alru_cache_with_make_key(reset_counter):
    @alru_cache(2, make_key=lambda x: type(x))
    async def cached(a):
        global counter

        counter += 1

        return counter

    class A:
        pass

    class B:
        pass

    assert 1 == (await cached(A()))
    assert 1 == (await cached(A()))
    assert 2 == (await cached(B()))
    assert 2 == (await cached(B()))


@pytest.mark.asyncio
async def test_okay_alru_cache_locks(reset_counter):
    @alru_cache(2)
    async def cache(a):
        global counter

        counter += 1
        await asyncio.sleep(0.1)

        return counter

    assert [1, 1, 1, 1] == (
        await asyncio.gather(cache(0), cache(0), cache(0), cache(0))
    )


@pytest.mark.asyncio
async def test_okay_attl_cache_base(reset_counter):
    @attl_cache(seconds=0.1)
    async def cache(a):
        global counter

        counter += 1

        return counter

    assert [1, 2, 3] == (await asyncio.gather(cache(0), cache(1), cache(2)))
    assert [1, 2, 3] == (await asyncio.gather(cache(0), cache(1), cache(2)))

    await asyncio.sleep(0.1)

    assert [4, 5, 6] == (await asyncio.gather(cache(0), cache(1), cache(2)))
    assert [4, 5, 6] == (await asyncio.gather(cache(0), cache(1), cache(2)))


@pytest.mark.asyncio
async def test_okay_attl_cache_locks(reset_counter):
    @attl_cache(seconds=0.1)
    async def cache(a):
        global counter

        counter += 1

        return counter

    assert [1, 1, 1] == (await asyncio.gather(cache(0), cache(0), cache(0)))

    await asyncio.sleep(0.1)

    assert [2, 2, 2] == (await asyncio.gather(cache(0), cache(0), cache(0)))
