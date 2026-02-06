"""Pytest configuration and fixtures."""

import pytest
import tempfile
import os
from src.dual_board_kanban.infrastructure.base import (
    DatabaseConnection,
    MigrationRunner,
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db = DatabaseConnection(db_path)
    db.connect()

    # Run migrations
    migrator = MigrationRunner(db)
    migrator.run_migrations()

    yield db

    # Cleanup
    db.disconnect()
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def sample_hypothesis_data():
    """Sample hypothesis data for testing."""
    return {
        "business_value": "Increase user engagement",
        "problem_statement": "Users are not engaging with feature X",
        "customers_impacted": "All premium users",
        "hypothesis_statement": "We believe that adding feature X will result in 20% increase in engagement. We will know we've succeeded when daily active users increase by 20%.",
        "metrics_baseline": "Current DAU: 10,000",
        "solutions_ideas": ["Implement feature X", "Add notifications"],
        "lessons_learned": "Initial approach didn't work",
    }


@pytest.fixture
def sample_work_item_data():
    """Sample work item data for testing."""
    return {
        "title": "Implement feature X",
        "goals": ["Complete implementation", "Pass code review"],
        "description": "Implement the new feature X as described in the hypothesis",
        "acceptance_criteria": ["Feature works as specified", "All tests pass"],
        "rigor_level": "MEDIUM",
        "effort_level": "MEDIUM",
        "assignee": "John Doe",
        "swimlane": "STRATEGIC_EXPERIMENTS",
    }
