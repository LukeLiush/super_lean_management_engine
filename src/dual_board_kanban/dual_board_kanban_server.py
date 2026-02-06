#!/usr/bin/env python3
"""FastAPI server for the dual-board-kanban system."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from dual_board_kanban.infrastructure.base import DatabaseConnection, MigrationRunner
from dual_board_kanban.infrastructure.repositories import (
    HypothesisRepository,
    WorkItemRepository,
    FlowHistoryRepository,
)
from dual_board_kanban.application.board_service import BoardService
from dual_board_kanban.application.hypothesis_service import HypothesisService
from dual_board_kanban.application.work_item_service import WorkItemService
from dual_board_kanban.application.metrics_service import MetricsService
from dual_board_kanban.application.detail_page_service import DetailPageService

# Initialize FastAPI app
app = FastAPI(title="Dual-Board Kanban System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = DatabaseConnection("dual_board_kanban.db")
db.connect()

# Run migrations
migrator = MigrationRunner(db)
migrator.run_migrations()

# Initialize repositories
hypothesis_repo = HypothesisRepository(db)
work_item_repo = WorkItemRepository(db)
flow_history_repo = FlowHistoryRepository(db)

# Initialize services
board_service = BoardService(hypothesis_repo, work_item_repo)
hypothesis_service = HypothesisService(hypothesis_repo, work_item_repo)
work_item_service = WorkItemService(hypothesis_repo, work_item_repo)
metrics_service = MetricsService(hypothesis_repo, work_item_repo, flow_history_repo)
detail_page_service = DetailPageService(hypothesis_repo, work_item_repo)


# Pydantic models
class CreateHypothesisRequest(BaseModel):
    business_value: str
    problem_statement: str
    customers_impacted: str
    hypothesis_statement: str
    metrics_baseline: str
    solutions_ideas: List[str]
    lessons_learned: str = ""


class CreateWorkItemRequest(BaseModel):
    title: str
    goals: List[str]
    description: str
    acceptance_criteria: List[str]
    rigor_level: str
    effort_level: str
    assignee: Optional[str]
    swimlane: str
    parent_hypothesis_id: str


class MoveItemRequest(BaseModel):
    target_stage: str


class MarkBlockedRequest(BaseModel):
    blocker_type: str
    severity: str
    owner: str
    reason: str


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Strategic board endpoint
@app.get("/api/strategic-board")
async def get_strategic_board():
    """Get strategic board view."""
    board = board_service.get_strategic_board()
    return {
        "stages": board.stages,
        "cards_by_stage": {
            stage: [
                {
                    "id": card.id,
                    "title": card.title,
                    "stage": card.stage,
                    "is_blocked": card.is_blocked,
                }
                for card in cards
            ]
            for stage, cards in board.cards_by_stage.items()
        },
    }


# Work board endpoint
@app.get("/api/work-board")
async def get_work_board():
    """Get work delivery board view."""
    board = board_service.get_work_delivery_board()
    return {
        "stages": board.stages,
        "swimlanes": board.swimlanes,
        "flow_load": board.flow_load,
        "flow_debt": board.flow_debt,
        "cards_by_swimlane_and_stage": {
            swimlane: {
                stage: [
                    {
                        "id": card.id,
                        "title": card.title,
                        "stage": card.stage,
                        "is_blocked": card.is_blocked,
                        "child_count": card.child_count,
                    }
                    for card in cards
                ]
                for stage, cards in stages_dict.items()
            }
            for swimlane, stages_dict in board.cards_by_swimlane_and_stage.items()
        },
    }


# Metrics endpoint
@app.get("/api/metrics")
async def get_metrics():
    """Get metrics dashboard data."""
    cycle_time = metrics_service.get_cycle_time_metrics()
    lead_time = metrics_service.get_lead_time_metrics()
    flow_load = metrics_service.get_flow_load()
    flow_debt = metrics_service.get_flow_debt()

    return {
        "cycle_time": {
            "average": cycle_time.average,
            "median": cycle_time.median,
            "p50": cycle_time.p50,
            "p75": cycle_time.p75,
            "p90": cycle_time.p90,
            "count": cycle_time.count,
        },
        "lead_time": {
            "average": lead_time.average,
            "median": lead_time.median,
            "p50": lead_time.p50,
            "p75": lead_time.p75,
            "p90": lead_time.p90,
            "count": lead_time.count,
        },
        "flow_load": {
            "total_units": flow_load.total_units,
            "high_effort_count": flow_load.high_effort_count,
            "medium_effort_count": flow_load.medium_effort_count,
            "low_effort_count": flow_load.low_effort_count,
            "high_concentration": flow_load.high_concentration,
        },
        "flow_debt": {"count": flow_debt.count},
    }


# Hypotheses list endpoint
@app.get("/api/hypotheses")
async def get_hypotheses():
    """Get all hypotheses."""
    hypotheses = hypothesis_repo.find_all()
    return [
        {
            "id": h.id,
            "hypothesis_statement": h.hypothesis_statement,
            "business_value": h.business_value,
            "stage": h.stage.name,
        }
        for h in hypotheses
    ]


# Create hypothesis endpoint
@app.post("/api/hypothesis")
async def create_hypothesis(request: CreateHypothesisRequest):
    """Create a new hypothesis."""
    try:
        hypothesis_id = hypothesis_service.create_hypothesis(
            business_value=request.business_value,
            problem_statement=request.problem_statement,
            customers_impacted=request.customers_impacted,
            hypothesis_statement=request.hypothesis_statement,
            metrics_baseline=request.metrics_baseline,
            solutions_ideas=request.solutions_ideas,
            lessons_learned=request.lessons_learned,
        )
        return {"id": hypothesis_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Create work item endpoint
@app.post("/api/work-item")
async def create_work_item(request: CreateWorkItemRequest):
    """Create a new work item."""
    try:
        work_item_id = work_item_service.create_work_item(
            title=request.title,
            goals=request.goals,
            description=request.description,
            acceptance_criteria=request.acceptance_criteria,
            rigor_level=request.rigor_level,
            effort_level=request.effort_level,
            assignee=request.assignee,
            swimlane=request.swimlane,
            parent_hypothesis_id=request.parent_hypothesis_id,
        )
        return {"id": work_item_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Move hypothesis endpoint
@app.put("/api/hypothesis/{hypothesis_id}/move")
async def move_hypothesis(hypothesis_id: str, request: MoveItemRequest):
    """Move hypothesis to a new stage."""
    try:
        board_service.move_hypothesis(hypothesis_id, request.target_stage)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Move work item endpoint
@app.put("/api/work-item/{work_item_id}/move")
async def move_work_item(work_item_id: str, request: MoveItemRequest):
    """Move work item to a new stage."""
    try:
        board_service.move_work_item(work_item_id, request.target_stage)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Get hypothesis detail endpoint
@app.get("/api/hypothesis/{hypothesis_id}")
async def get_hypothesis_detail(hypothesis_id: str):
    """Get hypothesis detail view."""
    try:
        detail = detail_page_service.get_hypothesis_detail(hypothesis_id)
        return {
            "id": detail.id,
            "business_value": detail.business_value,
            "problem_statement": detail.problem_statement,
            "customers_impacted": detail.customers_impacted,
            "hypothesis_statement": detail.hypothesis_statement,
            "metrics_baseline": detail.metrics_baseline,
            "solutions_ideas": detail.solutions_ideas,
            "lessons_learned": detail.lessons_learned,
            "stage": detail.stage,
            "is_blocked": detail.is_blocked,
            "linked_work_item_ids": detail.linked_work_item_ids,
            "created_at": detail.created_at.isoformat(),
            "updated_at": detail.updated_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Get work item detail endpoint
@app.get("/api/work-item/{work_item_id}")
async def get_work_item_detail(work_item_id: str):
    """Get work item detail view."""
    try:
        detail = detail_page_service.get_work_item_detail(work_item_id)
        return {
            "id": detail.id,
            "title": detail.title,
            "goals": detail.goals,
            "description": detail.description,
            "acceptance_criteria": detail.acceptance_criteria,
            "rigor_level": detail.rigor_level,
            "effort_level": detail.effort_level,
            "assignee": detail.assignee,
            "swimlane": detail.swimlane,
            "stage": detail.stage,
            "parent_hypothesis_id": detail.parent_hypothesis_id,
            "parent_work_item_id": detail.parent_work_item_id,
            "child_work_item_ids": detail.child_work_item_ids,
            "is_blocked": detail.is_blocked,
            "is_invalidated": detail.is_invalidated,
            "created_at": detail.created_at.isoformat(),
            "updated_at": detail.updated_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
