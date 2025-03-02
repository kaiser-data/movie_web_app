# datamanager/__init__.py

from .sqlite_data_manager import SQLiteDataManager
from .models import db
from .data_manager_interface import DataManagerInterface

# Expose the components as part of the package
__all__ = ['SQLiteDataManager', 'db', 'DataManagerInterface']