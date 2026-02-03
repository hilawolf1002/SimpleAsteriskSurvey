import os
import errno
import fcntl
from typing import Optional


class CallIdTracker:
    """
    Monotonic call-id generator backed by a text file.

    - Stores the *last issued id* in `path` as plain text (e.g. "42\n")
    - get_next() returns 1,2,3,... forever
    - Safe for multi-process concurrency via POSIX file locking (Linux/Unix)
    """

    def __init__(self, path: str = "data/call_id_track"):
        self.path = path
        self._ensure_parent_dir()

    def _ensure_parent_dir(self) -> None:
        parent = os.path.dirname(self.path) or "."
        os.makedirs(parent, exist_ok=True)

    def _read_int(self, fd: int) -> int:
        os.lseek(fd, 0, os.SEEK_SET)
        data = os.read(fd, 64).decode("utf-8", errors="ignore").strip()
        if not data:
            return 0
        try:
            n = int(data)
        except ValueError:
            # If file got corrupted, fail loudly rather than silently reusing IDs
            raise ValueError(f"Invalid call_id_track content: {data!r}")
        if n < 0:
            raise ValueError(f"Invalid call_id_track value (negative): {n}")
        return n

    def _write_int_atomic(self, fd: int, value: int) -> None:
        # Truncate + write + fsync while holding lock
        os.lseek(fd, 0, os.SEEK_SET)
        os.ftruncate(fd, 0)
        os.write(fd, f"{value}\n".encode("utf-8"))
        os.fsync(fd)

    def get_next(self) -> int:
        """
        Returns next integer ID. Uses an exclusive lock so multiple processes
        never produce the same ID.
        """
        # Open (create if missing) with read/write
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            # Exclusive lock (blocks until acquired)
            fcntl.flock(fd, fcntl.LOCK_EX)

            current = self._read_int(fd)
            nxt = current + 1

            self._write_int_atomic(fd, nxt)
            return nxt

        finally:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)

    def peek_last(self) -> int:
        """
        Returns the last issued ID (0 if none yet). Locked read.
        """
        fd = os.open(self.path, os.O_RDONLY | os.O_CREAT, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_SH)
            return self._read_int(fd)
        finally:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)

    def reset(self, value: int = 0) -> None:
        """
        Sets the stored last-issued ID to `value` (default 0).
        Locked write.
        """
        if value < 0:
            raise ValueError("value must be >= 0")

        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            self._write_int_atomic(fd, value)
        finally:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)


# Example usage:
# tracker = CallIdTracker("data/call_id_track")
# call_id = tracker.get_next()   # 1, 2, 3, ...
