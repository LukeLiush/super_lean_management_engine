"""Unit tests for application services."""

import pytest
from dual_board_kanban.application.board_service import BoardService
from dual_board_kanban.application.hypothesis_service import HypothesisService
from dual_board_kanban.application.work_item_service import WorkItemService
from dual_board_kanban.application.metrics_service import MetricsService, MetricsFilters
from dual_board_kanban.infrastructure.repositories import (
    HypothesisRepository,
    WorkItemRepository,
    FlowHistoryRepository,
)


class TestBoardService:
    """Tests for BoardService."""

    def test_get_strategic_board(self, temp_db, sample_hypothesis_data):
        """Test getting strategic board."""
        hyp_repo = HypothesisRepository(temp_db)
        wi_repo = WorkItemRepository(temp_db)
        service = BoardService(hyp_repo, wi_repo)

        # Create and save a hypothesis
        from dual_board_kanban.domain.hypothesis import Hypothesis

        hyp = Hypothesis.create(**sample_hypothesis_data)
        hyp_repo.save(hyp)

        board = service.get_strategic_board()
        assert board.stages == ["In Queue", "Review", "Execution", "Done"]
        assert "In Queue" in board.cards_by_stage

    def test_get_work_delivery_board(self, temp_db, sample_work_item_data):
        """Test getting work delivery board."""
        hyp_repo = HypothesisRepository(temp_db)
        wi_repo = WorkItemRepository(temp_db)
        service = BoardService(hyp_repo, wi_repo)

        # Create and save a work item
        from dual_board_kanban.domain.work_item import WorkItem

        wi = WorkItem.create(**sample_work_item_data, parent_hypothesis_id="hyp-123")
        wi_repo.save(wi)

        board = service.get_work_delivery_board()
        assert len(board.stages) == 8
        assert "Queue" in board.stages
        assert "Done" in board.stages


class TestHypothesisService:
    """Tests for HypothesisService."""

    def test_create_hypothesis(self, temp_db, sample_hypothesis_data):
        """Test creating a hypothesis."""
        hyp_repo = HypothesisRepository(temp_db)
        wi_repo = WorkItemRepository(temp_db)
        service = HypothesisService(hyp_repo, wi_repo)

        hyp_id = service.create_hypothesis(**sample_hypothesis_data)
        assert hyp_id is not None

        found = hyp_repo.find_by_id(hyp_id)
        assert found is not None

    def test_hypothesis_statement_validation(self, temp_db, sample_hypothesis_data):
        """Test hypothesis statement format validation."""
        hyp_repo = HypothesisRepository(temp_db)
        wi_repo = WorkItemRepository(temp_db)
        service = HypothesisService(hyp_repo, wi_repo)

        invalid_data = sample_hypothesis_data.copy()
        invalid_data["hypothesis_statement"] = "Invalid format"

        with pytest.raises(ValueError):
            service.create_hypothesis(**invalid_data)

    def test_get_linked_work_items_summary(
        self, temp_db, sample_hypothesis_data, sample_work_item_data
    ):
        """Test getting linked work items summary."""
        hyp_repo = HypothesisRepository(temp_db)
        wi_repo = WorkItemRepository(temp_db)
        service = HypothesisService(hyp_repo, wi_repo)

        # Create hypothesis
        hyp_id = service.create_hypothesis(**sample_hypothesis_data)

        # Create work items linked to hypothesis
        from dual_board_kanban.domain.work_item import WorkItem

        wi = WorkItem.create(**sample_work_item_data, parent_hypothesis_id=hyp_id)
        wi_repo.save(wi)

        summary = service.get_linked_work_items_summary(hyp_id)
        assert summary["MEDIUM"]["MEDIUM"] == 1


class TestWorkItemService:
    """Tests for WorkItemService."""

    def test_create_work_item(
        self, temp_db, sample_hypothesis_data, sample_work_item_data
    ):
        """Test creating a work item."""
        hyp_repo = HypothesisRepository(temp_db)
        wi_repo = WorkItemRepository(temp_db)
        service = WorkItemService(hyp_repo, wi_repo)

        # Create parent hypothesis
        from dual_board_kanban.domain.hypothesis import Hypothesis

        hyp = Hypothesis.create(**sample_hypothesis_data)
        hyp_repo.save(hyp)

        # Create work item
        wi_id = service.create_work_item(
            **sample_work_item_data, parent_hypothesis_id=hyp.id
        )
        assert wi_id is not None

    def test_add_child_work_item(
        self, temp_db, sample_hypothesis_data, sample_work_item_data
    ):
        """Test adding child work item."""
        hyp_repo = HypothesisRepository(temp_db)
        wi_repo = WorkItemRepository(temp_db)
        service = WorkItemService(hyp_repo, wi_repo)

        # Create parent hypothesis
        from dual_board_kanban.domain.hypothesis import Hypothesis

        hyp = Hypothesis.create(**sample_hypothesis_data)
        hyp_repo.save(hyp)

        # Create parent and child work items
        parent_id = service.create_work_item(
            **sample_work_item_data, parent_hypothesis_id=hyp.id
        )
        child_id = service.create_work_item(
            **sample_work_item_data, parent_hypothesis_id=hyp.id
        )

        # Add child to parent
        service.add_child_work_item(parent_id, child_id)

        # Verify
        parent = wi_repo.find_by_id(parent_id)
        assert child_id in parent.child_work_item_ids


class TestMetricsService:
    """Tests for MetricsService."""

    def test_get_flow_load(
        self, temp_db, sample_hypothesis_data, sample_work_item_data
    ):
        """Test getting flow load."""
        hyp_repo = HypothesisRepository(temp_db)
        wi_repo = WorkItemRepository(temp_db)
        flow_repo = FlowHistoryRepository(temp_db)
        service = MetricsService(hyp_repo, wi_repo, flow_repo)

        # Create work items
        from dual_board_kanban.domain.work_item import WorkItem

        wi = WorkItem.create(**sample_work_item_data, parent_hypothesis_id="hyp-123")
        wi_repo.save(wi)

        metrics = service.get_flow_load()
        assert metrics.total_units > 0

    def test_get_flow_debt(
        self, temp_db, sample_hypothesis_data, sample_work_item_data
    ):
        """Test getting flow debt."""
        hyp_repo = HypothesisRepository(temp_db)
        wi_repo = WorkItemRepository(temp_db)
        flow_repo = FlowHistoryRepository(temp_db)
        service = MetricsService(hyp_repo, wi_repo, flow_repo)

        # Create invalidated work item
        from dual_board_kanban.domain.work_item import WorkItem

        wi = WorkItem.create(**sample_work_item_data, parent_hypothesis_id="hyp-123")
        wi.mark_invalidated(created_maintenance_burden=True)
        wi_repo.save(wi)

        metrics = service.get_flow_debt()
        assert metrics.count == 1

    def test_metrics_filtering(
        self, temp_db, sample_hypothesis_data, sample_work_item_data
    ):
        """Test metrics filtering."""
        hyp_repo = HypothesisRepository(temp_db)
        wi_repo = WorkItemRepository(temp_db)
        flow_repo = FlowHistoryRepository(temp_db)
        service = MetricsService(hyp_repo, wi_repo, flow_repo)

        # Create work items with different swimlanes
        from dual_board_kanban.domain.work_item import WorkItem

        wi1 = WorkItem.create(**sample_work_item_data, parent_hypothesis_id="hyp-123")
        wi_repo.save(wi1)

        # Apply filter
        filters = MetricsFilters(swimlane="STRATEGIC_EXPERIMENTS")
        metrics = service.get_cycle_time_metrics(filters)
        assert metrics is not None
