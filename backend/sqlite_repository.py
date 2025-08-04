from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any, Type, Tuple
from sqlalchemy import Table, select, insert, update, delete, func, and_
from sqlalchemy.engine import Engine
from pydantic import BaseModel
from utils.result import Result
import database
from datetime import date

T = TypeVar('T', bound=BaseModel)


class SQLiteRepository(ABC, Generic[T]):
    """
    Abstract base class defining the interface for SQLite repository operations
    with Pydantic models.
    """
    
    @abstractmethod
    def get_by_id(self, record_id: int) -> Result:
        """
        Retrieve a record by its ID, returning a Result with the Pydantic model instance
        or an error if not found.
        """
        pass
    
    @abstractmethod
    def get_all(self) -> Result:
        """
        Retrieve all records, returning a Result with a list of Pydantic model instances.
        """
        pass
    
    @abstractmethod
    def create(self, model: T) -> Result:
        """
        Create a new record using the provided Pydantic model.
        Returns a Result with the ID of the created record.
        """
        pass
    
    @abstractmethod
    def update(self, record_id: int, model: T) -> Result:
        """
        Update an existing record with the provided Pydantic model.
        Returns a Result indicating success or failure.
        """
        pass
    
    @abstractmethod
    def delete(self, record_id: int) -> Result:
        """
        Delete a record by its ID.
        Returns a Result indicating success or failure.
        """
        pass

class BaseSQLiteRepository(SQLiteRepository[T]):
    """
    Base implementation of the SQLiteRepository interface using SQLAlchemy.
    """
    
    def __init__(self, table: Table, model_class: Type[T], engine: Optional[Engine] = None):
        """
        Initialize the repository with a table and model class.
        
        Args:
            table: The SQLAlchemy Table object
            model_class: The Pydantic model class to use for records
            engine: Optional SQLAlchemy engine instance (will use default if not provided)
        """
        self.table = table
        self.model_class = model_class
        self.engine = engine or database.engine
    
    def _row_to_model(self, row) -> T:
        """Convert a SQLAlchemy Row to a Pydantic model"""
        if row is None:
            return None
        
        # Convert row to dict, handling SQLAlchemy Row objects
        if hasattr(row, '_mapping'):
            data = dict(row._mapping)
        else:
            data = dict(row)
            
        # Handle date objects that might need conversion
        for key, value in data.items():
            if isinstance(value, date):
                data[key] = value
        
        return self.model_class.model_validate(data)
    
    def _model_to_dict(self, model: T) -> Dict[str, Any]:
        """Convert a Pydantic model to a dictionary for database operations"""
        # Use model_dump and exclude the 'id' field for creates/updates as it's auto-generated
        data = model.model_dump(exclude={'id'}, exclude_none=True)
        return data
    
    def get_by_id(self, record_id: int) -> Result:
        """Get a record by its ID and convert to Pydantic model"""
        try:
            stmt = select(self.table).where(self.table.c.id == record_id)
            
            with self.engine.connect() as conn:
                result = conn.execute(stmt).fetchone()
                
                if not result:
                    return Result.error_result(f"Record with ID {record_id} not found", 404)
                
                model = self._row_to_model(result)
                return Result.success_result(model)
                
        except Exception as e:
            return Result.error_result(f"Error fetching record: {str(e)}", 500)
    
    def get_all(self) -> Result:
        """Get all records and convert to Pydantic models"""
        try:
            stmt = select(self.table)
            
            with self.engine.connect() as conn:
                results = conn.execute(stmt).fetchall()
                models = [self._row_to_model(row) for row in results]
                return Result.success_result(models)
                
        except Exception as e:
            return Result.error_result(f"Error fetching all records: {str(e)}", 500)
    
    def create(self, model: T) -> Result:
        """Create a new record from a Pydantic model"""
        try:
            data = self._model_to_dict(model)
            stmt = insert(self.table).values(**data)
            
            with self.engine.begin() as conn:
                result = conn.execute(stmt)
                record_id = result.inserted_primary_key[0]
                return Result.success_result(record_id)
                
        except Exception as e:
            return Result.error_result(f"Error creating record: {str(e)}", 500)
    
    def update(self, record_id: int, model: T) -> Result:
        """Update an existing record with a Pydantic model"""
        try:
            # Check if record exists
            check_result = self.get_by_id(record_id)
            if not check_result.success:
                return check_result
            
            data = self._model_to_dict(model)
            stmt = update(self.table).where(self.table.c.id == record_id).values(**data)
            
            with self.engine.begin() as conn:
                conn.execute(stmt)
                return Result.success_result()
                
        except Exception as e:
            return Result.error_result(f"Error updating record: {str(e)}", 500)
    
    def delete(self, record_id: int) -> Result:
        """Delete a record by its ID"""
        try:
            # Check if record exists
            check_result = self.get_by_id(record_id)
            if not check_result.success:
                return check_result
            
            stmt = delete(self.table).where(self.table.c.id == record_id)
            
            with self.engine.begin() as conn:
                conn.execute(stmt)
                return Result.success_result()
                
        except Exception as e:
            return Result.error_result(f"Error deleting record: {str(e)}", 500)

class BaseSQLiteService(Generic[T]):
    """
    Base service class that wraps repository operations.
    Subclasses only need to specify the repository type.
    """
    
    def __init__(self, repository: BaseSQLiteRepository[T]):
        self.repository = repository
    
    def get_by_id(self, record_id: int) -> Result:
        return self.repository.get_by_id(record_id)
    
    def get_all(self) -> Result:
        return self.repository.get_all()
    
    def create(self, model: T) -> Result:
        return self.repository.create(model)
    
    def update(self, record_id: int, model: T) -> Result:
        return self.repository.update(record_id, model)
    
    def delete(self, record_id: int) -> Result:
        return self.repository.delete(record_id)
    
