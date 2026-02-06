"""Flow metrics domain service for calculating flow metrics."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
from statistics import mean, median
from dual_board_kanban.domain.work_item import WorkItem
from dual_board_kanban.domain.hypothesis import Hypothesis


def calculate_percentile(data: List[float], percentile: int) -> float:
    """Calculate percentile for a sorted list of values."""
    if not data:
        return 0
    if len(data) == 1:
        return data[0]

    index = (percentile / 100.0) * (len(data) - 1)
    lower = int(index)
    upper = lower + 1

    if upper >= len(data):
        return data[lower]

    weight = index - lower
    return data[lower] * (1 - weight) + data[upper] * weight


@dataclass
class CycleTimeMetrics:
    """Cycle time metrics."""

    average: float
    median: float
    p50: float
    p75: float
    p90: float
    count: int


@dataclass
class LeadTimeMetrics:
    """Lead time metrics."""

    average: float
    median: float
    p50: float
    p75: float
    p90: float
    count: int


@dataclass
class ThroughputMetrics:
    """Throughput metrics."""

    count: int
    cadence: str
    start_date: datetime
    end_date: datetime


@dataclass
class BlockingAgeMetrics:
    """Blocking age metrics."""

    total_time_blocked: timedelta
    average_block_duration: timedelta
    count_of_blocks: int
    active_stage_blocking: timedelta
    non_active_stage_blocking: timedelta


@dataclass
class FlowLoadMetrics:
    """Flow load metrics."""

    total_units: int
    high_effort_count: int
    medium_effort_count: int
    low_effort_count: int
    high_concentration: bool


@dataclass
class FlowDebtMetrics:
    """Flow debt metrics."""

    count: int


class FlowMetricsService:
    """
    Domain service for calculating flow metrics.
    """

    def calculate_cycle_time(self, work_items: List[WorkItem]) -> CycleTimeMetrics:
        """
        Calculate cycle time statistics (Design → Done).
        Cycle time is the duration from when a work item enters Design stage until Done.
        """
        cycle_times = []

        for work_item in work_items:
            # Find Design stage entry and Done stage entry
            design_time = None
            done_time = None

            for transition in work_item.stage_transitions:
                if transition.to_stage == "Design" and design_time is None:
                    design_time = transition.transitioned_at
                if transition.to_stage == "Done":
                    done_time = transition.transitioned_at

            # Only count items that have completed the cycle
            if design_time and done_time:
                cycle_time = (
                    done_time - design_time
                ).total_seconds() / 3600  # Convert to hours
                cycle_times.append(cycle_time)

        if not cycle_times:
            return CycleTimeMetrics(average=0, median=0, p50=0, p75=0, p90=0, count=0)

        cycle_times.sort()
        avg = mean(cycle_times)
        med = median(cycle_times)

        # Calculate percentiles
        p50 = calculate_percentile(cycle_times, 50)
        p75 = calculate_percentile(cycle_times, 75)
        p90 = calculate_percentile(cycle_times, 90)

        return CycleTimeMetrics(
            average=avg, median=med, p50=p50, p75=p75, p90=p90, count=len(cycle_times)
        )

    def calculate_lead_time(self, work_items: List[WorkItem]) -> LeadTimeMetrics:
        """
        Calculate lead time statistics (Queue → Done).
        Lead time is the duration from when a work item enters Queue stage until Done.
        """
        lead_times = []

        for work_item in work_items:
            # Find Queue stage entry and Done stage entry
            queue_time = None
            done_time = None

            for transition in work_item.stage_transitions:
                if transition.to_stage == "Queue" and queue_time is None:
                    queue_time = transition.transitioned_at
                if transition.to_stage == "Done":
                    done_time = transition.transitioned_at

            # If no Queue transition recorded, use created_at
            if queue_time is None:
                queue_time = work_item.created_at

            # Only count items that have completed the cycle
            if queue_time and done_time:
                lead_time = (
                    done_time - queue_time
                ).total_seconds() / 3600  # Convert to hours
                lead_times.append(lead_time)

        if not lead_times:
            return LeadTimeMetrics(average=0, median=0, p50=0, p75=0, p90=0, count=0)

        lead_times.sort()
        avg = mean(lead_times)
        med = median(lead_times)

        # Calculate percentiles
        p50 = calculate_percentile(lead_times, 50)
        p75 = calculate_percentile(lead_times, 75)
        p90 = calculate_percentile(lead_times, 90)

        return LeadTimeMetrics(
            average=avg, median=med, p50=p50, p75=p75, p90=p90, count=len(lead_times)
        )

    def calculate_throughput(
        self, work_items: List[WorkItem], start_date: datetime, end_date: datetime
    ) -> ThroughputMetrics:
        """
        Calculate throughput for given date range.
        Throughput is the count of work items completed (moved to Done) within the period.
        """
        count = 0

        for work_item in work_items:
            # Find when item reached Done stage
            for transition in work_item.stage_transitions:
                if transition.to_stage == "Done":
                    if start_date <= transition.transitioned_at <= end_date:
                        count += 1
                    break

        return ThroughputMetrics(
            count=count, cadence="custom", start_date=start_date, end_date=end_date
        )

    def calculate_blocking_ages(
        self, work_items: List[WorkItem], hypotheses: List[Hypothesis]
    ) -> BlockingAgeMetrics:
        """
        Calculate blocking age statistics.
        Blocking age is the sum of all durations between block start and block end timestamps.
        """
        total_blocking = timedelta(0)
        active_stage_blocking = timedelta(0)
        non_active_stage_blocking = timedelta(0)
        block_count = 0
        block_durations = []

        # Process work items
        for work_item in work_items:
            if work_item.blocker:
                duration = work_item.blocker.get_blocking_duration()
                block_durations.append(duration)
                total_blocking += duration
                block_count += 1

                if work_item.is_in_active_stage():
                    active_stage_blocking += duration
                else:
                    non_active_stage_blocking += duration

        # Process hypotheses
        for hypothesis in hypotheses:
            if hypothesis.blocker:
                duration = hypothesis.blocker.get_blocking_duration()
                block_durations.append(duration)
                total_blocking += duration
                block_count += 1

                if hypothesis.is_in_active_stage():
                    active_stage_blocking += duration
                else:
                    non_active_stage_blocking += duration

        # Calculate average
        avg_duration = timedelta(0)
        if block_durations:
            total_seconds = sum(d.total_seconds() for d in block_durations)
            avg_seconds = total_seconds / len(block_durations)
            avg_duration = timedelta(seconds=avg_seconds)

        return BlockingAgeMetrics(
            total_time_blocked=total_blocking,
            average_block_duration=avg_duration,
            count_of_blocks=block_count,
            active_stage_blocking=active_stage_blocking,
            non_active_stage_blocking=non_active_stage_blocking,
        )

    def calculate_flow_load(self, work_items: List[WorkItem]) -> FlowLoadMetrics:
        """
        Calculate current flow load (total effort units in system).
        Flow load is the sum of effort units across all work items not in Done stage.
        High=3, Medium=2, Low=1
        """
        total_units = 0
        high_count = 0
        medium_count = 0
        low_count = 0

        for work_item in work_items:
            # Only count items not in Done stage
            if work_item.stage.name != "Done":
                effort_units = work_item.get_effort_units()
                total_units += effort_units

                if work_item.effort_level.value == "HIGH":
                    high_count += 1
                elif work_item.effort_level.value == "MEDIUM":
                    medium_count += 1
                else:
                    low_count += 1

        # High concentration is when more than 50% of units are High effort
        high_concentration = False
        if total_units > 0:
            high_units = high_count * 3
            high_concentration = high_units > (total_units * 0.5)

        return FlowLoadMetrics(
            total_units=total_units,
            high_effort_count=high_count,
            medium_effort_count=medium_count,
            low_effort_count=low_count,
            high_concentration=high_concentration,
        )

    def calculate_flow_debt(self, work_items: List[WorkItem]) -> int:
        """
        Calculate flow debt (invalidated experiments with maintenance burden).
        """
        count = 0
        for work_item in work_items:
            if work_item.is_invalidated and work_item.created_maintenance_burden:
                count += 1
        return count
