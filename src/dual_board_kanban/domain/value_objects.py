"""Value objects for the domain layer."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from datetime import datetime, timedelta


class BoardType(Enum):
    """Type of board."""

    STRATEGIC = "STRATEGIC"
    WORK_DELIVERY = "WORK_DELIVERY"


class RigorLevel(Enum):
    """Rigor level for work items."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class EffortLevel(Enum):
    """Effort level for work items."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Swimlane(Enum):
    """Swimlane categories for work items."""

    STRATEGIC_EXPERIMENTS = "STRATEGIC_EXPERIMENTS"
    TACTICAL_DEBT = "TACTICAL_DEBT"
    DEFECTS_SUPPORT = "DEFECTS_SUPPORT"


class BlockerSeverity(Enum):
    """Severity level for blockers."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True)
class Stage:
    """
    Value object representing a workflow stage.
    Immutable and comparable.
    """

    name: str
    board_type: BoardType
    is_active: bool
    order: int

    def __eq__(self, other):
        """Check equality by name and board type."""
        if not isinstance(other, Stage):
            return False
        return self.name == other.name and self.board_type == other.board_type

    def __hash__(self):
        """Hash by name and board type."""
        return hash((self.name, self.board_type))

    @staticmethod
    def get_strategic_stages() -> List["Stage"]:
        """Get ordered list of strategic board stages."""
        return [
            Stage("In Queue", BoardType.STRATEGIC, False, 0),
            Stage("Review", BoardType.STRATEGIC, False, 1),
            Stage("Execution", BoardType.STRATEGIC, True, 2),
            Stage("Done", BoardType.STRATEGIC, False, 3),
        ]

    @staticmethod
    def get_work_delivery_stages() -> List["Stage"]:
        """Get ordered list of work delivery board stages."""
        return [
            Stage("Queue", BoardType.WORK_DELIVERY, False, 0),
            Stage("Design", BoardType.WORK_DELIVERY, True, 1),
            Stage("Design-Review", BoardType.WORK_DELIVERY, True, 2),
            Stage("Implementation", BoardType.WORK_DELIVERY, True, 3),
            Stage("CR-Review", BoardType.WORK_DELIVERY, True, 4),
            Stage("Deploy", BoardType.WORK_DELIVERY, True, 5),
            Stage("Release", BoardType.WORK_DELIVERY, True, 6),
            Stage("Done", BoardType.WORK_DELIVERY, False, 7),
        ]

    def is_adjacent_to(self, other: "Stage") -> bool:
        """
        Check if this stage is adjacent to another stage.
        Adjacent means they are in the same board and differ by exactly 1 in order.
        """
        if self.board_type != other.board_type:
            return False
        return abs(self.order - other.order) == 1

    @staticmethod
    def get_stage_by_name(name: str, board_type: BoardType) -> "Stage":
        """Get stage by name and board type."""
        if board_type == BoardType.STRATEGIC:
            stages = Stage.get_strategic_stages()
        else:
            stages = Stage.get_work_delivery_stages()

        for stage in stages:
            if stage.name == name:
                return stage

        raise ValueError(f"Stage '{name}' not found for board type {board_type}")


@dataclass
class StageTransition:
    """Record of a stage transition."""

    id: str
    entity_type: str  # HYPOTHESIS or WORK_ITEM
    entity_id: str
    from_stage: str
    to_stage: str
    transitioned_at: datetime


@dataclass
class Blocker:
    """
    Value object representing a blocking impediment.
    """

    id: str
    blocker_type: str
    severity: BlockerSeverity
    owner: str
    reason: str
    blocked_at: datetime
    unblocked_at: Optional[datetime] = None

    def get_blocking_duration(self) -> timedelta:
        """Calculate duration of blocking."""
        end_time = self.unblocked_at if self.unblocked_at else datetime.utcnow()
        return end_time - self.blocked_at

    def is_currently_blocked(self) -> bool:
        """Check if currently blocked."""
        return self.unblocked_at is None
