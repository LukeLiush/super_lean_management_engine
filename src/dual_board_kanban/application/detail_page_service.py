"""Detail page service for managing detail page operations."""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from datetime import datetime
from dual_board_kanban.infrastructure.repositories import (
    HypothesisRepository,
    WorkItemRepository,
)


@dataclass
class BreadcrumbItem:
    """Item in breadcrumb navigation."""

    id: str
    title: str
    item_type: str  # BOARD, HYPOTHESIS, WORK_ITEM


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
    parent_hypothesis_title: Optional[str]
    parent_work_item_id: Optional[str]
    parent_work_item_title: Optional[str]
    child_work_item_ids: List[str]
    child_work_item_titles: List[str]
    is_blocked: bool
    blocker_info: Optional[dict]
    is_invalidated: bool
    created_maintenance_burden: bool
    created_at: datetime
    updated_at: datetime
    breadcrumb_path: List[BreadcrumbItem]
    previous_sibling_id: Optional[str]
    next_sibling_id: Optional[str]


@dataclass
class HypothesisDetailView:
    """View model for hypothesis detail page."""

    id: str
    business_value: str
    problem_statement: str
    customers_impacted: str
    hypothesis_statement: str
    metrics_baseline: str
    solutions_ideas: List[str]
    lessons_learned: str
    stage: str
    is_blocked: bool
    blocker_info: Optional[dict]
    linked_work_item_ids: List[str]
    linked_work_item_titles: List[str]
    created_at: datetime
    updated_at: datetime
    breadcrumb_path: List[BreadcrumbItem]


class DetailPageService:
    """Application service for detail page operations."""

    def __init__(
        self, hypothesis_repo: HypothesisRepository, work_item_repo: WorkItemRepository
    ):
        """Initialize detail page service with repositories."""
        self.hypothesis_repo = hypothesis_repo
        self.work_item_repo = work_item_repo

    def get_work_item_detail(
        self, work_item_id: str, navigation_history: Optional[List[str]] = None
    ) -> WorkItemDetailView:
        """Get work item detail view with all relationships and navigation data."""
        work_item = self.work_item_repo.find_by_id(work_item_id)
        if not work_item:
            raise ValueError(f"Work item {work_item_id} not found")

        # Get parent hypothesis
        parent_hypothesis = self.hypothesis_repo.find_by_id(
            work_item.parent_hypothesis_id
        )
        parent_hypothesis_title = (
            parent_hypothesis.hypothesis_statement[:50] if parent_hypothesis else None
        )

        # Get parent work item
        parent_work_item = None
        parent_work_item_title = None
        if work_item.parent_work_item_id:
            parent_work_item = self.work_item_repo.find_by_id(
                work_item.parent_work_item_id
            )
            parent_work_item_title = (
                parent_work_item.title if parent_work_item else None
            )

        # Get child work items
        child_work_items = self.work_item_repo.find_by_parent(work_item_id)
        child_titles = [child.title for child in child_work_items]

        # Get blocker info
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

        # Get breadcrumb path
        breadcrumb_path = self._get_breadcrumb_path(
            work_item_id, "WORK_ITEM", navigation_history or []
        )

        # Get sibling navigation
        previous_sibling_id, next_sibling_id = self._get_sibling_navigation(
            work_item_id
        )

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
            parent_hypothesis_title=parent_hypothesis_title,
            parent_work_item_id=work_item.parent_work_item_id,
            parent_work_item_title=parent_work_item_title,
            child_work_item_ids=work_item.child_work_item_ids,
            child_work_item_titles=child_titles,
            is_blocked=work_item.blocker is not None,
            blocker_info=blocker_info,
            is_invalidated=work_item.is_invalidated,
            created_maintenance_burden=work_item.created_maintenance_burden,
            created_at=work_item.created_at,
            updated_at=work_item.updated_at,
            breadcrumb_path=breadcrumb_path,
            previous_sibling_id=previous_sibling_id,
            next_sibling_id=next_sibling_id,
        )

    def get_hypothesis_detail(
        self, hypothesis_id: str, navigation_history: Optional[List[str]] = None
    ) -> HypothesisDetailView:
        """Get hypothesis detail view with all relationships and navigation data."""
        hypothesis = self.hypothesis_repo.find_by_id(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")

        # Get linked work items
        linked_work_items = self.work_item_repo.find_by_hypothesis(hypothesis_id)
        linked_titles = [wi.title for wi in linked_work_items]

        # Get blocker info
        blocker_info = None
        if hypothesis.blocker:
            blocker_info = {
                "type": hypothesis.blocker.blocker_type,
                "severity": hypothesis.blocker.severity.value,
                "owner": hypothesis.blocker.owner,
                "reason": hypothesis.blocker.reason,
                "blocked_at": hypothesis.blocker.blocked_at.isoformat(),
                "unblocked_at": hypothesis.blocker.unblocked_at.isoformat()
                if hypothesis.blocker.unblocked_at
                else None,
            }

        # Get breadcrumb path
        breadcrumb_path = self._get_breadcrumb_path(
            hypothesis_id, "HYPOTHESIS", navigation_history or []
        )

        return HypothesisDetailView(
            id=hypothesis.id,
            business_value=hypothesis.business_value,
            problem_statement=hypothesis.problem_statement,
            customers_impacted=hypothesis.customers_impacted,
            hypothesis_statement=hypothesis.hypothesis_statement,
            metrics_baseline=hypothesis.metrics_baseline,
            solutions_ideas=hypothesis.solutions_ideas,
            lessons_learned=hypothesis.lessons_learned,
            stage=hypothesis.stage.name,
            is_blocked=hypothesis.blocker is not None,
            blocker_info=blocker_info,
            linked_work_item_ids=[wi.id for wi in linked_work_items],
            linked_work_item_titles=linked_titles,
            created_at=hypothesis.created_at,
            updated_at=hypothesis.updated_at,
            breadcrumb_path=breadcrumb_path,
        )

    def _get_breadcrumb_path(
        self, item_id: str, item_type: str, navigation_history: List[str]
    ) -> List[BreadcrumbItem]:
        """Get breadcrumb navigation path."""
        breadcrumb = [BreadcrumbItem(id="board", title="Board", item_type="BOARD")]

        # Add items from navigation history
        for hist_id in navigation_history:
            # Try to find as work item first
            work_item = self.work_item_repo.find_by_id(hist_id)
            if work_item:
                breadcrumb.append(
                    BreadcrumbItem(
                        id=hist_id, title=work_item.title, item_type="WORK_ITEM"
                    )
                )
            else:
                # Try as hypothesis
                hypothesis = self.hypothesis_repo.find_by_id(hist_id)
                if hypothesis:
                    breadcrumb.append(
                        BreadcrumbItem(
                            id=hist_id,
                            title=hypothesis.hypothesis_statement[:50],
                            item_type="HYPOTHESIS",
                        )
                    )

        # Add current item
        if item_type == "WORK_ITEM":
            work_item = self.work_item_repo.find_by_id(item_id)
            if work_item:
                breadcrumb.append(
                    BreadcrumbItem(
                        id=item_id, title=work_item.title, item_type="WORK_ITEM"
                    )
                )
        else:
            hypothesis = self.hypothesis_repo.find_by_id(item_id)
            if hypothesis:
                breadcrumb.append(
                    BreadcrumbItem(
                        id=item_id,
                        title=hypothesis.hypothesis_statement[:50],
                        item_type="HYPOTHESIS",
                    )
                )

        return breadcrumb

    def _get_sibling_navigation(
        self, work_item_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Get previous and next sibling IDs for navigation."""
        work_item = self.work_item_repo.find_by_id(work_item_id)
        if not work_item or not work_item.parent_work_item_id:
            return None, None

        # Get all siblings
        siblings = self.work_item_repo.find_by_parent(work_item.parent_work_item_id)
        sibling_ids = [s.id for s in siblings]

        if work_item_id not in sibling_ids:
            return None, None

        current_index = sibling_ids.index(work_item_id)
        previous_id = sibling_ids[current_index - 1] if current_index > 0 else None
        next_id = (
            sibling_ids[current_index + 1]
            if current_index < len(sibling_ids) - 1
            else None
        )

        return previous_id, next_id
