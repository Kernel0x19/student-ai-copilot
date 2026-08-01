"""Unit tests for connector registry and orchestrator

Tests cover:
- Connector initialization and configuration
- Sequential execution with error isolation
- Database ingestion and deduplication
- Deadline change detection
- Connector status tracking
"""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import (
    Base,
    ConnectorStatus,
    Opportunity,
    Application,
    ApplicationState,
    AuditLog,
    Notification,
)
from app.ingestion.connector_registry import (
    ConnectorOrchestrator,
    CONNECTOR_REGISTRY,
    create_orchestrator,
    get_enabled_connectors,
)
from app.ingestion.connectors.base import BaseConnector


# Test fixtures

@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def mock_connector_class():
    """Create a mock connector class for testing"""
    
    class MockConnector(BaseConnector):
        """Mock connector for testing"""
        
        def __init__(self, config):
            super().__init__(config)
            self.name = "MockConnector"
        
        async def fetch(self):
            return [
                {
                    'html': '<div>Test scholarship</div>',
                    'url': 'https://example.com/scholarship1'
                }
            ]
        
        async def parse(self, raw_data):
            return [
                {
                    'title': 'Test Scholarship 1',
                    'description': 'Test description',
                    'deadline': (date.today() + timedelta(days=30)).isoformat(),
                    'source_url': 'https://example.com/scholarship1',
                    'source': 'test',
                    'category': 'scholarship',
                    'amount_min': 10000,
                    'amount_max': 50000,
                }
            ]
    
    return MockConnector


# Test connector initialization

def test_get_enabled_connectors():
    """Test getting list of registered connectors"""
    connectors = get_enabled_connectors()
    
    assert 'aicte' in connectors
    assert 'unstop' in connectors
    assert 'internshala' in connectors
    assert len(connectors) == 3


def test_orchestrator_initialization(db_session):
    """Test orchestrator initialization with default config"""
    orchestrator = ConnectorOrchestrator(db_session)
    
    assert orchestrator.db == db_session
    assert len(orchestrator.connectors) == 3
    assert all(isinstance(c, BaseConnector) for c in orchestrator.connectors)


def test_orchestrator_with_enabled_connectors(db_session):
    """Test orchestrator with specific enabled connectors"""
    config = {'enabled_connectors': ['aicte', 'unstop']}
    orchestrator = ConnectorOrchestrator(db_session, config)
    
    assert len(orchestrator.connectors) == 2
    connector_names = [c.name for c in orchestrator.connectors]
    assert 'AICTEConnector' in connector_names
    assert 'UnstopConnector' in connector_names


def test_orchestrator_with_connector_configs(db_session):
    """Test orchestrator with connector-specific configurations"""
    config = {
        'enabled_connectors': ['aicte'],
        'connector_configs': {
            'aicte': {
                'rate_limit_delay': 5.0,
                'timeout': 60.0
            }
        }
    }
    orchestrator = ConnectorOrchestrator(db_session, config)
    
    assert len(orchestrator.connectors) == 1
    aicte_connector = orchestrator.connectors[0]
    assert aicte_connector.rate_limit_delay == 5.0
    assert aicte_connector.timeout == 60.0


def test_create_orchestrator_factory(db_session):
    """Test orchestrator factory function"""
    orchestrator = create_orchestrator(
        db_session,
        enabled_connectors=['aicte'],
        connector_configs={'aicte': {'timeout': 45.0}}
    )
    
    assert isinstance(orchestrator, ConnectorOrchestrator)
    assert len(orchestrator.connectors) == 1


# Test connector execution

@pytest.mark.asyncio
async def test_run_all_success(db_session, mock_connector_class):
    """Test successful execution of all connectors"""
    # Patch the registry with our mock connector
    with patch.dict(CONNECTOR_REGISTRY, {'mock': mock_connector_class}):
        config = {'enabled_connectors': ['mock']}
        orchestrator = ConnectorOrchestrator(db_session, config)
        
        # Run orchestration
        results = await orchestrator.run_all()
        
        # Verify results
        assert 'connectors' in results
        assert 'timestamp' in results
        assert 'total_records' in results
        assert 'total_errors' in results
        
        assert len(results['connectors']) == 1
        assert results['connectors'][0]['success'] is True
        assert results['total_records'] == 1
        assert results['total_errors'] == 0
        
        # Verify opportunity was created in database
        opportunities = db_session.query(Opportunity).all()
        assert len(opportunities) == 1
        assert opportunities[0].title == 'Test Scholarship 1'
        
        # Verify connector status was updated
        status = db_session.query(ConnectorStatus).filter_by(name='MockConnector').first()
        assert status is not None
        assert status.last_success is not None
        assert status.last_error is None


@pytest.mark.asyncio
async def test_run_all_with_error_isolation(db_session, mock_connector_class):
    """Test error isolation - continue on connector failure"""
    
    # Create a failing connector
    class FailingConnector(BaseConnector):
        def __init__(self, config):
            super().__init__(config)
            self.name = "FailingConnector"
        
        async def fetch(self):
            raise Exception("Simulated fetch error")
        
        async def parse(self, raw_data):
            return []
    
    # Patch registry with both connectors
    with patch.dict(CONNECTOR_REGISTRY, {
        'failing': FailingConnector,
        'mock': mock_connector_class
    }):
        config = {'enabled_connectors': ['failing', 'mock']}
        orchestrator = ConnectorOrchestrator(db_session, config)
        
        # Run orchestration
        results = await orchestrator.run_all()
        
        # Verify first connector failed, second succeeded
        assert len(results['connectors']) == 2
        assert results['connectors'][0]['success'] is False
        assert results['connectors'][1]['success'] is True
        assert results['total_errors'] == 1
        
        # Verify successful connector still ingested data
        opportunities = db_session.query(Opportunity).all()
        assert len(opportunities) == 1


# Test database ingestion

@pytest.mark.asyncio
async def test_ingest_records_creates_new_opportunities(db_session):
    """Test creating new opportunity records"""
    orchestrator = ConnectorOrchestrator(db_session)
    
    records = [
        {
            'title': 'Scholarship A',
            'description': 'Description A',
            'deadline': date.today().isoformat(),
            'source_url': 'https://example.com/scholarship-a',
            'source': 'test',
            'category': 'scholarship',
        },
        {
            'title': 'Scholarship B',
            'description': 'Description B',
            'deadline': date.today().isoformat(),
            'source_url': 'https://example.com/scholarship-b',
            'source': 'test',
            'category': 'scholarship',
        }
    ]
    
    count = await orchestrator._ingest_records(records, 'test')
    
    assert count == 2
    opportunities = db_session.query(Opportunity).all()
    assert len(opportunities) == 2


@pytest.mark.asyncio
async def test_ingest_records_updates_existing(db_session):
    """Test updating existing opportunity records (deduplication)"""
    # Create existing opportunity
    existing = Opportunity(
        title='Old Title',
        description='Old description',
        deadline=date.today(),
        source_url='https://example.com/scholarship-1',
        source='test',
        category='scholarship',
    )
    db_session.add(existing)
    db_session.commit()
    existing_id = existing.id
    
    orchestrator = ConnectorOrchestrator(db_session)
    
    # Update with same source_url
    records = [
        {
            'title': 'Updated Title',
            'description': 'Updated description',
            'deadline': (date.today() + timedelta(days=10)).isoformat(),
            'source_url': 'https://example.com/scholarship-1',
            'source': 'test',
            'category': 'scholarship',
        }
    ]
    
    count = await orchestrator._ingest_records(records, 'test')
    
    assert count == 1
    
    # Verify update, not create
    opportunities = db_session.query(Opportunity).all()
    assert len(opportunities) == 1
    assert opportunities[0].id == existing_id
    assert opportunities[0].title == 'Updated Title'


# Test deadline change detection

@pytest.mark.asyncio
async def test_deadline_change_creates_audit_log(db_session):
    """Test deadline change creates audit log entry"""
    # Create opportunity
    opp = Opportunity(
        title='Test Scholarship',
        description='Test',
        deadline=date.today(),
        source_url='https://example.com/test',
        source='test',
        category='scholarship',
    )
    db_session.add(opp)
    db_session.commit()
    
    orchestrator = ConnectorOrchestrator(db_session)
    
    # Trigger deadline change
    old_deadline = opp.deadline
    new_deadline = date.today() + timedelta(days=15)
    opp.deadline = new_deadline
    
    await orchestrator._create_deadline_change_event(opp, old_deadline)
    db_session.commit()
    
    # Verify audit log created
    logs = db_session.query(AuditLog).filter_by(action='deadline_change').all()
    assert len(logs) == 1
    assert logs[0].resource_type == 'opportunity'
    assert logs[0].resource_id == opp.id


@pytest.mark.asyncio
async def test_deadline_change_notifies_affected_users(db_session):
    """Test deadline change creates notifications for affected users"""
    from app.db.models import User
    
    # Create user
    user = User(email='test@example.com')
    db_session.add(user)
    db_session.flush()
    
    # Create opportunity
    opp = Opportunity(
        title='Test Scholarship',
        description='Test',
        deadline=date.today(),
        source_url='https://example.com/test',
        source='test',
        category='scholarship',
    )
    db_session.add(opp)
    db_session.flush()
    
    # Create active application
    app = Application(
        user_id=user.id,
        opportunity_id=opp.id,
        state=ApplicationState.ELIGIBILITY_CHECK,
    )
    db_session.add(app)
    db_session.commit()
    
    orchestrator = ConnectorOrchestrator(db_session)
    
    # Trigger deadline change
    old_deadline = opp.deadline
    opp.deadline = date.today() + timedelta(days=20)
    
    await orchestrator._create_deadline_change_event(opp, old_deadline)
    db_session.commit()
    
    # Verify notification created
    notifications = db_session.query(Notification).filter_by(user_id=user.id).all()
    assert len(notifications) == 1
    assert 'Deadline Change' in notifications[0].title


# Test connector status tracking

@pytest.mark.asyncio
async def test_update_connector_status_success(db_session):
    """Test updating connector status on success"""
    orchestrator = ConnectorOrchestrator(db_session)
    
    await orchestrator._update_connector_status(
        name='test_connector',
        success=True,
        records_processed=42,
        error=None
    )
    db_session.commit()
    
    status = db_session.query(ConnectorStatus).filter_by(name='test_connector').first()
    assert status is not None
    assert status.last_run is not None
    assert status.last_success is not None
    assert status.last_error is None
    assert status.records_processed == 42
    assert status.is_stale is False


@pytest.mark.asyncio
async def test_update_connector_status_failure(db_session):
    """Test updating connector status on failure"""
    orchestrator = ConnectorOrchestrator(db_session)
    
    await orchestrator._update_connector_status(
        name='test_connector',
        success=False,
        records_processed=0,
        error='Connection timeout'
    )
    db_session.commit()
    
    status = db_session.query(ConnectorStatus).filter_by(name='test_connector').first()
    assert status is not None
    assert status.last_run is not None
    assert status.last_error == 'Connection timeout'
    assert status.records_processed == 0


@pytest.mark.asyncio
async def test_update_connector_status_updates_existing(db_session):
    """Test updating existing connector status record"""
    # Create initial status
    status = ConnectorStatus(
        name='test_connector',
        last_run=datetime.utcnow(),
        last_success=datetime.utcnow(),
        records_processed=10
    )
    db_session.add(status)
    db_session.commit()
    status_id = status.id
    
    orchestrator = ConnectorOrchestrator(db_session)
    
    # Update status
    await orchestrator._update_connector_status(
        name='test_connector',
        success=True,
        records_processed=25,
        error=None
    )
    db_session.commit()
    
    # Verify same record was updated
    statuses = db_session.query(ConnectorStatus).filter_by(name='test_connector').all()
    assert len(statuses) == 1
    assert statuses[0].id == status_id
    assert statuses[0].records_processed == 25


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
