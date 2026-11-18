"""
Tests for CanonicalHasher.
Verifies structural canonical serialization, dict order invariance, string whitespace preservation,
and list order preservation.
UAF-81.0 Sections 15, 16.
"""

import pytest
from uaf.core.hashing.canonical_hasher import CanonicalHasher


def test_dict_key_ordering_invariance():
    obj1 = {"alpha": 1, "beta": 2, "gamma": {"inner_b": 10, "inner_a": 20}}
    obj2 = {"gamma": {"inner_a": 20, "inner_b": 10}, "beta": 2, "alpha": 1}

    hash1 = CanonicalHasher.compute_hash(obj1)
    hash2 = CanonicalHasher.compute_hash(obj2)

    assert hash1 == hash2


def test_string_whitespace_preservation_different_hash():
    """
    CRITICAL INVARIANT: Exact string contents are preserved.
    Whitespace inside or surrounding strings must NOT be destructively stripped.
    """
    obj1 = {"name": "Asset"}
    obj2 = {"name": " Asset "}
    obj3 = {"name": "Asset "}

    hash1 = CanonicalHasher.compute_hash(obj1)
    hash2 = CanonicalHasher.compute_hash(obj2)
    hash3 = CanonicalHasher.compute_hash(obj3)

    assert hash1 != hash2
    assert hash2 != hash3
    assert hash1 != hash3


def test_list_order_preservation():
    """Lists represent ordered sequences and must retain exact item order."""
    list1 = {"items": [1, 2, 3]}
    list2 = {"items": [3, 2, 1]}

    hash1 = CanonicalHasher.compute_hash(list1)
    hash2 = CanonicalHasher.compute_hash(list2)

    assert hash1 != hash2


def test_negative_zero_standardization():
    obj1 = {"coord": 0.0}
    obj2 = {"coord": -0.0}

    assert CanonicalHasher.compute_hash(obj1) == CanonicalHasher.compute_hash(obj2)


def test_nan_infinity_rejected():
    with pytest.raises(ValueError, match="NaN and Infinity"):
        CanonicalHasher.compute_hash({"val": float("nan")})

    with pytest.raises(ValueError, match="NaN and Infinity"):
        CanonicalHasher.compute_hash({"val": float("inf")})


def test_canonical_json_compactness():
    obj = {"b": 2, "a": 1}
    canonical_json = CanonicalHasher.to_canonical_json(obj)

    # No spaces between keys or colons
    assert canonical_json == '{"a":1,"b":2}'
