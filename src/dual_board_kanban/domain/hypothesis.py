"""Hypothesis entity for the domain layer."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from uuid import uuid4
from dual_board_kanban.domain.value_objects import (
    Stage,
    BoardType,
    Blocker,
    StageTransition,
)


@dataclass
class Hypothesis:
    """
    Strategic hypothesis entity with validation canvas.
    Represents a strategic assumption to be validated through experiments.
    """

    id: str
    business_value: str
    problem_statement: str
    customers_impacted: str
    hypothesis_statement: str  # Format: "We believe that [X] will result in [Y]. We will know we've succeeded when [Z]."
    metrics_baseline: str
    solutions_ideas: List[str]
    lessons_learned: str
    stage: Stage
    created_at: datetime
    updated_at: datetime
    stage_transitions: List[StageTransition] = field(default_factory=list)
    blocker: Optional[Blocker] = None

    @staticmethod
    def create(
        business_value: str,
        problem_statement: str,
        customers_impacted: str,
        hypothesis_statement: str,
        metrics_baseline: str,
        solutions_ideas: List[str],
        lessons_learned: str = "",
    ) -> "Hypothesis":
        """Create a new hypothesis with initial stage."""
        now = datetime.utcnow()
        initial_stage = Stage.get_strategic_stages()[0]  # In Queue

        hypothesis = Hypothesis(
            id=str(uuid4()),
            business_value=business_value,
            problem_statement=problem_statement,
            customers_impacted=customers_impacted,
            hypothesis_statement=hypothesis_statement,
            metrics_baseline=metrics_baseline,
            solutions_ideas=solutions_ideas,
            lessons_learned=lessons_learned,
            stage=initial_stage,
            created_at=now,
            updated_at=now,
            stage_transitions=[],
            blocker=None,
        )

        return hypothesis

    def move_to_stage(self, new_stage: Stage) -> None:
        """Move hypothesis to a new stage, recording transition."""
        if new_stage.board_type != BoardType.STRATEGIC:
            raise ValueError("Hypothesis can only move to strategic board stages")

        if not self.stage.is_adjacent_to(new_stage):
            raise ValueError(
                f"Cannot move from {self.stage.name} to {new_stage.name} - stages must be adjacent"
            )

        # Record transition
        transition = StageTransition(
            id=str(uuid4()),
            entity_type="HYPOTHESIS",
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
        """Check if hypothesis is in an active stage (Execution)."""
        return self.stage.is_active

    def get_linked_work_items_summary(self) -> Dict[str, Dict[str, int]]:
        """
        Get count of linked work items by rigor and effort level.
        This will be populated by the application layer when retrieving hypothesis details.
        """
        return {
            "HIGH": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "MEDIUM": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "LOW": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
        }

    def mark_blocked(self, blocker: Blocker) -> None:
        """Mark hypothesis as blocked with blocker details."""
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
