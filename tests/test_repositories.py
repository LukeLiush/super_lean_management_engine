"""Unit tests for repositories."""

from dual_board_kanban.domain.hypothesis import Hypothesis
from dual_board_kanban.domain.work_item import WorkItem
from dual_board_kanban.infrastructure.repositories import (
    HypothesisRepository,
    WorkItemRepository,
)


class TestHypothesisRepository:
    """Tests for HypothesisRepository."""

    def test_save_and_find_hypothesis(self, temp_db, sample_hypothesis_data):
        """Test saving and finding a hypothesis."""
        repo = HypothesisRepository(temp_db)

        hypothesis = Hypothesis.create(**sample_hypothesis_data)
        repo.save(hypothesis)

        found = repo.find_by_id(hypothesis.id)
        assert found is not None
        assert found.id == hypothesis.id
        assert found.business_value == hypothesis.business_value

    def test_find_all_hypotheses(self, temp_db, sample_hypothesis_data):
        """Test finding all hypotheses."""
        repo = HypothesisRepository(temp_db)

        hyp1 = Hypothesis.create(**sample_hypothesis_data)
        hyp2 = Hypothesis.create(**sample_hypothesis_data)

        repo.save(hyp1)
        repo.save(hyp2)

        all_hypotheses = repo.find_all()
        assert len(all_hypotheses) == 2

    def test_find_hypothesis_by_stage(self, temp_db, sample_hypothesis_data):
        """Test finding hypotheses by stage."""
        repo = HypothesisRepository(temp_db)

        hyp = Hypothesis.create(**sample_hypothesis_data)
        repo.save(hyp)

        in_queue = repo.find_by_stage(hyp.stage)
        assert len(in_queue) == 1
        assert in_queue[0].id == hyp.id


class TestWorkItemRepository:
    """Tests for WorkItemRepository."""

    def test_save_and_find_work_item(self, temp_db, sample_work_item_data):
        """Test saving and finding a work item."""
        repo = WorkItemRepository(temp_db)

        work_item = WorkItem.create(
            **sample_work_item_data, parent_hypothesis_id="hyp-123"
        )
        repo.save(work_item)

        found = repo.find_by_id(work_item.id)
        assert found is not None
        assert found.id == work_item.id
        assert found.title == work_item.title

    def test_find_work_items_by_hypothesis(self, temp_db, sample_work_item_data):
        """Test finding work items by hypothesis."""
        repo = WorkItemRepository(temp_db)

        hyp_id = "hyp-123"
        wi1 = WorkItem.create(**sample_work_item_data, parent_hypothesis_id=hyp_id)
        wi2 = WorkItem.create(**sample_work_item_data, parent_hypothesis_id=hyp_id)

        repo.save(wi1)
        repo.save(wi2)

        found = repo.find_by_hypothesis(hyp_id)
        assert len(found) == 2

    def test_find_work_items_by_parent(self, temp_db, sample_work_item_data):
        """Test finding child work items by parent."""
        repo = WorkItemRepository(temp_db)

        parent = WorkItem.create(
            **sample_work_item_data, parent_hypothesis_id="hyp-123"
        )
        child = WorkItem.create(**sample_work_item_data, parent_hypothesis_id="hyp-123")

        parent.add_child(child.id)
        child.set_parent(parent.id)

        repo.save(parent)
        repo.save(child)

        children = repo.find_by_parent(parent.id)
        assert len(children) == 1
        assert children[0].id == child.id

    def test_find_not_done_work_items(self, temp_db, sample_work_item_data):
        """Test finding work items not in Done stage."""
        repo = WorkItemRepository(temp_db)

        wi = WorkItem.create(**sample_work_item_data, parent_hypothesis_id="hyp-123")
        repo.save(wi)

        not_done = repo.find_not_done()
        assert len(not_done) >= 1
        assert any(item.id == wi.id for item in not_done)

    def test_work_item_children_persistence(self, temp_db, sample_work_item_data):
        """Test that work item children are persisted correctly."""
        repo = WorkItemRepository(temp_db)

        parent = WorkItem.create(
            **sample_work_item_data, parent_hypothesis_id="hyp-123"
        )
        child1 = WorkItem.create(
            **sample_work_item_data, parent_hypothesis_id="hyp-123"
        )
        child2 = WorkItem.create(
            **sample_work_item_data, parent_hypothesis_id="hyp-123"
        )

        parent.add_child(child1.id)
        parent.add_child(child2.id)
        child1.set_parent(parent.id)
        child2.set_parent(parent.id)

        repo.save(parent)
        repo.save(child1)
        repo.save(child2)

        # Retrieve and verify
        found_parent = repo.find_by_id(parent.id)
        assert len(found_parent.child_work_item_ids) == 2
        assert child1.id in found_parent.child_work_item_ids
        assert child2.id in found_parent.child_work_item_ids
