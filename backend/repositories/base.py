from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from backend.database.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic repository providing basic CRUD operations."""

    def __init__(self, model_cls: Type[T], session: Session):
        self.model_cls = model_cls
        self.session = session

    def get_by_id(self, item_id: str) -> Optional[T]:
        """Fetch a single record by primary key UUID."""
        return self.session.query(self.model_cls).filter(self.model_cls.id == item_id).first()

    def create(self, instance: T) -> T:
        """Add and commit a new instance to the database."""
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """List records with pagination."""
        return self.session.query(self.model_cls).offset(skip).limit(limit).all()

    def update(self, instance: T, update_data: Dict[str, Any]) -> T:
        """Update fields on an existing instance."""
        for key, value in update_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def delete(self, item_id: str) -> bool:
        """Delete a record by primary key UUID."""
        instance = self.get_by_id(item_id)
        if instance:
            self.session.delete(instance)
            self.session.commit()
            return True
        return False
