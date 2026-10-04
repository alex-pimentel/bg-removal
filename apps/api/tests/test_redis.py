import src.core.redis as redis_module


class _FakeRedis:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


async def test_get_redis_caches_and_close(monkeypatch) -> None:
    redis_module._redis = None
    fake = _FakeRedis()
    monkeypatch.setattr(redis_module.aioredis, "from_url", lambda *a, **k: fake)

    first = await redis_module.get_redis()
    second = await redis_module.get_redis()
    assert first is fake
    assert second is fake

    await redis_module.close_redis()
    assert fake.closed is True
    assert redis_module._redis is None


async def test_close_redis_noop_when_unset() -> None:
    redis_module._redis = None
    await redis_module.close_redis()
    assert redis_module._redis is None
