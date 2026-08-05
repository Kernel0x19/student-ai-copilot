"""Connector registry and orchestrator for managing data source connectors

This module provides centralized management of all data connectors, including:
- Connector registration and initialization
- Sequential execution with error isolation
- Database integration for storing/updating opportunities
- Deadline change detection and notification
- Connector status tracking for monitoring

Requirements satisfied:
- Requirement 4.1: Scheduled opportunity polling infrastructure
- Requirement 4.2: Sequential connector execution with error isolation
- Requirement 4.3: Execution logging (start time, end time, records processed, errors)
- Requirement 4.4: Connector failure isolation (continue execution on errors)
- Requirement 6.1: Track last_successful_poll timestamp per connector
- Requirement 6.2: Connector status tracking for monitoring
- Requirement 6.3: Connector metadata and error storage
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from sqlalchemy.orm import Session

from app.db.models import (
    Application,
    ApplicationState,
    AuditLog,
    ConnectorStatus,
    Opportunity,
)
from app.ingestion.connectors.base import BaseConnector
from app.ingestion.connectors.unstop_connector import UnstopConnector
from app.ingestion.connectors.internshala import InternshalaConnector

logger = logging.getLogger(__name__)


# Global connector registry mapping connector names to their classes
CONNECTOR_REGISTRY: Dict[str, Type[BaseConnector]] = {
    'unstop': UnstopConnector,
    'internshala': InternshalaConnector,
}


class ConnectorOrchestrator:
    """Manages execution of all data connectors with error handling and status tracking
    
    The orchestrator is responsible for:
    - Initializing and configuring connectors
    - Executing connectors sequentially with error isolation
    - Storing/updating opportunities in the database with deduplication
    - Detecting deadline changes and triggering notifications
    - Tracking connector execution status for monitoring
    
    **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 6.1, 6.2, 6.3**
    """
    
    def __init__(self, db_session: Session, config: Optional[Dict[str, Any]] = None):
        """Initialize the connector orchestrator
        
        Args:
            db_session: SQLAlchemy database session for data persistence
            config: Configuration dictionary with optional keys:
                - enabled_connectors: List of connector names to enable (default: all)
                - connector_configs: Dict of connector-specific configurations
        """
        self.db = db_session
        self.config = config or {}
        self.connectors = self._init_connectors()
        
        logger.info(
            f"ConnectorOrchestrator initialized with {len(self.connectors)} connectors: "
            f"{[c.name for c in self.connectors]}"
        )
    
    def _init_connectors(self) -> List[BaseConnector]:
        """Initialize connector instances from registry
        
        Returns:
            List of initialized connector instances
        """
        # Get list of enabled connectors (default: all registered connectors)
        enabled = self.config.get('enabled_connectors', list(CONNECTOR_REGISTRY.keys()))
        
        connectors = []
        for name in enabled:
            if name not in CONNECTOR_REGISTRY:
                logger.warning(f"Connector '{name}' not found in registry, skipping")
                continue
            
            # Get connector-specific configuration
            connector_config = self.config.get('connector_configs', {}).get(name, {})
            
            # Instantiate the connector
            connector_class = CONNECTOR_REGISTRY[name]
            connector = connector_class(connector_config)
            connectors.append(connector)
            
            logger.debug(f"Initialized connector: {name}")
        
        return connectors
    
    async def run_all(self) -> Dict[str, Any]:
        """Execute all connectors sequentially with error handling
        
        This method orchestrates the complete data ingestion workflow:
        1. Execute each connector in sequence (Requirement 4.2)
        2. Isolate errors - continue on failure (Requirement 4.4)
        3. Ingest successful results into database
        4. Detect deadline changes and trigger notifications
        5. Update connector status tracking (Requirement 6.1, 6.2)
        6. Log execution metadata (Requirement 4.3)
        
        Returns:
            Dictionary containing:
                - connectors: List of per-connector results
                - timestamp: Overall execution timestamp
                - total_records: Total records processed across all connectors
                - total_errors: Total connector failures
        
        **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 6.1, 6.2, 6.3**
        """
        overall_start_time = datetime.utcnow()
        logger.info("=" * 80)
        logger.info(f"Starting connector orchestration run at {overall_start_time.isoformat()}")
        logger.info("=" * 80)
        
        results = []
        total_records = 0
        total_errors = 0
        
        # Execute each connector sequentially (Requirement 4.2)
        for connector in self.connectors:
            connector_start_time = datetime.utcnow()
            
            logger.info(f"\n>>> Starting connector: {connector.name}")
            
            try:
                # Run the connector (Requirement 4.1)
                result = await connector.run()
                results.append(result)
                
                # Log execution metadata (Requirement 4.3)
                logger.info(
                    f"{connector.name} execution: success={result['success']}, "
                    f"records={result.get('count', 0)}, "
                    f"time={result.get('execution_time_seconds', 0):.2f}s"
                )
                
                if result['success']:
                    # Ingest records into database
                    records_ingested = await self._ingest_records(
                        result['records'],
                        connector.name
                    )
                    total_records += records_ingested
                    
                    # Update connector status - success (Requirement 6.1, 6.2)
                    await self._update_connector_status(
                        name=connector.name,
                        success=True,
                        records_processed=records_ingested,
                        error=None
                    )
                    
                    logger.info(f"✓ {connector.name} completed successfully - {records_ingested} records ingested")
                else:
                    # Update connector status - failure (Requirement 6.3)
                    await self._update_connector_status(
                        name=connector.name,
                        success=False,
                        records_processed=0,
                        error=result.get('error', 'Unknown error')
                    )
                    total_errors += 1
                    
                    logger.error(f"✗ {connector.name} failed: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                # Error isolation - continue executing remaining connectors (Requirement 4.4)
                error_msg = str(e)
                logger.exception(f"✗ Unexpected error in connector {connector.name}: {error_msg}")
                
                results.append({
                    'connector': connector.name,
                    'success': False,
                    'error': error_msg,
                    'timestamp': connector_start_time.isoformat()
                })
                
                # Update connector status - unexpected error (Requirement 6.3)
                await self._update_connector_status(
                    name=connector.name,
                    success=False,
                    records_processed=0,
                    error=error_msg
                )
                total_errors += 1
            
            connector_end_time = datetime.utcnow()
            connector_duration = (connector_end_time - connector_start_time).total_seconds()
            logger.info(f"<<< Finished connector: {connector.name} (duration: {connector_duration:.2f}s)\n")
        
        overall_end_time = datetime.utcnow()
        overall_duration = (overall_end_time - overall_start_time).total_seconds()
        
        # Commit all database changes
        try:
            self.db.commit()
            logger.info("Database changes committed successfully")
        except Exception as e:
            logger.error(f"Failed to commit database changes: {str(e)}")
            self.db.rollback()
            raise
        
        logger.info("=" * 80)
        logger.info(
            f"Connector orchestration completed in {overall_duration:.2f}s: "
            f"{total_records} records processed, {total_errors} errors"
        )
        logger.info("=" * 80)
        
        return {
            'connectors': results,
            'timestamp': overall_start_time.isoformat(),
            'total_records': total_records,
            'total_errors': total_errors,
            'execution_time_seconds': overall_duration
        }
    
    async def run_connector(self, connector_name: str) -> Dict[str, Any]:
        """Execute a single connector by name with error handling
        
        Args:
            connector_name: Name of the connector class (e.g. 'AICTEConnector' or 'aicte')
        """
        # Find connector instance (either by class name or registry key)
        connector = None
        for c in self.connectors:
            if c.name == connector_name or c.__class__.__name__ == connector_name:
                connector = c
                break
                
        if not connector:
            # Try to initialize it if not in current enabled list
            for key, cls in CONNECTOR_REGISTRY.items():
                if key == connector_name or cls.__name__ == connector_name:
                    connector = cls({})
                    break
                    
        if not connector:
            return {"error": f"Connector {connector_name} not found", "success": False}
            
        start_time = datetime.utcnow()
        try:
            result = await connector.run()
            if result.get('success'):
                records_ingested = await self._ingest_records(result.get('records', []), connector.name)
                await self._update_connector_status(connector.name, True, records_ingested, None)
                self.db.commit()
                return {"success": True, "connector": connector.name, "records": records_ingested}
            else:
                error = result.get('error', 'Unknown error')
                await self._update_connector_status(connector.name, False, 0, error)
                self.db.commit()
                return {"success": False, "connector": connector.name, "error": error}
        except Exception as e:
            await self._update_connector_status(connector.name, False, 0, str(e))
            self.db.commit()
            return {"success": False, "connector": connector.name, "error": str(e)}
    
    async def _ingest_records(
        self,
        records: List[Dict[str, Any]],
        source: str
    ) -> int:
        """Store or update opportunities in database with deduplication
        
        For each record:
        - Check for existing opportunity by source_url (deduplication)
        - Update existing record or create new one
        - Detect deadline changes and create events
        
        Args:
            records: List of opportunity dictionaries from connector
            source: Connector name/source identifier
            
        Returns:
            Number of records successfully ingested
        
        **Validates: Requirements 1.5 (deduplication), 5.1-5.2 (deadline change detection)**
        """
        from datetime import date as date_class
        
        ingested_count = 0
        
        for record in records:
            try:
                # Normalize deadline field - convert string to date object if needed
                if 'deadline' in record and record['deadline']:
                    if isinstance(record['deadline'], str):
                        # Parse ISO format date string (YYYY-MM-DD)
                        try:
                            record['deadline'] = datetime.strptime(record['deadline'], '%Y-%m-%d').date()
                        except ValueError:
                            logger.warning(f"Invalid deadline format: {record['deadline']}, setting to None")
                            record['deadline'] = None
                    elif isinstance(record['deadline'], datetime):
                        # Convert datetime to date
                        record['deadline'] = record['deadline'].date()
                    elif not isinstance(record['deadline'], date_class):
                        logger.warning(f"Unexpected deadline type: {type(record['deadline'])}, setting to None")
                        record['deadline'] = None
                
                # Check for duplicate by source_url (Requirement 1.5)
                existing = self.db.query(Opportunity).filter_by(
                    source_url=record.get('source_url')
                ).first()
                
                if existing:
                    # Update existing record
                    old_deadline = existing.deadline
                    
                    # Update all fields from record
                    for key, value in record.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    
                    # Update sync timestamp
                    existing.last_synced_at = datetime.utcnow()
                    
                    logger.debug(f"Updated existing opportunity: {existing.id} - {existing.title}")
                    
                    # Detect deadline change (Requirement 5.1, 5.2)
                    if old_deadline != existing.deadline:
                        await self._create_deadline_change_event(existing, old_deadline)
                else:
                    # Create new opportunity record
                    opp = Opportunity(
                        **record,
                        last_synced_at=datetime.utcnow()
                    )
                    self.db.add(opp)
                    self.db.flush()  # Get the ID
                    
                    logger.debug(f"Created new opportunity: {opp.id} - {opp.title}")
                
                ingested_count += 1
            
            except Exception as e:
                logger.error(
                    f"Failed to ingest record from {source}: {str(e)}. "
                    f"Record: {record.get('title', 'Unknown')}"
                )
                # Rollback this record's changes and continue
                self.db.rollback()
                continue
        
        return ingested_count
    
    async def _create_deadline_change_event(
        self,
        opportunity: Opportunity,
        old_deadline: Optional[Any]
    ) -> None:
        """Log deadline change and trigger notifications for affected students
        
        When a deadline changes:
        1. Create audit log entry (Requirement 5.2)
        2. Find affected students with active applications (Requirement 5.3)
        3. Enqueue notification tasks for each student (Requirement 5.4)
        
        Args:
            opportunity: Updated opportunity with new deadline
            old_deadline: Previous deadline value
        
        **Validates: Requirements 5.2, 5.3, 5.4**
        """
        logger.info(
            f"Deadline change detected for opportunity {opportunity.id}: "
            f"{old_deadline} → {opportunity.deadline}"
        )
        
        # Create audit log entry (Requirement 5.2)
        log = AuditLog(
            action='deadline_change',
            resource_type='opportunity',
            resource_id=opportunity.id,
            audit_metadata={
                'old_deadline': str(old_deadline) if old_deadline else None,
                'new_deadline': str(opportunity.deadline) if opportunity.deadline else None,
                'opportunity_title': opportunity.title,
                'source': opportunity.source
            }
        )
        self.db.add(log)
        
        # Find affected students (Requirement 5.3)
        # Students with saved or in-progress applications
        affected_states = [
            ApplicationState.DISCOVERED,
            ApplicationState.ELIGIBILITY_CHECK,
            ApplicationState.DOCUMENT_VALIDATION,
            ApplicationState.HUMAN_REVIEW
        ]
        
        affected_apps = self.db.query(Application).filter(
            Application.opportunity_id == opportunity.id,
            Application.state.in_(affected_states)
        ).all()
        
        if affected_apps:
            logger.info(f"Found {len(affected_apps)} affected applications for deadline change")
            
            # Enqueue notification tasks (Requirement 5.4)
            # Note: Actual notification sending will be implemented in task 3.3
            # For now, we'll log and create notification records
            from app.db.models import Notification
            
            for app in affected_apps:
                notification = Notification(
                    user_id=app.user_id,
                    title="Deadline Change Alert",
                    body=(
                        f"The deadline for '{opportunity.title}' has changed from "
                        f"{old_deadline} to {opportunity.deadline}. Please review your application."
                    ),
                    channel="in_app"
                )
                self.db.add(notification)
                
                logger.debug(f"Created deadline change notification for user {app.user_id}")
        else:
            logger.debug("No affected applications found for deadline change")
    
    async def _update_connector_status(
        self,
        name: str,
        success: bool,
        records_processed: int = 0,
        error: Optional[str] = None
    ) -> None:
        """Track connector execution status in database
        
        Updates or creates a ConnectorStatus record with execution metadata:
        - last_run timestamp (always updated)
        - last_success timestamp (only on success)
        - last_error message (only on failure)
        - records_processed count
        - is_stale flag (for monitoring)
        
        Args:
            name: Connector name
            success: Whether execution succeeded
            records_processed: Number of records processed
            error: Error message if failed
        
        **Validates: Requirements 6.1, 6.2, 6.3**
        """
        # Find or create connector status record
        status = self.db.query(ConnectorStatus).filter_by(name=name).first()
        if not status:
            status = ConnectorStatus(name=name)
            self.db.add(status)
            logger.debug(f"Created new ConnectorStatus record for {name}")
        
        # Update timestamps
        status.last_run = datetime.utcnow()
        
        if success:
            # Update success metadata (Requirement 6.1)
            status.last_success = datetime.utcnow()
            status.last_error = None
            status.is_stale = False
            logger.debug(f"Updated {name} status: SUCCESS, {records_processed} records")
        else:
            # Update error metadata (Requirement 6.3)
            status.last_error = error
            # Note: is_stale flag will be set by monitoring task (task 3.4)
            logger.debug(f"Updated {name} status: FAILURE - {error}")
        
        # Update records processed count
        status.records_processed = records_processed
        status.updated_at = datetime.utcnow()
        
        # Flush to ensure status is persisted
        self.db.flush()


def get_enabled_connectors() -> List[str]:
    """Get list of all registered connector names
    
    Returns:
        List of connector names available in the registry
    """
    return list(CONNECTOR_REGISTRY.keys())


def create_orchestrator(
    db_session: Session,
    enabled_connectors: Optional[List[str]] = None,
    connector_configs: Optional[Dict[str, Dict[str, Any]]] = None
) -> ConnectorOrchestrator:
    """Factory function to create a configured connector orchestrator
    
    Args:
        db_session: SQLAlchemy database session
        enabled_connectors: List of connector names to enable (default: all)
        connector_configs: Dict mapping connector names to their configurations
        
    Returns:
        Configured ConnectorOrchestrator instance
        
    Example:
        >>> orchestrator = create_orchestrator(
        ...     db_session=db,
        ...     enabled_connectors=['aicte', 'unstop'],
        ...     connector_configs={
        ...         'aicte': {'rate_limit_delay': 3.0},
        ...         'unstop': {'unstop_api_key': 'your-key'}
        ...     }
        ... )
        >>> results = await orchestrator.run_all()
    """
    config = {}
    
    if enabled_connectors is not None:
        config['enabled_connectors'] = enabled_connectors
    
    if connector_configs is not None:
        config['connector_configs'] = connector_configs
    
    return ConnectorOrchestrator(db_session, config)
