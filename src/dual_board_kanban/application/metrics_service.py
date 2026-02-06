"""Metrics service for calculating and retrieving flow metrics."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from dual_board_kanban.domain.flow_metrics import (
    FlowMetricsService,
    CycleTimeMetrics,
    LeadTimeMetrics,
    ThroughputMetrics,
    BlockingAgeMetrics,
    FlowLoadMetrics,
    FlowDebtMetrics,
)
from dual_board_kanban.domain.work_item import WorkItem
from dual_board_kanban.infrastructure.repositories import (
    HypothesisRepository,
    WorkItemRepository,
    FlowHistoryRepository,
)


@dataclass
class MetricsFilters:
    """Filters for metrics queries."""

    swimlane: Optional[str] = None
    assignee: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class MetricsService:
    """Application service for metrics operations."""

    def __init__(
        self,
        hypothesis_repo: HypothesisRepository,
        work_item_repo: WorkItemRepository,
        flow_history_repo: FlowHistoryRepository,
    ):
        """Initialize metrics service with repositories."""
        self.hypothesis_repo = hypothesis_repo
        self.work_item_repo = work_item_repo
        self.flow_history_repo = flow_history_repo
        self.flow_metrics_service = FlowMetricsService()

    def get_cycle_time_metrics(
        self, filters: Optional[MetricsFilters] = None
    ) -> CycleTimeMetrics:
        """Get cycle time metrics with filters."""
        work_items = self.work_item_repo.find_all()
        work_items = self._apply_filters(work_items, filters)

        return self.flow_metrics_service.calculate_cycle_time(work_items)

    def get_lead_time_metrics(
        self, filters: Optional[MetricsFilters] = None
    ) -> LeadTimeMetrics:
        """Get lead time metrics with filters."""
        work_items = self.work_item_repo.find_all()
        work_items = self._apply_filters(work_items, filters)

        return self.flow_metrics_service.calculate_lead_time(work_items)

    def get_throughput_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
        filters: Optional[MetricsFilters] = None,
    ) -> ThroughputMetrics:
        """Get throughput metrics with cadence and filters."""
        work_items = self.work_item_repo.find_all()
        work_items = self._apply_filters(work_items, filters)

        return self.flow_metrics_service.calculate_throughput(
            work_items, start_date, end_date
        )

    def get_blocking_age_metrics(
        self, filters: Optional[MetricsFilters] = None
    ) -> BlockingAgeMetrics:
        """Get blocking age metrics with filters."""
        work_items = self.work_item_repo.find_all()
        work_items = self._apply_filters(work_items, filters)

        hypotheses = self.hypothesis_repo.find_all()

        return self.flow_metrics_service.calculate_blocking_ages(work_items, hypotheses)

    def get_flow_load(self) -> FlowLoadMetrics:
        """Get current flow load."""
        work_items = self.work_item_repo.find_not_done()

        return self.flow_metrics_service.calculate_flow_load(work_items)

    def get_flow_debt(self) -> FlowDebtMetrics:
        """Get current flow debt."""
        work_items = self.work_item_repo.find_all()
        count = self.flow_metrics_service.calculate_flow_debt(work_items)

        return FlowDebtMetrics(count=count)

    def export_metrics_csv(self, filters: Optional[MetricsFilters] = None) -> str:
        """Export metrics data as CSV."""
        work_items = self.work_item_repo.find_all()
        work_items = self._apply_filters(work_items, filters)

        csv_lines = ["ID,Title,Stage,Rigor,Effort,Assignee,Swimlane,Created,Updated"]

        for work_item in work_items:
            csv_lines.append(
                f"{work_item.id},{work_item.title},{work_item.stage.name},"
                f"{work_item.rigor_level.value},{work_item.effort_level.value},"
                f"{work_item.assignee or ''},"
                f"{work_item.swimlane.value},"
                f"{work_item.created_at.isoformat()},"
                f"{work_item.updated_at.isoformat()}"
            )

        return "\n".join(csv_lines)

    def _apply_filters(
        self, work_items: List[WorkItem], filters: Optional[MetricsFilters] = None
    ) -> List[WorkItem]:
        """Apply filters to work items."""
        if not filters:
            return work_items

        filtered: List[WorkItem] = work_items

        if filters.swimlane:
            filtered = [wi for wi in filtered if wi.swimlane.value == filters.swimlane]

        if filters.assignee:
            filtered = [wi for wi in filtered if wi.assignee == filters.assignee]

        if filters.start_date and filters.end_date:
            filtered = [
                wi
                for wi in filtered
                if filters.start_date <= wi.created_at <= filters.end_date
            ]

        return filtered
