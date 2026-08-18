"""Cross-database UUID type — works with SQLite and PostgreSQL."""
import uuid as _uuid
from sqlalchemy import types


class UUIDType(types.TypeDecorator):
    """Stores UUID as VARCHAR(36) for SQLite, native UUID for PostgreSQL."""
    impl = types.String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return _uuid.UUID(str(value))
        except Exception:
            return value
