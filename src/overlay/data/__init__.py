"""Data layer: OverFast API client, stats transforms, and the refresh worker.

Nothing in this package depends on Qt widgets, so it is safe to run on the
refresh worker thread, off the UI thread.
"""
from __future__ import annotations
