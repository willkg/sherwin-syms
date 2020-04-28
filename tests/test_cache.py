# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import time

import pytest

from sherwin_syms import cache


class TestMemoryCacheManager:
    def test_get_no_default(self):
        """Getting a key that doesn't exist with no default raises KeyError."""
        mcm = cache.MemoryCacheManager(maxsizekb=1)
        with pytest.raises(KeyError):
            mcm.get("key")

    def test_get_with_default(self):
        """Getting a key that doesn't exist, but with a default works."""
        mcm = cache.MemoryCacheManager(maxsizekb=1)
        assert mcm.get("key", default="default_value") == "default_value"

    def test_basic_set_and_get(self):
        """Setting a key works."""
        mcm = cache.MemoryCacheManager(maxsizekb=1)
        mcm.set("key", data=b"ou812")
        assert mcm.get("key") == b"ou812"

    def test_set_cacheerror(self):
        """Adding a value that exceeds the max cache size raises CacheError."""
        mcm = cache.MemoryCacheManager(maxsizekb=1)
        data = ("a" * 2000).encode("utf-8")

        with pytest.raises(cache.CacheError):
            mcm.set("key", data)

    def test_set_lru_culling(self):
        mcm = cache.MemoryCacheManager(maxsizekb=1)
        # Add 200 bytes in two old keys
        mcm.set("key1", data=("a" * 100).encode("utf-8"))
        mcm.set("key2", data=("a" * 100).encode("utf-8"))
        time.sleep(0.5)
        # Add 700 bytes
        mcm.set("key3", data=("a" * 700).encode("utf-8"))
        assert mcm._keys() == ["key1", "key2", "key3"]
        # Add 300 bytes which should remove key1 and key2
        mcm.set("key4", data=("a" * 300).encode("utf-8"))
        assert mcm._keys() == ["key3", "key4"]

    def test_delete(self):
        """Deleting keys works."""
        mcm = cache.MemoryCacheManager(maxsizekb=1)
        mcm.set("key", data=b"ou812")
        assert mcm.get("key") == b"ou812"

        mcm.delete("key")

        with pytest.raises(KeyError):
            mcm.get("key")
