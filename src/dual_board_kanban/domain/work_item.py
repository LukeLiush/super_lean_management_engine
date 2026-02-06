"""WorkItem entity for the domain layer."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from dual_board_kanban.domain.value_objects import (
    Stage,
    BoardType,
    RigorLevel,
    EffortLevel,
    Swimlane,
    Blocker,
    StageTransition,
)


@dataclass
class WorkItem:
    """
    Work item entity representing tactical execution.
    Can be an experiment, task, or defect tracked on the Work Board.
    """

    id: str
    title: str
    goals: List[str]
    description: str
    acceptance_criteria: List[str]
    rigor_level: RigorLevel
    effort_level: EffortLevel
    assignee: Optional[str]
    swimlane: Swimlane
    stage: Stage
    parent_hypothesis_id: str
    parent_work_item_id: Optional[str]
    child_work_item_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    stage_transitions: List[StageTransition] = field(default_factory=list)
    blocker: Optional[Blocker] = None
    is_invalidated: bool = False
    created_maintenance_burden: bool = False

    @staticmethod
    def create(
        title: str,
        goals: List[str],
        description: str,
        acceptance_criteria: List[str],
        rigor_level,
        effort_level,
        assignee: Optional[str],
        swimlane,
        parent_hypothesis_id: str,
    ) -> "WorkItem":
        """Create a new work item with initial stage."""
        # Convert string values to enums if needed
        if isinstance(rigor_level, str):
            rigor_level = RigorLevel(rigor_level)
        if isinstance(effort_level, str):
            effort_level = EffortLevel(effort_level)
        if isinstance(swimlane, str):
            swimlane = Swimlane(swimlane)

        now = datetime.utcnow()
        initial_stage = Stage.get_work_delivery_stages()[0]  # Queue

        work_item = WorkItem(
            id=str(uuid4()),
            title=title,
            goals=goals,
            description=description,
            acceptance_criteria=acceptance_criteria,
            rigor_level=rigor_level,
            effort_level=effort_level,
            assignee=assignee,
            swimlane=swimlane,
            stage=initial_stage,
            parent_hypothesis_id=parent_hypothesis_id,
            parent_work_item_id=None,
            child_work_item_ids=[],
            created_at=now,
            updated_at=now,
            stage_transitions=[],
            blocker=None,
            is_invalidated=False,
            created_maintenance_burden=False,
        )

        return work_item

    def move_to_stage(self, new_stage: Stage) -> None:
        """Move work item to a new stage, recording transition."""
        if new_stage.board_type != BoardType.WORK_DELIVERY:
            raise ValueError("Work item can only move to work delivery board stages")

        if not self.stage.is_adjacent_to(new_stage):
            raise ValueError(
                f"Cannot move from {self.stage.name} to {new_stage.name} - stages must be adjacent"
            )

        # Record transition
        transition = StageTransition(
            id=str(uuid4()),
            entity_type="WORK_ITEM",
            entity_id=self.id,
            from_stage=self.stage.name,
            to_stage=new_stage.name,
            transitioned_at=datetime.utcnow(),
        )
        self.stage_transitions.append(transition)

        # Update stage
        self.stage = new_stage
        self.updated_at = datetime.utcnow()

    def is_in_active_stage(self) -> bool:
        """Check if work item is in an active stage."""
        return self.stage.is_active

    def mark_blocked(self, blocker: Blocker) -> None:
        """Mark work item as blocked with blocker details."""
        if not self.is_in_active_stage():
            raise ValueError("Can only block items in active stages")
        self.blocker = blocker
        self.updated_at = datetime.utcnow()

    def unblock(self) -> None:
        """Remove blocked status and record unblock time."""
        if self.blocker:
            self.blocker.unblocked_at = datetime.utcnow()
            self.blocker = None
            self.updated_at = datetime.utcnow()

    def can_have_children(self) -> bool:
        """Check if work item can have children (no parent)."""
        return self.parent_work_item_id is None

    def can_have_parent(self) -> bool:
        """Check if work item can have a parent (no children and no existing parent)."""
        return len(self.child_work_item_ids) == 0 and self.parent_work_item_id is None

    def add_child(self, child_id: str) -> None:
        """Add a child work item."""
        if not self.can_have_children():
            raise ValueError(
                "Cannot add children to a work item that already has children or has a parent"
            )
        if child_id not in self.child_work_item_ids:
            self.child_work_item_ids.append(child_id)
            self.updated_at = datetime.utcnow()

    def remove_child(self, child_id: str) -> None:
        """Remove a child work item."""
        if child_id in self.child_work_item_ids:
            self.child_work_item_ids.remove(child_id)
            self.updated_at = datetime.utcnow()

    def set_parent(self, parent_id: str) -> None:
        """Set parent work item."""
        if not self.can_have_parent():
            raise ValueError("Cannot set parent for a work item that has children")
        self.parent_work_item_id = parent_id
        self.updated_at = datetime.utcnow()

    def clear_parent(self) -> None:
        """Clear parent work item."""
        self.parent_work_item_id = None
        self.updated_at = datetime.utcnow()

    def get_effort_units(self) -> int:
        """Get numeric effort units (High=3, Medium=2, Low=1)."""
        effort_map = {EffortLevel.HIGH: 3, EffortLevel.MEDIUM: 2, EffortLevel.LOW: 1}
        return effort_map.get(self.effort_level, 0)

    def get_child_count(self) -> int:
        """Get count of child work items."""
        return len(self.child_work_item_ids)

    def mark_invalidated(self, created_maintenance_burden: bool = False) -> None:
        """Mark work item as invalidated."""
        self.is_invalidated = True
        self.created_maintenance_burden = created_maintenance_burden
        self.updated_at = datetime.utcnow()
