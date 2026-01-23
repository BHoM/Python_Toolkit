import hashlib
import json
from typing import Any, Union
import enum

def deep_sort_dict(obj: dict[Any, Any], sort_lists: bool = True) -> Any:
    """Recursively sort nested dictionaries and lists for consistent ordering."""
    if isinstance(obj, dict):
        return {
            k: deep_sort_dict(v, sort_lists=sort_lists) for k, v in sorted(obj.items())
        }
    elif sort_lists and isinstance(obj, (list, tuple)):
        processed = [deep_sort_dict(x, sort_lists=sort_lists) for x in obj]
        if isinstance(obj, tuple):
            return tuple(
                sorted(
                    processed,
                    key=lambda x: json.dumps(x, sort_keys=True),
                )
            )
        else:
            return sorted(
                processed,
                key=lambda x: json.dumps(x, sort_keys=True),
            )
    else:
        return obj

def deterministic_hash(*values: Any, length: int = 16, algorithm: str = "md5", sort_lists: bool = True) -> int:
    """Create a deterministic hash from one or more values.

    This function produces consistent hash values across Python sessions,
    unlike the built-in hash() function which uses random salting.

    Args:
        *values (Any):
            One or more values to hash. Will be converted to strings and
            concatenated before hashing.
        length (int, optional):
            Number of hexadecimal characters to use from the hash.
            Defaults to 16 (64 bits).
        algorithm (str, optional):
            Hash algorithm to use. Must be supported by hashlib.
            Common options: 'md5', 'sha1', 'sha256', 'sha512'.
            Defaults to 'md5'.
        sort_lists (bool, optional):
            Whether to sort lists and dictionaries recursively before hashing,
            to ensure consistent ordering. Defaults to True.

    Returns:
        int:
            An integer hash value derived from the input values.

    Raises:
        ValueError:
            If the algorithm is not supported by hashlib.

    Example:
        >>> deterministic_hash("hello", "world", 123)
        123456789012345678
        >>> deterministic_hash("hello", "world", 123)  # same result in new session
        123456789012345678
        >>> deterministic_hash("test", length=8)
        12345678

    """

    # validate algorithm
    if algorithm not in hashlib.algorithms_available:
        raise ValueError(
            f"Hash algorithm '{algorithm}' not supported. "
            f"Available: {sorted(hashlib.algorithms_available)}"
        )

    # canonicalize each value
    canonicalized = []
    for v in values:
        if isinstance(v, (dict, list)):
            v = deep_sort_dict(v, sort_lists=sort_lists)
            v = json.dumps(v, sort_keys=True)
        canonicalized.append(str(v))

    concatenated = "".join(canonicalized)
    hasher = hashlib.new(algorithm)
    hasher.update(concatenated.encode("utf-8"))
    hex_digest = hasher.hexdigest()[:length]
    return int(hex_digest, 16)