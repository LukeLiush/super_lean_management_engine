"""Work item service for managing work item operations."""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from dual_board_kanban.domain.work_item import WorkItem
from dual_board_kanban.domain.value_objects import (
    RigorLevel,
    EffortLevel,
    Swimlane,
    Blocker,
    BlockerSeverity,
)
from dual_board_kanban.infrastructure.repositories import (
    HypothesisRepository,
    WorkItemRepository,
)


@dataclass
class WorkItemDetailView:
    """View model for work item detail page."""

    id: str
    title: str
    goals: List[str]
    description: str
    acceptance_criteria: List[str]
    rigor_level: str
    effort_level: str
    assignee: Optional[str]
    swimlane: str
    stage: str
    parent_hypothesis_id: str
    parent_work_item_id: Optional[str]
    child_work_item_ids: List[str]
    is_blocked: bool
    blocker_info: Optional[dict]
    is_invalidated: bool
    created_maintenance_burden: bool
    created_at: datetime
    updated_at: datetime


class WorkItemService:
    """Application service for work item operations."""

    def __init__(
        self, hypothesis_repo: HypothesisRepository, work_item_repo: WorkItemRepository
    ):
        """Initialize work item service with repositories."""
        self.hypothesis_repo = hypothesis_repo
        self.work_item_repo = work_item_repo

    def create_work_item(
        self,
        title: str,
        goals: List[str],
        description: str,
        acceptance_criteria: List[str],
        rigor_level: str,
        effort_level: str,
        assignee: Optional[str],
        swimlane: str,
        parent_hypothesis_id: str,
    ) -> str:
        """Create new work item."""
        # Validate parent hypothesis exists
        hypothesis = self.hypothesis_repo.find_by_id(parent_hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Parent hypothesis {parent_hypothesis_id} not found")

        work_item = WorkItem.create(
            title=title,
            goals=goals,
            description=description,
            acceptance_criteria=acceptance_criteria,
            rigor_level=RigorLevel[rigor_level],
            effort_level=EffortLevel[effort_level],
            assignee=assignee,
            swimlane=Swimlane[swimlane],
            parent_hypothesis_id=parent_hypothesis_id,
        )

        self.work_item_repo.save(work_item)
        return work_item.id

    def update_work_item(
        self,
        work_item_id: str,
        title: str,
        goals: List[str],
        description: str,
        acceptance_criteria: List[str],
        rigor_level: str,
        effort_level: str,
        assignee: Optional[str],
    ) -> None:
        """Update work item data."""
        work_item = self.work_item_repo.find_by_id(work_item_id)
        if not work_item:
            raise ValueError(f"Work item {work_item_id} not found")

        work_item.title = title
        work_item.goals = goals
        work_item.description = description
        work_item.acceptance_criteria = acceptance_criteria
        work_item.rigor_level = RigorLevel[rigor_level]
        work_item.effort_level = EffortLevel[effort_level]
        work_item.assignee = assignee
        work_item.updated_at = datetime.utcnow()

        self.work_item_repo.save(work_item)

    def get_work_item_details(self, work_item_id: str) -> WorkItemDetailView:
        """Get work item details."""
        work_item = self.work_item_repo.find_by_id(work_item_id)
        if not work_item:
            raise ValueError(f"Work item {work_item_id} not found")

        blocker_info = None
        if work_item.blocker:
            blocker_info = {
                "type": work_item.blocker.blocker_type,
                "severity": work_item.blocker.severity.value,
                "owner": work_item.blocker.owner,
                "reason": work_item.blocker.reason,
                "blocked_at": work_item.blocker.blocked_at.isoformat(),
                "unblocked_at": work_item.blocker.unblocked_at.isoformat()
                if work_item.blocker.unblocked_at
                else None,
            }

        return WorkItemDetailView(
            id=work_item.id,
            title=work_item.title,
            goals=work_item.goals,
            description=work_item.description,
            acceptance_criteria=work_item.acceptance_criteria,
            rigor_level=work_item.rigor_level.value,
            effort_level=work_item.effort_level.value,
            assignee=work_item.assignee,
            swimlane=work_item.swimlane.value,
            stage=work_item.stage.name,
            parent_hypothesis_id=work_item.parent_hypothesis_id,
            parent_work_item_id=work_item.parent_work_item_id,
            child_work_item_ids=work_item.child_work_item_ids,
            is_blocked=work_item.blocker is not None,
            blocker_info=blocker_info,
            is_invalidated=work_item.is_invalidated,
            created_maintenance_burden=work_item.created_maintenance_burden,
            created_at=work_item.created_at,
            updated_at=work_item.updated_at,
        )

    def mark_blocked(
        self,
        work_item_id: str,
        blocker_type: str,
        severity: str,
        owner: str,
        reason: str,
    ) -> None:
        """Mark work item as blocked."""
        work_item = self.work_item_repo.find_by_id(work_item_id)
        if not work_item:
            raise ValueError(f"Work item {work_item_id} not found")

        if not work_item.is_in_active_stage():
            raise ValueError("Can only block items in active stages")

        blocker = Blocker(
            id=f"blocker_{work_item_id}",
            blocker_type=blocker_type,
            severity=BlockerSeverity[severity],
            owner=owner,
            reason=reason,
            blocked_at=datetime.utcnow(),
        )

        work_item.mark_blocked(blocker)
        self.work_item_repo.save(work_item)

    def unblock(self, work_item_id: str) -> None:
        """Unblock work item."""
        work_item = self.work_item_repo.find_by_id(work_item_id)
        if not work_item:
            raise ValueError(f"Work item {work_item_id} not found")

        work_item.unblock()
        self.work_item_repo.save(work_item)

    def add_child_work_item(self, parent_id: str, child_id: str) -> None:
        """Add child work item to parent."""
        parent = self.work_item_repo.find_by_id(parent_id)
        if not parent:
            raise ValueError(f"Parent work item {parent_id} not found")

        child = self.work_item_repo.find_by_id(child_id)
        if not child:
            raise ValueError(f"Child work item {child_id} not found")

        if not parent.can_have_children():
            raise ValueError("Parent work item already has a parent")

        if not child.can_have_parent():
            raise ValueError("Child work item already has children")

        parent.add_child(child_id)
        child.set_parent(parent_id)

        self.work_item_repo.save(parent)
        self.work_item_repo.save(child)

    def remove_child_work_item(self, parent_id: str, child_id: str) -> None:
        """Remove child work item from parent."""
        parent = self.work_item_repo.find_by_id(parent_id)
        if not parent:
            raise ValueError(f"Parent work item {parent_id} not found")

        child = self.work_item_repo.find_by_id(child_id)
        if not child:
            raise ValueError(f"Child work item {child_id} not found")

        parent.remove_child(child_id)
        child.clear_parent()

        self.work_item_repo.save(parent)
        self.work_item_repo.save(child)

    def mark_invalidated(
        self, work_item_id: str, created_maintenance_burden: bool = False
    ) -> None:
        """Mark work item as invalidated."""
        work_item = self.work_item_repo.find_by_id(work_item_id)
        if not work_item:
            raise ValueError(f"Work item {work_item_id} not found")

        work_item.mark_invalidated(created_maintenance_burden)
        self.work_item_repo.save(work_item)
