"""Unit tests for domain entities."""

import pytest
from datetime import datetime
from dual_board_kanban.domain.work_item import WorkItem
from dual_board_kanban.domain.hypothesis import Hypothesis
from dual_board_kanban.domain.value_objects import (
    Stage,
    BoardType,
    Blocker,
    BlockerSeverity,
)


class TestStageValueObject:
    """Tests for Stage value object."""

    def test_stage_creation(self):
        """Test creating a stage."""
        stage = Stage("In Queue", BoardType.STRATEGIC, False, 0)
        assert stage.name == "In Queue"
        assert stage.board_type == BoardType.STRATEGIC
        assert not stage.is_active
        assert stage.order == 0

    def test_get_strategic_stages(self):
        """Test getting strategic board stages."""
        stages = Stage.get_strategic_stages()
        assert len(stages) == 4
        assert stages[0].name == "In Queue"
        assert stages[1].name == "Review"
        assert stages[2].name == "Execution"
        assert stages[3].name == "Done"

    def test_get_work_delivery_stages(self):
        """Test getting work delivery board stages."""
        stages = Stage.get_work_delivery_stages()
        assert len(stages) == 8
        assert stages[0].name == "Queue"
        assert stages[-1].name == "Done"

    def test_is_adjacent_to(self):
        """Test stage adjacency check."""
        stages = Stage.get_strategic_stages()
        assert stages[0].is_adjacent_to(stages[1])
        assert not stages[0].is_adjacent_to(stages[2])
        assert not stages[0].is_adjacent_to(stages[3])

    def test_stage_equality(self):
        """Test stage equality."""
        stage1 = Stage("In Queue", BoardType.STRATEGIC, False, 0)
        stage2 = Stage("In Queue", BoardType.STRATEGIC, False, 0)
        assert stage1 == stage2


class TestHypothesisEntity:
    """Tests for Hypothesis entity."""

    def test_hypothesis_creation(self, sample_hypothesis_data):
        """Test creating a hypothesis."""
        hypothesis = Hypothesis.create(**sample_hypothesis_data)

        assert hypothesis.id is not None
        assert hypothesis.business_value == sample_hypothesis_data["business_value"]
        assert hypothesis.stage.name == "In Queue"
        assert hypothesis.created_at is not None

    def test_hypothesis_move_to_stage(self, sample_hypothesis_data):
        """Test moving hypothesis between stages."""
        hypothesis = Hypothesis.create(**sample_hypothesis_data)

        review_stage = Stage.get_strategic_stages()[1]
        hypothesis.move_to_stage(review_stage)

        assert hypothesis.stage == review_stage
        assert len(hypothesis.stage_transitions) == 1

    def test_hypothesis_invalid_stage_transition(self, sample_hypothesis_data):
        """Test invalid stage transition."""
        hypothesis = Hypothesis.create(**sample_hypothesis_data)

        done_stage = Stage.get_strategic_stages()[3]
        with pytest.raises(ValueError):
            hypothesis.move_to_stage(done_stage)

    def test_hypothesis_is_in_active_stage(self, sample_hypothesis_data):
        """Test checking if hypothesis is in active stage."""
        hypothesis = Hypothesis.create(**sample_hypothesis_data)
        assert not hypothesis.is_in_active_stage()

        execution_stage = Stage.get_strategic_stages()[2]
        hypothesis.move_to_stage(Stage.get_strategic_stages()[1])
        hypothesis.move_to_stage(execution_stage)
        assert hypothesis.is_in_active_stage()


class TestWorkItemEntity:
    """Tests for WorkItem entity."""

    def test_work_item_creation(self, sample_work_item_data):
        """Test creating a work item."""
        work_item = WorkItem.create(
            **sample_work_item_data, parent_hypothesis_id="hyp-123"
        )

        assert work_item.id is not None
        assert work_item.title == sample_work_item_data["title"]
        assert work_item.stage.name == "Queue"
        assert work_item.parent_hypothesis_id == "hyp-123"

    def test_work_item_effort_units(self, sample_work_item_data):
        """Test effort unit calculation."""
        work_item = WorkItem.create(
            **sample_work_item_data, parent_hypothesis_id="hyp-123"
        )

        assert work_item.get_effort_units() == 2  # MEDIUM = 2

    def test_work_item_parent_child_relationship(self, sample_work_item_data):
        """Test parent-child relationships."""
        parent = WorkItem.create(
            **sample_work_item_data, parent_hypothesis_id="hyp-123"
        )

        child = WorkItem.create(**sample_work_item_data, parent_hypothesis_id="hyp-123")

        assert parent.can_have_children()
        assert child.can_have_parent()

        parent.add_child(child.id)
        child.set_parent(parent.id)

        # Parent can still have more children (multiple children allowed)
        assert parent.can_have_children()
        # Child cannot have more parents or children
        assert not child.can_have_parent()
        assert parent.get_child_count() == 1

    def test_work_item_cannot_have_both_parent_and_children(
        self, sample_work_item_data
    ):
        """Test that work item cannot have both parent and children."""
        parent = WorkItem.create(
            **sample_work_item_data, parent_hypothesis_id="hyp-123"
        )

        child = WorkItem.create(**sample_work_item_data, parent_hypothesis_id="hyp-123")

        parent.add_child(child.id)
        child.set_parent(parent.id)

        # Now child cannot have children
        grandchild = WorkItem.create(
            **sample_work_item_data, parent_hypothesis_id="hyp-123"
        )

        with pytest.raises(ValueError):
            child.add_child(grandchild.id)


class TestBlockerValueObject:
    """Tests for Blocker value object."""

    def test_blocker_creation(self):
        """Test creating a blocker."""
        blocker = Blocker(
            id="blocker-1",
            blocker_type="Dependency",
            severity=BlockerSeverity.HIGH,
            owner="John Doe",
            reason="Waiting for API",
            blocked_at=datetime.utcnow(),
        )

        assert blocker.id == "blocker-1"
        assert blocker.blocker_type == "Dependency"
        assert blocker.is_currently_blocked()

    def test_blocker_duration_calculation(self):
        """Test blocking duration calculation."""
        now = datetime.utcnow()
        blocker = Blocker(
            id="blocker-1",
            blocker_type="Dependency",
            severity=BlockerSeverity.HIGH,
            owner="John Doe",
            reason="Waiting for API",
            blocked_at=now,
        )

        # Unblock after 1 hour
        from datetime import timedelta

        blocker.unblocked_at = now + timedelta(hours=1)

        duration = blocker.get_blocking_duration()
        assert duration.total_seconds() == 3600  # 1 hour
