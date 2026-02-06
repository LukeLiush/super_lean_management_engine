"""Repository implementations for persistence."""

import json
from datetime import datetime
from typing import List, Optional
from dual_board_kanban.infrastructure.base import DatabaseConnection, Repository
from dual_board_kanban.domain.hypothesis import Hypothesis
from dual_board_kanban.domain.work_item import WorkItem
from dual_board_kanban.domain.value_objects import (
    Stage,
    BoardType,
    RigorLevel,
    EffortLevel,
    Swimlane,
)


class HypothesisRepository(Repository[Hypothesis]):
    """Repository for hypothesis persistence."""

    def __init__(self, db_connection: DatabaseConnection):
        """Initialize repository with database connection."""
        self.db = db_connection

    def save(self, hypothesis: Hypothesis) -> None:
        """Save hypothesis to database."""
        solutions_ideas_json = json.dumps(hypothesis.solutions_ideas)

        # Check if exists
        cursor = self.db.execute(
            "SELECT id FROM hypotheses WHERE id = ?", (hypothesis.id,)
        )
        exists = cursor.fetchone() is not None

        if exists:
            # Update
            self.db.execute(
                """
                UPDATE hypotheses SET
                    business_value = ?,
                    problem_statement = ?,
                    customers_impacted = ?,
                    hypothesis_statement = ?,
                    metrics_baseline = ?,
                    solutions_ideas = ?,
                    lessons_learned = ?,
                    stage = ?,
                    updated_at = ?
                WHERE id = ?
            """,
                (
                    hypothesis.business_value,
                    hypothesis.problem_statement,
                    hypothesis.customers_impacted,
                    hypothesis.hypothesis_statement,
                    hypothesis.metrics_baseline,
                    solutions_ideas_json,
                    hypothesis.lessons_learned,
                    hypothesis.stage.name,
                    hypothesis.updated_at,
                    hypothesis.id,
                ),
            )
        else:
            # Insert
            self.db.execute(
                """
                INSERT INTO hypotheses (
                    id, business_value, problem_statement, customers_impacted,
                    hypothesis_statement, metrics_baseline, solutions_ideas,
                    lessons_learned, stage, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    hypothesis.id,
                    hypothesis.business_value,
                    hypothesis.problem_statement,
                    hypothesis.customers_impacted,
                    hypothesis.hypothesis_statement,
                    hypothesis.metrics_baseline,
                    solutions_ideas_json,
                    hypothesis.lessons_learned,
                    hypothesis.stage.name,
                    hypothesis.created_at,
                    hypothesis.updated_at,
                ),
            )

        self.db.commit()

    def find_by_id(self, hypothesis_id: str) -> Optional[Hypothesis]:
        """Find hypothesis by ID."""
        cursor = self.db.execute(
            "SELECT * FROM hypotheses WHERE id = ?", (hypothesis_id,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_hypothesis(row)

    def find_all(self) -> List[Hypothesis]:
        """Find all hypotheses."""
        cursor = self.db.execute("SELECT * FROM hypotheses")
        rows = cursor.fetchall()

        return [self._row_to_hypothesis(row) for row in rows]

    def find_by_stage(self, stage: Stage) -> List[Hypothesis]:
        """Find hypotheses in specific stage."""
        cursor = self.db.execute(
            "SELECT * FROM hypotheses WHERE stage = ?", (stage.name,)
        )
        rows = cursor.fetchall()

        return [self._row_to_hypothesis(row) for row in rows]

    def _row_to_hypothesis(self, row) -> Hypothesis:
        """Convert database row to Hypothesis entity."""
        solutions_ideas = json.loads(row["solutions_ideas"])
        stage = Stage.get_stage_by_name(row["stage"], BoardType.STRATEGIC)

        return Hypothesis(
            id=row["id"],
            business_value=row["business_value"],
            problem_statement=row["problem_statement"],
            customers_impacted=row["customers_impacted"],
            hypothesis_statement=row["hypothesis_statement"],
            metrics_baseline=row["metrics_baseline"],
            solutions_ideas=solutions_ideas,
            lessons_learned=row["lessons_learned"],
            stage=stage,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            stage_transitions=[],
            blocker=None,
        )


class WorkItemRepository(Repository[WorkItem]):
    """Repository for work item persistence."""

    def __init__(self, db_connection: DatabaseConnection):
        """Initialize repository with database connection."""
        self.db = db_connection

    def save(self, work_item: WorkItem) -> None:
        """Save work item to database."""
        goals_json = json.dumps(work_item.goals)
        acceptance_criteria_json = json.dumps(work_item.acceptance_criteria)

        # Check if exists
        cursor = self.db.execute(
            "SELECT id FROM work_items WHERE id = ?", (work_item.id,)
        )
        exists = cursor.fetchone() is not None

        if exists:
            # Update
            self.db.execute(
                """
                UPDATE work_items SET
                    title = ?,
                    goals = ?,
                    description = ?,
                    acceptance_criteria = ?,
                    rigor_level = ?,
                    effort_level = ?,
                    assignee = ?,
                    swimlane = ?,
                    stage = ?,
                    parent_hypothesis_id = ?,
                    parent_work_item_id = ?,
                    is_invalidated = ?,
                    created_maintenance_burden = ?,
                    updated_at = ?
                WHERE id = ?
            """,
                (
                    work_item.title,
                    goals_json,
                    work_item.description,
                    acceptance_criteria_json,
                    work_item.rigor_level.value,
                    work_item.effort_level.value,
                    work_item.assignee,
                    work_item.swimlane.value,
                    work_item.stage.name,
                    work_item.parent_hypothesis_id,
                    work_item.parent_work_item_id,
                    work_item.is_invalidated,
                    work_item.created_maintenance_burden,
                    work_item.updated_at,
                    work_item.id,
                ),
            )
        else:
            # Insert
            self.db.execute(
                """
                INSERT INTO work_items (
                    id, title, goals, description, acceptance_criteria,
                    rigor_level, effort_level, assignee, swimlane, stage,
                    parent_hypothesis_id, parent_work_item_id,
                    is_invalidated, created_maintenance_burden,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    work_item.id,
                    work_item.title,
                    goals_json,
                    work_item.description,
                    acceptance_criteria_json,
                    work_item.rigor_level.value,
                    work_item.effort_level.value,
                    work_item.assignee,
                    work_item.swimlane.value,
                    work_item.stage.name,
                    work_item.parent_hypothesis_id,
                    work_item.parent_work_item_id,
                    work_item.is_invalidated,
                    work_item.created_maintenance_burden,
                    work_item.created_at,
                    work_item.updated_at,
                ),
            )

        # Save children relationships
        self.db.execute(
            "DELETE FROM work_item_children WHERE parent_id = ?", (work_item.id,)
        )
        for child_id in work_item.child_work_item_ids:
            self.db.execute(
                "INSERT INTO work_item_children (parent_id, child_id) VALUES (?, ?)",
                (work_item.id, child_id),
            )

        self.db.commit()

    def find_by_id(self, work_item_id: str) -> Optional[WorkItem]:
        """Find work item by ID."""
        cursor = self.db.execute(
            "SELECT * FROM work_items WHERE id = ?", (work_item_id,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_work_item(row)

    def find_all(self) -> List[WorkItem]:
        """Find all work items."""
        cursor = self.db.execute("SELECT * FROM work_items")
        rows = cursor.fetchall()

        return [self._row_to_work_item(row) for row in rows]

    def find_by_hypothesis(self, hypothesis_id: str) -> List[WorkItem]:
        """Find work items linked to hypothesis."""
        cursor = self.db.execute(
            "SELECT * FROM work_items WHERE parent_hypothesis_id = ?", (hypothesis_id,)
        )
        rows = cursor.fetchall()

        return [self._row_to_work_item(row) for row in rows]

    def find_by_parent(self, parent_id: str) -> List[WorkItem]:
        """Find child work items of parent."""
        cursor = self.db.execute(
            "SELECT * FROM work_items WHERE parent_work_item_id = ?", (parent_id,)
        )
        rows = cursor.fetchall()

        return [self._row_to_work_item(row) for row in rows]

    def find_not_done(self) -> List[WorkItem]:
        """Find work items not in Done stage."""
        cursor = self.db.execute("SELECT * FROM work_items WHERE stage != ?", ("Done",))
        rows = cursor.fetchall()

        return [self._row_to_work_item(row) for row in rows]

    def find_completed_in_period(
        self, start_date: datetime, end_date: datetime
    ) -> List[WorkItem]:
        """Find work items completed in date range."""
        cursor = self.db.execute(
            "SELECT * FROM work_items WHERE stage = ? AND updated_at BETWEEN ? AND ?",
            ("Done", start_date, end_date),
        )
        rows = cursor.fetchall()

        return [self._row_to_work_item(row) for row in rows]

    def _row_to_work_item(self, row) -> WorkItem:
        """Convert database row to WorkItem entity."""
        goals = json.loads(row["goals"])
        acceptance_criteria = json.loads(row["acceptance_criteria"])
        stage = Stage.get_stage_by_name(row["stage"], BoardType.WORK_DELIVERY)
        rigor_level = RigorLevel[row["rigor_level"]]
        effort_level = EffortLevel[row["effort_level"]]
        swimlane = Swimlane[row["swimlane"]]

        # Get children
        cursor = self.db.execute(
            "SELECT child_id FROM work_item_children WHERE parent_id = ?", (row["id"],)
        )
        children_rows = cursor.fetchall()
        child_ids = [child_row["child_id"] for child_row in children_rows]

        return WorkItem(
            id=row["id"],
            title=row["title"],
            goals=goals,
            description=row["description"],
            acceptance_criteria=acceptance_criteria,
            rigor_level=rigor_level,
            effort_level=effort_level,
            assignee=row["assignee"],
            swimlane=swimlane,
            stage=stage,
            parent_hypothesis_id=row["parent_hypothesis_id"],
            parent_work_item_id=row["parent_work_item_id"],
            child_work_item_ids=child_ids,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            stage_transitions=[],
            blocker=None,
            is_invalidated=row["is_invalidated"],
            created_maintenance_burden=row["created_maintenance_burden"],
        )


class FlowHistoryRepository:
    """Repository for flow metrics history."""

    def __init__(self, db_connection: DatabaseConnection):
        """Initialize repository with database connection."""
        self.db = db_connection

    def save_snapshot(self, snapshot_id: str, snapshot_data: dict) -> None:
        """Save metrics snapshot."""
        self.db.execute(
            """
            INSERT INTO flow_metrics_snapshots (
                id, snapshot_date, cycle_time_avg, cycle_time_median,
                cycle_time_p50, cycle_time_p75, cycle_time_p90,
                lead_time_avg, lead_time_median,
                lead_time_p50, lead_time_p75, lead_time_p90,
                throughput_count, throughput_cadence,
                flow_load, flow_debt,
                blocking_age_total, blocking_age_avg, blocking_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                snapshot_id,
                snapshot_data.get("snapshot_date"),
                snapshot_data.get("cycle_time_avg"),
                snapshot_data.get("cycle_time_median"),
                snapshot_data.get("cycle_time_p50"),
                snapshot_data.get("cycle_time_p75"),
                snapshot_data.get("cycle_time_p90"),
                snapshot_data.get("lead_time_avg"),
                snapshot_data.get("lead_time_median"),
                snapshot_data.get("lead_time_p50"),
                snapshot_data.get("lead_time_p75"),
                snapshot_data.get("lead_time_p90"),
                snapshot_data.get("throughput_count"),
                snapshot_data.get("throughput_cadence"),
                snapshot_data.get("flow_load"),
                snapshot_data.get("flow_debt"),
                snapshot_data.get("blocking_age_total"),
                snapshot_data.get("blocking_age_avg"),
                snapshot_data.get("blocking_count"),
            ),
        )
        self.db.commit()

    def find_snapshots_in_period(
        self, start_date: datetime, end_date: datetime
    ) -> List[dict]:
        """Find snapshots in date range."""
        cursor = self.db.execute(
            "SELECT * FROM flow_metrics_snapshots WHERE snapshot_date BETWEEN ? AND ?",
            (start_date, end_date),
        )
        rows = cursor.fetchall()

        return [dict(row) for row in rows]
