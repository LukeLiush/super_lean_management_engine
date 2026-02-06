#!/usr/bin/env python3
"""Streamlit UI for the dual-board-kanban system."""

import streamlit as st
from datetime import datetime, timedelta
import requests

# Page config
st.set_page_config(
    page_title="Dual-Board Kanban",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if "api_available" not in st.session_state:
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=2)
        st.session_state.api_available = response.status_code == 200
    except Exception:
        st.session_state.api_available = False


# Helper functions for API calls
def api_get(endpoint: str):
    """Make GET request to API."""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None


def api_post(endpoint: str, data: dict):
    """Make POST request to API."""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        try:
            error_detail = e.response.json().get("detail", str(e))
        except Exception:
            error_detail = str(e)
        st.error(f"API Error: {error_detail}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None


def api_put(endpoint: str, data: dict):
    """Make PUT request to API."""
    try:
        response = requests.put(f"{API_BASE_URL}{endpoint}", json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None


# Check API availability
if not st.session_state.api_available:
    st.error(
        "❌ FastAPI server is not running. Please start it with: `uv run python src/dual_board_kanban/dual_board_kanban_server.py`"
    )
    st.stop()

# Sidebar
st.sidebar.title("🎯 Dual-Board Kanban")
page = st.sidebar.radio(
    "Navigation",
    [
        "Strategic Board",
        "Work Board",
        "Metrics",
        "Create Hypothesis",
        "Create Work Item",
    ],
)


def render_strategic_board():
    """Render the strategic board."""
    st.title("Strategic Board")

    board_data = api_get("/api/strategic-board")
    if not board_data:
        return

    # Create columns for stages
    cols = st.columns(len(board_data["stages"]))

    for col, stage in zip(cols, board_data["stages"]):
        with col:
            st.subheader(stage)
            cards = board_data["cards_by_stage"].get(stage, [])

            for card in cards:
                with st.container():
                    col1, col2 = st.columns([4, 1])

                    with col1:
                        if card["is_blocked"]:
                            st.warning(f"🚫 {card['title']}")
                        else:
                            st.info(card["title"])

                    with col2:
                        if st.button("📋", key=f"hyp-{card['id']}"):
                            st.session_state.selected_hypothesis = card["id"]
                            st.rerun()


def render_work_board():
    """Render the work delivery board."""
    st.title("Work Board")

    board_data = api_get("/api/work-board")
    if not board_data:
        return

    # Display flow metrics summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Flow Load", f"{board_data['flow_load']} units")
    with col2:
        st.metric("Flow Debt", board_data["flow_debt"])
    with col3:
        st.metric("Stages", len(board_data["stages"]))
    with col4:
        st.metric("Swimlanes", len(board_data["swimlanes"]))

    st.divider()

    # Swimlane tabs
    swimlane_tabs = st.tabs(board_data["swimlanes"])

    for tab, swimlane in zip(swimlane_tabs, board_data["swimlanes"]):
        with tab:
            st.subheader(swimlane.replace("_", " "))

            # Create columns for stages
            cols = st.columns(len(board_data["stages"]))

            for col, stage in zip(cols, board_data["stages"]):
                with col:
                    st.write(f"**{stage}**")
                    cards = (
                        board_data["cards_by_swimlane_and_stage"]
                        .get(swimlane, {})
                        .get(stage, [])
                    )

                    for card in cards:
                        with st.container():
                            col1, col2 = st.columns([4, 1])

                            with col1:
                                if card["is_blocked"]:
                                    st.warning(f"🚫 {card['title']}")
                                else:
                                    st.info(card["title"])

                                if card["child_count"] > 0:
                                    st.caption(f"👶 {card['child_count']} children")

                            with col2:
                                if st.button("📋", key=f"wi-{card['id']}"):
                                    st.session_state.selected_work_item = card["id"]
                                    st.rerun()


def render_metrics():
    """Render the metrics dashboard."""
    st.title("📊 Metrics Dashboard")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        st.selectbox(
            "Swimlane",
            ["All", "STRATEGIC_EXPERIMENTS", "TACTICAL_DEBT", "DEFECTS_SUPPORT"],
        )

    with col2:
        st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now(),
        )

    with col3:
        st.text_input("Assignee (optional)")

    st.divider()

    # Get metrics
    metrics_data = api_get("/api/metrics")
    if not metrics_data:
        return

    # Cycle Time Metrics
    st.subheader("Cycle Time (Design → Done)")
    cycle_time = metrics_data["cycle_time"]

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Average", f"{cycle_time['average']:.1f}h")
    with col2:
        st.metric("Median", f"{cycle_time['median']:.1f}h")
    with col3:
        st.metric("50th %ile", f"{cycle_time['p50']:.1f}h")
    with col4:
        st.metric("75th %ile", f"{cycle_time['p75']:.1f}h")
    with col5:
        st.metric("90th %ile", f"{cycle_time['p90']:.1f}h")

    st.divider()

    # Lead Time Metrics
    st.subheader("Lead Time (Queue → Done)")
    lead_time = metrics_data["lead_time"]

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Average", f"{lead_time['average']:.1f}h")
    with col2:
        st.metric("Median", f"{lead_time['median']:.1f}h")
    with col3:
        st.metric("50th %ile", f"{lead_time['p50']:.1f}h")
    with col4:
        st.metric("75th %ile", f"{lead_time['p75']:.1f}h")
    with col5:
        st.metric("90th %ile", f"{lead_time['p90']:.1f}h")

    st.divider()

    # Flow Load
    st.subheader("Flow Load (Current)")
    flow_load = metrics_data["flow_load"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Units", flow_load["total_units"])
    with col2:
        st.metric("High Effort", flow_load["high_effort_count"])
    with col3:
        st.metric("Medium Effort", flow_load["medium_effort_count"])
    with col4:
        st.metric("Low Effort", flow_load["low_effort_count"])

    if flow_load["high_concentration"]:
        st.warning("⚠️ High concentration of High Effort items detected!")

    st.divider()

    # Flow Debt
    st.subheader("Flow Debt")
    flow_debt = metrics_data["flow_debt"]
    st.metric("Invalidated Experiments with Maintenance Burden", flow_debt["count"])


def render_create_hypothesis():
    """Render the create hypothesis form."""
    st.title("➕ Create Hypothesis")

    with st.form("create_hypothesis_form"):
        business_value = st.text_input("Business Value")
        problem_statement = st.text_area("Problem Statement")
        customers_impacted = st.text_input("Customers Impacted")
        hypothesis_statement = st.text_area(
            "Hypothesis Statement (format: We believe that [X] will result in [Y]. We will know we've succeeded when [Z].)"
        )
        metrics_baseline = st.text_area("Metrics Baseline")
        solutions_ideas = st.text_area("Solutions/Ideas (one per line)").split("\n")
        lessons_learned = st.text_area("Lessons Learned (optional)")

        if st.form_submit_button("Create Hypothesis"):
            result = api_post(
                "/api/hypothesis",
                {
                    "business_value": business_value,
                    "problem_statement": problem_statement,
                    "customers_impacted": customers_impacted,
                    "hypothesis_statement": hypothesis_statement,
                    "metrics_baseline": metrics_baseline,
                    "solutions_ideas": [
                        s.strip() for s in solutions_ideas if s.strip()
                    ],
                    "lessons_learned": lessons_learned,
                },
            )
            if result:
                st.success(f"✅ Hypothesis created: {result['id']}")


def render_create_work_item():
    """Render the create work item form."""
    st.title("➕ Create Work Item")

    # Get hypotheses for dropdown
    hypotheses_data = api_get("/api/hypotheses")
    if not hypotheses_data:
        st.error("Could not load hypotheses")
        return

    hypothesis_options = {
        h["hypothesis_statement"][:50]: h["id"] for h in hypotheses_data
    }

    with st.form("create_work_item_form"):
        title = st.text_input("Title")
        goals = st.text_area("Goals (one per line)").split("\n")
        description = st.text_area("Description")
        acceptance_criteria = st.text_area("Acceptance Criteria (one per line)").split(
            "\n"
        )

        col1, col2 = st.columns(2)
        with col1:
            rigor_level = st.selectbox("Rigor Level", ["HIGH", "MEDIUM", "LOW"])
            effort_level = st.selectbox("Effort Level", ["HIGH", "MEDIUM", "LOW"])

        with col2:
            assignee = st.text_input("Assignee (optional)")
            swimlane = st.selectbox(
                "Swimlane",
                ["STRATEGIC_EXPERIMENTS", "TACTICAL_DEBT", "DEFECTS_SUPPORT"],
            )

        parent_hypothesis = st.selectbox(
            "Parent Hypothesis", list(hypothesis_options.keys())
        )

        if st.form_submit_button("Create Work Item"):
            result = api_post(
                "/api/work-item",
                {
                    "title": title,
                    "goals": [g.strip() for g in goals if g.strip()],
                    "description": description,
                    "acceptance_criteria": [
                        a.strip() for a in acceptance_criteria if a.strip()
                    ],
                    "rigor_level": rigor_level,
                    "effort_level": effort_level,
                    "assignee": assignee if assignee else None,
                    "swimlane": swimlane,
                    "parent_hypothesis_id": hypothesis_options[parent_hypothesis],
                },
            )
            if result:
                st.success(f"✅ Work Item created: {result['id']}")


# Main content
if page == "Strategic Board":
    render_strategic_board()
elif page == "Work Board":
    render_work_board()
elif page == "Metrics":
    render_metrics()
elif page == "Create Hypothesis":
    render_create_hypothesis()
elif page == "Create Work Item":
    render_create_work_item()

# Footer
st.divider()
st.caption("🎯 Dual-Board Kanban System | Strategic-Tactical Alignment")
