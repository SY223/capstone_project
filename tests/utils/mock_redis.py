import pytest
import app.core.cache as cache_module

class MockRedis:
    async def get(self, key):
        return None

    async def set(self, key, value, ex=None):
        return True

    async def delete(self, *keys):
        return 1

    async def keys(self, pattern):
        return []

mock_redis = MockRedis()
