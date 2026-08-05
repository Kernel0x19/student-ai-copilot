"""Data source connectors for automated opportunity ingestion"""

from .base import BaseConnector, STANDARD_OPPORTUNITY_SCHEMA, get_schema_documentation
from .unstop_connector import UnstopConnector
from .internshala import InternshalaConnector
from .indeed_connector import IndeedConnector
from .naukri_connector import NaukriConnector
from .wellfound_connector import WellfoundConnector
from .seed_connectors import NSPConnector, MahaDBTConnector, MySchemeConnector

__all__ = [
    'BaseConnector',
    'STANDARD_OPPORTUNITY_SCHEMA',
    'get_schema_documentation',
    'UnstopConnector',
    'InternshalaConnector',
    'IndeedConnector',
    'NaukriConnector',
    'WellfoundConnector',
    'NSPConnector',
    'MahaDBTConnector',
    'MySchemeConnector',
]

