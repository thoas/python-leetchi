from .api import LeetchiAPI, APIError

version = (0, 2, 1)

__version__ = '.'.join(map(str, version))

__all__ = [LeetchiAPI, APIError]
