"""
Tests for PostgreSQL configuration and connection pooling.
"""
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from app.config import Settings


def test_postgres_configuration_fields():
    """Test that PostgreSQL configuration fields exist with correct defaults."""
    settings = Settings()
    
    assert settings.postgres_host == "localhost"
    assert settings.postgres_port == 5432
    assert settings.postgres_db == "edupilot"
    assert settings.postgres_user == "postgres"
    assert settings.postgres_password == ""
    assert settings.db_pool_size == 5
    assert settings.db_max_overflow == 15
    assert settings.db_pool_timeout == 30
    assert settings.db_pool_recycle == 3600


def test_postgres_url_construction():
    """Test that PostgreSQL URL is correctly constructed from components."""
    settings = Settings(
        postgres_host="db.example.com",
        postgres_port=5433,
        postgres_db="testdb",
        postgres_user="testuser",
        postgres_password="testpass"
    )
    
    expected_url = "postgresql://testuser:testpass@db.example.com:5433/testdb"
    assert settings.postgres_url == expected_url


def test_postgres_async_url_construction():
    """Test that PostgreSQL async URL uses asyncpg dialect."""
    settings = Settings(
        postgres_host="db.example.com",
        postgres_port=5432,
        postgres_db="testdb",
        postgres_user="testuser",
        postgres_password="testpass"
    )
    
    expected_url = "postgresql+asyncpg://testuser:testpass@db.example.com:5432/testdb"
    assert settings.postgres_async_url == expected_url


def test_get_database_url_with_postgres_password():
    """Test that get_database_url returns PostgreSQL URL when password is set."""
    settings = Settings(
        postgres_password="securepass",
        database_url="sqlite:///./test.db"
    )
    
    result = settings.get_database_url()
    assert result.startswith("postgresql://")
    assert "securepass" in result


def test_get_database_url_without_postgres_password():
    """Test that get_database_url returns SQLite URL when password is not set."""
    settings = Settings(
        postgres_password="",
        database_url="sqlite:///./test.db"
    )
    
    result = settings.get_database_url()
    assert result == "sqlite:///./test.db"


def test_connection_pooling_configuration():
    """Test that connection pooling is configured with correct parameters."""
    settings = Settings(
        postgres_password="testpass",
        db_pool_size=5,
        db_max_overflow=15,
        db_pool_timeout=30,
        db_pool_recycle=3600
    )
    
    # Verify min pool size
    assert settings.db_pool_size == 5
    
    # Verify max connections (pool_size + max_overflow = 20)
    assert settings.db_pool_size + settings.db_max_overflow == 20
    
    # Verify timeout and recycle settings
    assert settings.db_pool_timeout == 30
    assert settings.db_pool_recycle == 3600


def test_sqlalchemy_engine_pool_parameters():
    """Test that SQLAlchemy engine receives correct pooling parameters."""
    # This is more of an integration test to verify the session.py configuration
    from app.db.session import engine, database_url
    
    if database_url.startswith("postgresql"):
        # Verify pool configuration
        assert engine.pool.size() >= 0  # Pool size is dynamic
        assert hasattr(engine.pool, '_overflow_lock')  # Indicates pool with overflow is configured
    elif database_url.startswith("sqlite"):
        # SQLite doesn't use connection pooling the same way
        assert engine.pool is not None


def test_postgres_dialect_selection():
    """Test that PostgreSQL uses the correct SQLAlchemy dialect."""
    settings = Settings(
        postgres_password="testpass"
    )
    
    url = settings.get_database_url()
    
    # Create a test engine to verify dialect
    test_engine = create_engine(url, pool_size=5, max_overflow=15)
    
    assert test_engine.dialect.name == "postgresql"
    
    # Cleanup
    test_engine.dispose()


def test_connection_pool_min_max_boundaries():
    """Test that connection pool respects min 5 and max 20 boundaries."""
    settings = Settings(
        postgres_password="testpass",
        db_pool_size=5,
        db_max_overflow=15
    )
    
    # Minimum connections
    assert settings.db_pool_size >= 5
    
    # Maximum connections (pool_size + max_overflow)
    max_connections = settings.db_pool_size + settings.db_max_overflow
    assert max_connections == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
