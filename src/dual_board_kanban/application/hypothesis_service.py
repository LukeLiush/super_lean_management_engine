"""Hypothesis service for managing hypothesis operations."""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
from dual_board_kanban.domain.hypothesis import Hypothesis
from dual_board_kanban.domain.value_objects import Blocker, BlockerSeverity
from dual_board_kanban.infrastructure.repositories import (
    HypothesisRepository,
    WorkItemRepository,
)


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
    linked_work_items_count: int
    created_at: datetime
    updated_at: datetime


class HypothesisService:
    """Application service for hypothesis operations."""

    def __init__(
        self, hypothesis_repo: HypothesisRepository, work_item_repo: WorkItemRepository
    ):
        """Initialize hypothesis service with repositories."""
        self.hypothesis_repo = hypothesis_repo
        self.work_item_repo = work_item_repo

    def create_hypothesis(
        self,
        business_value: str,
        problem_statement: str,
        customers_impacted: str,
        hypothesis_statement: str,
        metrics_baseline: str,
        solutions_ideas: List[str],
        lessons_learned: str = "",
    ) -> str:
        """Create new hypothesis with canvas data."""
        # Validate hypothesis statement format
        self._validate_hypothesis_statement(hypothesis_statement)

        hypothesis = Hypothesis.create(
            business_value=business_value,
            problem_statement=problem_statement,
            customers_impacted=customers_impacted,
            hypothesis_statement=hypothesis_statement,
            metrics_baseline=metrics_baseline,
            solutions_ideas=solutions_ideas,
            lessons_learned=lessons_learned,
        )

        self.hypothesis_repo.save(hypothesis)
        return hypothesis.id

    def update_hypothesis(
        self,
        hypothesis_id: str,
        business_value: str,
        problem_statement: str,
        customers_impacted: str,
        hypothesis_statement: str,
        metrics_baseline: str,
        solutions_ideas: List[str],
        lessons_learned: str = "",
    ) -> None:
        """Update hypothesis canvas data."""
        hypothesis = self.hypothesis_repo.find_by_id(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")

        # Validate hypothesis statement format
        self._validate_hypothesis_statement(hypothesis_statement)

        hypothesis.business_value = business_value
        hypothesis.problem_statement = problem_statement
        hypothesis.customers_impacted = customers_impacted
        hypothesis.hypothesis_statement = hypothesis_statement
        hypothesis.metrics_baseline = metrics_baseline
        hypothesis.solutions_ideas = solutions_ideas
        hypothesis.lessons_learned = lessons_learned
        hypothesis.updated_at = datetime.utcnow()

        self.hypothesis_repo.save(hypothesis)

    def get_hypothesis_details(self, hypothesis_id: str) -> HypothesisDetailView:
        """Get hypothesis details with linked work items."""
        hypothesis = self.hypothesis_repo.find_by_id(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")

        # Get linked work items
        linked_work_items = self.work_item_repo.find_by_hypothesis(hypothesis_id)

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
            linked_work_items_count=len(linked_work_items),
            created_at=hypothesis.created_at,
            updated_at=hypothesis.updated_at,
        )

    def get_linked_work_items_summary(
        self, hypothesis_id: str
    ) -> Dict[str, Dict[str, int]]:
        """Get work items summary by rigor and effort level."""
        linked_work_items = self.work_item_repo.find_by_hypothesis(hypothesis_id)

        summary = {
            "HIGH": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "MEDIUM": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "LOW": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
        }

        for work_item in linked_work_items:
            rigor = work_item.rigor_level.value
            effort = work_item.effort_level.value
            summary[rigor][effort] += 1

        return summary

    def mark_blocked(
        self,
        hypothesis_id: str,
        blocker_type: str,
        severity: str,
        owner: str,
        reason: str,
    ) -> None:
        """Mark hypothesis as blocked."""
        hypothesis = self.hypothesis_repo.find_by_id(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")

        if not hypothesis.is_in_active_stage():
            raise ValueError("Can only block items in active stages")

        blocker = Blocker(
            id=f"blocker_{hypothesis_id}",
            blocker_type=blocker_type,
            severity=BlockerSeverity[severity],
            owner=owner,
            reason=reason,
            blocked_at=datetime.utcnow(),
        )

        hypothesis.mark_blocked(blocker)
        self.hypothesis_repo.save(hypothesis)

    def unblock(self, hypothesis_id: str) -> None:
        """Unblock hypothesis."""
        hypothesis = self.hypothesis_repo.find_by_id(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")

        hypothesis.unblock()
        self.hypothesis_repo.save(hypothesis)

    def _validate_hypothesis_statement(self, statement: str) -> None:
        """Validate hypothesis statement format."""
        # Format: "We believe that [X] will result in [Y]. We will know we've succeeded when [Z]."
        pattern = r"We believe that .+ will result in .+\. We will know we've succeeded when .+\."
        if not re.match(pattern, statement):
            raise ValueError(
                "Hypothesis statement must follow format: "
                "'We believe that [X] will result in [Y]. We will know we've succeeded when [Z].'"
            )
