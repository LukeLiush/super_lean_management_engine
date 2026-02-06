"""Base classes and interfaces for repositories and services."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Set
from datetime import datetime

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """Base repository interface."""

    @abstractmethod
    def save(self, entity: T) -> None:
        """Save entity to persistence."""
        pass

    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[T]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def find_all(self) -> List[T]:
        """Find all entities."""
        pass


class DatabaseConnection:
    """SQLite database connection manager."""

    def __init__(self, db_path: str = "dual_board_kanban.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self._connection = None

    def connect(self):
        """Establish database connection."""
        import sqlite3

        self._connection = sqlite3.connect(self.db_path)
        self._connection.row_factory = sqlite3.Row
        return self._connection

    def disconnect(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def get_connection(self):
        """Get active database connection."""
        if self._connection is None:
            self.connect()
        return self._connection

    def execute(self, query: str, params: tuple = ()):
        """Execute query and return cursor."""
        conn = self.get_connection()
        return conn.execute(query, params)

    def commit(self):
        """Commit transaction."""
        if self._connection:
            self._connection.commit()

    def rollback(self):
        """Rollback transaction."""
        if self._connection:
            self._connection.rollback()


class MigrationRunner:
    """Database migration system."""

    def __init__(self, db_connection: DatabaseConnection):
        """Initialize migration runner."""
        self.db = db_connection
        self.migrations_applied: Set[str] = set()

    def run_migrations(self):
        """Run all pending migrations."""
        self._ensure_migrations_table()
        self._run_schema_migration()

    def _ensure_migrations_table(self):
        """Create migrations tracking table if not exists."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id TEXT PRIMARY KEY,
                applied_at TIMESTAMP NOT NULL
            )
        """)
        self.db.commit()

    def _run_schema_migration(self):
        """Run main schema migration."""
        migration_id = "001_initial_schema"

        cursor = self.db.execute(
            "SELECT id FROM migrations WHERE id = ?", (migration_id,)
        )
        if cursor.fetchone():
            return  # Already applied

        # Create all tables
        self._create_hypotheses_table()
        self._create_work_items_table()
        self._create_work_item_children_table()
        self._create_stage_transitions_table()
        self._create_blockers_table()
        self._create_flow_metrics_snapshots_table()

        # Record migration
        self.db.execute(
            "INSERT INTO migrations (id, applied_at) VALUES (?, ?)",
            (migration_id, datetime.utcnow()),
        )
        self.db.commit()

    def _create_hypotheses_table(self):
        """Create hypotheses table."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS hypotheses (
                id TEXT PRIMARY KEY,
                business_value TEXT NOT NULL,
                problem_statement TEXT NOT NULL,
                customers_impacted TEXT NOT NULL,
                hypothesis_statement TEXT NOT NULL,
                metrics_baseline TEXT NOT NULL,
                solutions_ideas TEXT NOT NULL,
                lessons_learned TEXT,
                stage TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """)
        self.db.commit()

    def _create_work_items_table(self):
        """Create work items table."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS work_items (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                goals TEXT NOT NULL,
                description TEXT NOT NULL,
                acceptance_criteria TEXT NOT NULL,
                rigor_level TEXT NOT NULL,
                effort_level TEXT NOT NULL,
                assignee TEXT,
                swimlane TEXT NOT NULL,
                stage TEXT NOT NULL,
                parent_hypothesis_id TEXT NOT NULL,
                parent_work_item_id TEXT,
                is_invalidated BOOLEAN DEFAULT FALSE,
                created_maintenance_burden BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                FOREIGN KEY (parent_hypothesis_id) REFERENCES hypotheses(id),
                FOREIGN KEY (parent_work_item_id) REFERENCES work_items(id)
            )
        """)
        self.db.commit()

    def _create_work_item_children_table(self):
        """Create work item children junction table."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS work_item_children (
                parent_id TEXT NOT NULL,
                child_id TEXT NOT NULL,
                PRIMARY KEY (parent_id, child_id),
                FOREIGN KEY (parent_id) REFERENCES work_items(id),
                FOREIGN KEY (child_id) REFERENCES work_items(id)
            )
        """)
        self.db.commit()

    def _create_stage_transitions_table(self):
        """Create stage transitions table."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS stage_transitions (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                from_stage TEXT,
                to_stage TEXT NOT NULL,
                transitioned_at TIMESTAMP NOT NULL
            )
        """)
        self.db.commit()

    def _create_blockers_table(self):
        """Create blockers table."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS blockers (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                blocker_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                owner TEXT NOT NULL,
                reason TEXT NOT NULL,
                blocked_at TIMESTAMP NOT NULL,
                unblocked_at TIMESTAMP
            )
        """)
        self.db.commit()

    def _create_flow_metrics_snapshots_table(self):
        """Create flow metrics snapshots table."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS flow_metrics_snapshots (
                id TEXT PRIMARY KEY,
                snapshot_date TIMESTAMP NOT NULL,
                cycle_time_avg REAL,
                cycle_time_median REAL,
                cycle_time_p50 REAL,
                cycle_time_p75 REAL,
                cycle_time_p90 REAL,
                lead_time_avg REAL,
                lead_time_median REAL,
                lead_time_p50 REAL,
                lead_time_p75 REAL,
                lead_time_p90 REAL,
                throughput_count INTEGER,
                throughput_cadence TEXT,
                flow_load INTEGER,
                flow_debt INTEGER,
                blocking_age_total REAL,
                blocking_age_avg REAL,
                blocking_count INTEGER
            )
        """)
        self.db.commit()
