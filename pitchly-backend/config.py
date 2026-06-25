# Responsibility: root-level config re-export for import compatibility
# All actual configuration lives in app/config.py

from app.config import Settings, get_settings

settings = get_settings()

__all__ = ["Settings", "settings", "get_settings"]
