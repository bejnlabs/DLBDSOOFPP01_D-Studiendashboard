"""Darstellungsschicht."""

from .cli import CliView
from .protokoll import DashboardView

__all__ = ["DashboardView", "CliView"]
