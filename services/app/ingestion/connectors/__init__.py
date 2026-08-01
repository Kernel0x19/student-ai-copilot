"""Data source connectors for automated opportunity ingestion"""

from .base import BaseConnector, STANDARD_OPPORTUNITY_SCHEMA, get_schema_documentation
from .aicte import AICTEConnector
from .unstop import UnstopConnector
from .internshala import InternshalaConnector
from .seed_connectors import NSPConnector, MahaDBTConnector, MySchemeConnector

__all__ = [
    'BaseConnector',
    'STANDARD_OPPORTUNITY_SCHEMA',
    'get_schema_documentation',
    'AICTEConnector',
    'UnstopConnector',
    'InternshalaConnector',
    'NSPConnector',
    'MahaDBTConnector',
    'MySchemeConnector',
]
