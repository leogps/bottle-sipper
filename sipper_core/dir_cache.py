import threading
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass, field
from os import stat_result
from typing import TypeVar, Generic, Optional

T = TypeVar("T")

class Node(ABC, Generic[T]):
    """Base for all filesystem entries."""

    def __init__(self) -> None:
        pass

    @abstractmethod
    def children(self) -> list[T]: ...

    @abstractmethod
    def has_children(self) -> bool: ...

    @abstractmethod
    def add_child(self, child: T) -> None: ...


class Dir(Node["Node"]):
    """Composite — can contain other Dir or File nodes."""

    def __init__(self,
                 path: str,
                 full_path: str,
                 stat: stat_result,
                 parent_path: str) -> None:
        super().__init__()

        self.path = path
        self.full_path = full_path
        self.stat = stat
        self.parent_path = parent_path
        self.etag_value = f'{int(stat.st_mtime)}-{stat.st_size}'
        self._children: list[Node] = []

    def children(self) -> list[Node]:
        return self._children

    def has_children(self) -> bool:
        return len(self._children) > 0

    def add_child(self, child: Node) -> None:
        self._children.append(child)


class File(Node[None]):
    """Leaf — no children, stores stat info."""

    def __init__(self, path: str,
                 full_path: str,
                 stat: stat_result,
                 parent_path: str,
                 mime_type: str) -> None:
        super().__init__()

        self.path = path
        self.full_path = full_path
        self.stat = stat
        self.parent_path = parent_path
        self.mime_type = mime_type
        self.etag_value = f'{int(stat.st_mtime)}-{stat.st_size}'

    def children(self) -> list[None]:
        return []

    def has_children(self) -> bool:
        return False

    def add_child(self, child: None) -> None:
        raise TypeError(f"Cannot add children to a File: {self.path}")


def _depth_sufficient(cached: int, needed: int) -> bool:
    """Return True if a cache entry at *cached* depth covers a request at *needed* depth.

    Depth semantics: -1 = infinity, 0 = stat only, 1 = stat + immediate children.
    A cached_depth >= 1 means the children list is available; callers recurse into
    each child directory via its own independent cache entry, so depth=1 is sufficient
    even for an infinity request at the parent level.
    """
    if cached == -1:
        return True
    if needed == -1:
        return cached >= 1
    return cached >= needed


@dataclass
class CacheEntry:
    """Single entry stored in DirCache."""
    node: Dir
    cached_depth: int
    cached_at: float = field(default_factory=time.time)


CLEANUP_INTERVAL = 60


class DirCache:
    """Thread-safe, TTL-based cache for directory metadata.

    Key   : normalised URL path (str), e.g. '/' or '/docs/api'
    Value : CacheEntry holding a Dir node (stat + immediate children)
              and the depth at which the subtree was explored.

    cached_depth semantics
    ----------------------
    0  – only the directory's own stat is stored (no children)
    1  – stat + immediate children (Dir/File nodes) are stored
    -1 – stat + all descendants are stored (infinity traversal)

    A cached entry with cached_depth >= 1 satisfies any depth request
    because child directories carry their own independent cache entries
    and are checked recursively during traversal.

    When enabled, a single daemon thread runs every CLEANUP_INTERVAL seconds
    to evict expired entries and reclaim memory.
    """

    def __init__(self, ttl: int = 0) -> None:
        self.ttl = ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._cleanup_thread: Optional[threading.Thread] = None
        if self.enabled:
            self._start_cleanup()

    @property
    def enabled(self) -> bool:
        return self.ttl > 0

    def get(self, path: str, needed_depth: int) -> Optional[CacheEntry]:
        """Return a valid CacheEntry or None on miss / expiry / insufficient depth."""
        if not self.enabled:
            return None
        with self._lock:
            entry = self._cache.get(path)
            if entry is None:
                return None
            if time.time() - entry.cached_at > self.ttl:
                del self._cache[path]
                return None
            if needed_depth == 0:
                return entry
            if entry.cached_depth >= 1 or entry.cached_depth == -1:
                return entry
            return None

    def put(self, path: str, node: Dir, depth: int) -> None:
        """Store or upgrade a cache entry for *path*.

        Always pops before inserting so that refreshed entries move to the tail
        of the OrderedDict, preserving chronological (oldest-first) order.
        """
        if not self.enabled:
            return
        with self._lock:
            existing = self._cache.get(path)
            if existing is not None and _depth_sufficient(existing.cached_depth, depth):
                return
            self._cache.pop(path, None)
            self._cache[path] = CacheEntry(node=node, cached_depth=depth, cached_at=time.time())

    def _start_cleanup(self) -> None:
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name='dir-cache-cleanup'
        )
        self._cleanup_thread.start()

    def _cleanup_loop(self) -> None:
        """Run until stopped, evicting expired entries every CLEANUP_INTERVAL seconds."""
        while not self._stop_event.wait(CLEANUP_INTERVAL):
            self._evict_expired()

    def _evict_expired(self) -> None:
        now = time.time()
        with self._lock:
            snapshot = list(self._cache.items())
        expired = []
        for path, entry in snapshot:
            if now - entry.cached_at > self.ttl:
                expired.append(path)
            else:
                break
        if expired:
            with self._lock:
                for path in expired:
                    entry = self._cache.get(path)
                    if entry is not None and now - entry.cached_at > self.ttl:
                        del self._cache[path]

    def stop(self) -> None:
        """Signal the cleanup thread to exit and wait for it to finish."""
        self._stop_event.set()
        if self._cleanup_thread is not None:
            self._cleanup_thread.join()

    def invalidate(self, path: str) -> None:
        """Remove a single entry from the cache."""
        with self._lock:
            self._cache.pop(path, None)

    def clear(self) -> None:
        """Evict all entries."""
        with self._lock:
            self._cache.clear()
