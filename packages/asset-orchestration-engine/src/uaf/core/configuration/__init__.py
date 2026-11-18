"""
UAF Core Configuration Package
"""

from .uaf_config import UAFConfig
from .precedence import ConfigResolver, deep_merge

__all__ = ["UAFConfig", "ConfigResolver", "deep_merge"]
