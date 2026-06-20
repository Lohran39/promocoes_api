from typing import Any

class SimpleCache:
    def __init__(self):
        self._store = {}

    def get(self, key: str) -> Any:
        return self._store.get(key)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear_pattern(self, pattern: str) -> None:
        prefix = pattern.replace("*", "")
        keys_to_delete = [k for k in self._store if k.startswith(prefix)]
        for k in keys_to_delete:
            del self._store[k]

cache = SimpleCache()
