from .api import LeetchiAPI, APIError

version = (0, 2)

__version__ = '.'.join(map(str, version))

__all__ = [LeetchiAPI, APIError]
