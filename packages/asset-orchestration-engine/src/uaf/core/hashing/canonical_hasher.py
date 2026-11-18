"""
CanonicalHasher provides deterministic, bit-exact structural hashing for UAF specifications and models.
UAF-81.0 Sections 15, 16.
Implements structural canonical serialization:
- Recursively sorts dictionary keys.
- Preserves exact list element order.
- Preserves exact string contents (no destructive whitespace stripping inside strings).
- Compact JSON representation with separators (',', ':') without external whitespace.
- Consistent float/number representation.
- Stable UTF-8 byte encoding.
"""

import json
import hashlib
import math
from typing import Any, Dict, List, Union


class CanonicalHasher:
    """
    Computes deterministic SHA-256 hashes over arbitrary Python structures,
    dataclasses, and dictionaries using canonical structural serialization.
    """

    @classmethod
    def normalize_structure(cls, data: Any) -> Any:
        """
        Recursively normalizes a data structure so it conforms to canonical JSON standards:
        - Dict keys are sorted.
        - Floats are standardized (rounding negative zero to positive zero).
        - Enums and custom objects with to_dict() are converted.
        - Sets and tuples are handled deterministically.
        - Strings retain their exact values.
        """
        if data is None:
            return None
        elif isinstance(data, (bool, int)):
            return data
        elif isinstance(data, float):
            if math.isnan(data) or math.isinf(data):
                raise ValueError("NaN and Infinity are not permitted in canonical hashing.")
            # Standardize -0.0 to 0.0
            if data == 0.0:
                return 0.0
            return data
        elif isinstance(data, str):
            return data
        elif hasattr(data, "to_dict") and callable(data.to_dict):
            return cls.normalize_structure(data.to_dict())
        elif hasattr(data, "value"):  # Enum
            return cls.normalize_structure(data.value)
        elif isinstance(data, dict):
            # Sort keys lexically
            return {
                str(k): cls.normalize_structure(v)
                for k, v in sorted(data.items(), key=lambda item: str(item[0]))
            }
        elif isinstance(data, (list, tuple)):
            # Retain order
            return [cls.normalize_structure(item) for item in data]
        elif isinstance(data, set):
            # Sets have no intrinsic order, so sort normalized string representation
            normalized_items = [cls.normalize_structure(item) for item in data]
            return sorted(normalized_items, key=lambda x: json.dumps(x, sort_keys=True))
        else:
            return str(data)

    @classmethod
    def to_canonical_json(cls, data: Any) -> str:
        """
        Produces a canonical JSON string:
        - Sorted keys
        - Separators (',', ':') without whitespace
        - UTF-8 compatible
        - Exact string contents preserved
        """
        normalized = cls.normalize_structure(data)
        return json.dumps(
            normalized,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )

    @classmethod
    def compute_hash(cls, data: Any) -> str:
        """
        Computes SHA-256 hex digest of the canonical JSON representation.
        """
        canonical_str = cls.to_canonical_json(data)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
