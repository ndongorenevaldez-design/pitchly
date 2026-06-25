# Responsibility: root-level dependencies re-export for import compatibility
# Actual auth dependency logic lives in app/auth.py

from app.auth import get_current_user

__all__ = ["get_current_user"]
