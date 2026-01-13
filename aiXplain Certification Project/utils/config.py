"""Compatibility shim: `utils.config` imports `Config` from `utils.utils_config`"""
from .utils_config import Config

__all__ = ["Config"]
