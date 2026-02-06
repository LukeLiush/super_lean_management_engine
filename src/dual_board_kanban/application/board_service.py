"""Board service for managing board operations."""

from dataclasses import dataclass
from typing import List, Dict
from dual_board_kanban.domain.value_objects import Stage, BoardType
from dual_board_kanban.infrastructure.repositories import (
    HypothesisRepository,
    WorkItemRepository,
)


@dataclass
class CardView:
    """View model for a card on the board."""

    id: str
    title: str
    stage: str
    is_blocked: bool
    child_count: int = 0


@dataclass
class StrategicBoardView:
    """View model for strategic board."""

    stages: List[str]
    cards_by_stage: Dict[str, List[CardView]]


@dataclass
class WorkDeliveryBoardView:
    """View model for work delivery board."""

    stages: List[str]
    swimlanes: List[str]
    cards_by_swimlane_and_stage: Dict[str, Dict[str, List[CardView]]]
    flow_load: int
    flow_debt: int


class BoardService:
    """Application service for board operations."""

    def __init__(
        self, hypothesis_repo: HypothesisRepository, work_item_repo: WorkItemRepository
    ):
        """Initialize board service with repositories."""
        self.hypothesis_repo = hypothesis_repo
        self.work_item_repo = work_item_repo

    def get_strategic_board(self) -> StrategicBoardView:
        """Get strategic board with all hypotheses."""
        hypotheses = self.hypothesis_repo.find_all()
        stages = [stage.name for stage in Stage.get_strategic_stages()]

        # Group hypotheses by stage
        cards_by_stage: Dict[str, List[CardView]] = {stage: [] for stage in stages}

        for hypothesis in hypotheses:
            card = CardView(
                id=hypothesis.id,
                title=hypothesis.hypothesis_statement[:50],  # Truncate for display
                stage=hypothesis.stage.name,
                is_blocked=hypothesis.blocker is not None,
                child_count=0,  # Hypotheses don't have children
            )
            cards_by_stage[hypothesis.stage.name].append(card)

        return StrategicBoardView(stages=stages, cards_by_stage=cards_by_stage)

    def get_work_delivery_board(self) -> WorkDeliveryBoardView:
        """Get work delivery board with all work items."""
        work_items = self.work_item_repo.find_all()
        stages = [stage.name for stage in Stage.get_work_delivery_stages()]
        swimlanes = ["STRATEGIC_EXPERIMENTS", "TACTICAL_DEBT", "DEFECTS_SUPPORT"]

        # Group work items by swimlane and stage
        cards_by_swimlane_and_stage: Dict[str, Dict[str, List[CardView]]] = {}
        for swimlane in swimlanes:
            cards_by_swimlane_and_stage[swimlane] = {stage: [] for stage in stages}

        for work_item in work_items:
            card = CardView(
                id=work_item.id,
                title=work_item.title,
                stage=work_item.stage.name,
                is_blocked=work_item.blocker is not None,
                child_count=work_item.get_child_count(),
            )
            swimlane_key = work_item.swimlane.value
            cards_by_swimlane_and_stage[swimlane_key][work_item.stage.name].append(card)

        # Calculate flow load and flow debt
        flow_load = sum(
            wi.get_effort_units() for wi in work_items if wi.stage.name != "Done"
        )
        flow_debt = sum(
            1
            for wi in work_items
            if wi.is_invalidated and wi.created_maintenance_burden
        )

        return WorkDeliveryBoardView(
            stages=stages,
            swimlanes=swimlanes,
            cards_by_swimlane_and_stage=cards_by_swimlane_and_stage,
            flow_load=flow_load,
            flow_debt=flow_debt,
        )

    def move_hypothesis(self, hypothesis_id: str, target_stage_name: str) -> None:
        """Move hypothesis to target stage."""
        hypothesis = self.hypothesis_repo.find_by_id(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")

        target_stage = Stage.get_stage_by_name(target_stage_name, BoardType.STRATEGIC)

        # Validate adjacency
        if not hypothesis.stage.is_adjacent_to(target_stage):
            raise ValueError(
                f"Cannot move from {hypothesis.stage.name} to {target_stage_name}"
            )

        hypothesis.move_to_stage(target_stage)
        self.hypothesis_repo.save(hypothesis)

    def move_work_item(self, work_item_id: str, target_stage_name: str) -> None:
        """Move work item to target stage, check parent completion."""
        work_item = self.work_item_repo.find_by_id(work_item_id)
        if not work_item:
            raise ValueError(f"Work item {work_item_id} not found")

        target_stage = Stage.get_stage_by_name(
            target_stage_name, BoardType.WORK_DELIVERY
        )

        # Validate adjacency
        if not work_item.stage.is_adjacent_to(target_stage):
            raise ValueError(
                f"Cannot move from {work_item.stage.name} to {target_stage_name}"
            )

        work_item.move_to_stage(target_stage)
        self.work_item_repo.save(work_item)

        # Check if parent needs to be updated
        if work_item.parent_work_item_id:
            self._update_parent_stage(work_item.parent_work_item_id)

    def _update_parent_stage(self, parent_id: str) -> None:
        """Update parent work item stage based on children."""
        parent = self.work_item_repo.find_by_id(parent_id)
        if not parent:
            return

        children = self.work_item_repo.find_by_parent(parent_id)

        if not children:
            return

        # Check if all children are in Done
        all_done = all(child.stage.name == "Done" for child in children)
        if all_done:
            # Move parent to Done if not already
            if parent.stage.name != "Done":
                # Move through adjacent stages to reach Done
                while parent.stage.name != "Done":
                    stages = Stage.get_work_delivery_stages()
                    current_order = parent.stage.order
                    next_stage = next(s for s in stages if s.order == current_order + 1)
                    parent.move_to_stage(next_stage)
                self.work_item_repo.save(parent)
        else:
            # Check if any child is in Implementation
            any_implementation = any(
                child.stage.name == "Implementation" for child in children
            )
            if any_implementation and parent.stage.name not in [
                "Implementation",
                "Done",
            ]:
                # Move parent to Implementation if not already there or beyond
                impl_stage = Stage.get_stage_by_name(
                    "Implementation", BoardType.WORK_DELIVERY
                )
                # Move through adjacent stages to reach Implementation
                while parent.stage.order < impl_stage.order:
                    stages = Stage.get_work_delivery_stages()
                    current_order = parent.stage.order
                    next_stage = next(s for s in stages if s.order == current_order + 1)
                    parent.move_to_stage(next_stage)
                self.work_item_repo.save(parent)
