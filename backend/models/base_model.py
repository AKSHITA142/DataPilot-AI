import json
from typing import Any
from sqlalchemy.types import TypeDecorator, TEXT
from sqlalchemy.dialects.postgresql import JSONB


class JSONType(TypeDecorator):
    """
    Platform-independent JSON column type.
    Uses PostgreSQL JSONB in production and text-based JSON on SQLite/other DBs.
    """
    impl = TEXT
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(TEXT())

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return value
        return value
