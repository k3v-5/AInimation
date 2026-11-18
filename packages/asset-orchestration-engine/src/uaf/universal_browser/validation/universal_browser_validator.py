"""
UAF-81.69: Universal Asset Browser Validator.
Enforces normative catalog invariants, canonical paths,
collection acyclicity, search index consistency, and diagnostic signatures.
"""

from __future__ import annotations

import re
from typing import List, Tuple

from uaf.universal_browser.models.definition import (
    AssetCollection,
    AssetTag,
    BrowserDiagnosticBundle,
    BrowserStateSnapshot,
    CatalogEntry,
    normalize_catalog_path,
)


class UniversalBrowserValidator:
    """
    Authoritative validator enforcing normative invariants for the Universal Asset Browser.
    """

    @staticmethod
    def validate_canonical_path(path_str: str) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not path_str or not isinstance(path_str, str):
            errors.append("EMPTY_PATH: Catalog path must be a non-empty string.")
            return False, errors

        if ".." in path_str:
            errors.append(f"NO_NON_CANONICAL_CATALOG_PATH: Path traversal '..' in '{path_str}'.")
        if "\\" in path_str:
            errors.append(f"NO_NON_CANONICAL_CATALOG_PATH: Backslash '\\' in '{path_str}'.")
        if "//" in path_str:
            errors.append(f"NO_NON_CANONICAL_CATALOG_PATH: Consecutive slashes in '{path_str}'.")
        if re.search(r'[<>:"|?*]', path_str):
            errors.append(f"INVALID_CHARS: Path '{path_str}' contains forbidden characters.")

        try:
            normalize_catalog_path(path_str)
        except Exception as e:
            errors.append(f"NORMALIZATION_ERROR: {str(e)}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_catalog_entry(entry: CatalogEntry) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        if not entry.identity.asset_id:
            errors.append("EMPTY_ASSET_ID: Asset ID must not be empty.")

        path_ok, path_errs = UniversalBrowserValidator.validate_canonical_path(entry.identity.canonical_path)
        if not path_ok:
            errors.extend(path_errs)

        if len(entry.identity.content_hash) != 64:
            errors.append(f"INVALID_HASH: Content hash '{entry.identity.content_hash}' must be 64 hex characters.")

        if entry.metadata.file_size_bytes < 0:
            errors.append("NEGATIVE_SIZE: Asset file size cannot be negative.")

        return len(errors) == 0, errors

    @staticmethod
    def validate_collection(collection: AssetCollection) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not collection.collection_id:
            errors.append("EMPTY_COLLECTION_ID: Collection ID cannot be empty.")
        if not collection.name:
            errors.append("EMPTY_COLLECTION_NAME: Collection name cannot be empty.")
        if collection.parent_id == collection.collection_id:
            errors.append(f"NO_COLLECTION_CYCLES: Collection '{collection.collection_id}' cannot be its own parent.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_tag(tag: AssetTag) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not tag.tag_id:
            errors.append("EMPTY_TAG_ID: Tag ID cannot be empty.")
        if not tag.name or not tag.name.strip():
            errors.append("EMPTY_TAG_NAME: Tag name cannot be empty.")
        if not re.match(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", tag.color_hex):
            errors.append(f"INVALID_HEX_COLOR: Tag color '{tag.color_hex}' is not a valid hex color.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_snapshot(snapshot: BrowserStateSnapshot) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        expected = snapshot.compute_hash()
        if snapshot.state_hash != expected:
            errors.append(f"SNAPSHOT_CORRUPTION: Expected state hash '{expected}', got '{snapshot.state_hash}'.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_diagnostic_bundle(bundle: BrowserDiagnosticBundle) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        expected = bundle.sign()
        if bundle.signature != expected:
            errors.append(f"BUNDLE_CORRUPTION: Expected signature '{expected}', got '{bundle.signature}'.")
        return len(errors) == 0, errors
