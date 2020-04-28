# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from dataclasses import dataclass
from datetime import datetime


NO_DEFAULT = object()


class CacheManager:
    def get(self, key, default=NO_DEFAULT):
        """Raises KeyError if not in cache."""
        pass

    def set(self, key, contents):
        pass

    def delete(self, key):
        pass


class CacheError(Exception):
    pass


@dataclass
class IndexItem:
    size: int
    lastused: datetime
    data: bytes


class MemoryCacheManager(CacheManager):
    def __init__(self, maxsizekb=1024):
        self.maxsize = maxsizekb * 1024

        # key -> IndexItem
        # NOTE(willkg): not thread safe
        self._cache = {}

    def _cache_size(self):
        return sum([item.size for item in self._cache.values()])

    def _oldest(self):
        items_by_age = sorted(
            [(item.lastused, key) for key, item in self._cache.items()]
        )
        return items_by_age[0][1]

    def _keys(self):
        # NOTE(willkg): self._cache is a dict, so the keys are in the order
        # they were added
        return list(self._cache.keys())

    def get(self, key, default=NO_DEFAULT):
        try:
            item = self._cache[key]
        except KeyError:
            if default != NO_DEFAULT:
                return default
            raise
        item.lastused = datetime.now()
        return item.data

    def set(self, key, data):
        data_len = len(data)
        if data_len > self.maxsize:
            raise CacheError("Data is larger than max size.")

        item = IndexItem(size=data_len, lastused=datetime.now(), data=data)
        self._cache[key] = item

        # Remove oldest items from cache until we're under max size again
        while self._cache_size() > self.maxsize:
            self.delete(self._oldest())

    def delete(self, key):
        del self._cache[key]
