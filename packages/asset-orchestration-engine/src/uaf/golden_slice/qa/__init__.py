"""Automated QA runner and test case definitions for Golden Vertical Slice."""

from uaf.golden_slice.qa.test_cases import QATestResult
from uaf.golden_slice.qa.runner import QARunner, QASuiteReport

__all__ = [
    "QATestResult",
    "QARunner",
    "QASuiteReport",
]
