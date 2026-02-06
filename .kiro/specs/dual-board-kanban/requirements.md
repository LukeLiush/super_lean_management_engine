# Requirements Document: Dual-Board Kanban System

## Introduction

This document specifies requirements for a dual-board Kanban system designed to track strategic hypotheses and tactical experiments. The system enables teams to visualize the relationship between strategic thinking (hypotheses) and tactical execution (experiments/work items), while providing flow metrics to optimize delivery.

## Glossary

- **System**: The dual-board Kanban application
- **Strategic_Board**: The board tracking strategic hypotheses
- **Work_Board**: The board tracking tactical experiments and work items
- **Hypothesis**: A strategic assumption to be validated through experiments
- **Work_Item**: A tactical experiment, task, or defect tracked on the Work Board
- **Hypothesis_Canvas**: The structured template containing hypothesis details
- **Active_Stage**: A stage where work is actively being performed (Design-Review, CR-Review, Deploy, Release, Design, Implementation)
- **Blocker**: An impediment preventing progress in an active stage
- **Flow_Metrics**: Quantitative measurements of work flow through the system
- **Flow_Load**: Total effort units currently in the system
- **Flow_Debt**: Count of invalidated experiments that created maintenance burden
- **Swimlane**: A horizontal partition on the Work Board categorizing work types
- **Rigor_Level**: The thoroughness required for a work item (High/Medium/Low)
- **Effort_Level**: The estimated effort for a work item (High/Medium/Low)

## Requirements

### Requirement 1: Board Navigation

**User Story:** As a user, I want to navigate between the Strategic Board and Work Board, so that I can view both strategic hypotheses and tactical work.

#### Acceptance Criteria

1. THE System SHALL provide tab-based navigation between Strategic_Board and Work_Board
2. WHEN a user selects a board tab, THE System SHALL display the corresponding board
3. WHEN switching between boards, THE System SHALL preserve the state of the previously viewed board


### Requirement 2: Strategic Board Structure

**User Story:** As a strategist, I want to track hypotheses through defined stages, so that I can manage the validation lifecycle.

#### Acceptance Criteria

1. THE Strategic_Board SHALL display stages in this order: In Queue, Review, Execution, Done
2. WHEN a Hypothesis is created, THE System SHALL place it in the In Queue stage
3. THE System SHALL allow moving Hypothesis cards between adjacent stages
4. WHEN a Hypothesis is in Execution stage, THE System SHALL mark this as Active_Stage

### Requirement 3: Work Board Structure

**User Story:** As a delivery manager, I want to track work items through delivery stages across different work types, so that I can manage tactical execution.

#### Acceptance Criteria

1. THE Work_Board SHALL display stages in this order: Queue, Design, Design-Review, Implementation, CR-Review, Deploy, Release, Done
2. THE Work_Board SHALL display three Swimlane sections: Strategic Experiments (Value Drivers), Tactical Debt & Cleanup (Value Enablers), Defects & Support (Failure Demand)
3. WHEN a Work_Item is created, THE System SHALL place it in the Queue stage within the specified Swimlane
4. THE System SHALL allow moving Work_Item cards between adjacent stages within their Swimlane
5. WHEN a Work_Item is in Design-Review, CR-Review, Deploy, or Release stages, THE System SHALL mark these as Active_Stage
6. WHEN a user clicks a Swimlane header, THE System SHALL toggle the visibility of that Swimlane's content

### Requirement 4: Hypothesis Canvas Management

**User Story:** As a strategist, I want to document hypothesis details using a structured canvas, so that I can capture all relevant strategic information.

#### Acceptance Criteria

1. THE System SHALL store these fields for each Hypothesis: Business value, Problem statement, Customers impacted, Hypothesis statement, Metrics baseline, Solutions/Ideas, Lessons learned
2. WHEN a user creates a Hypothesis, THE System SHALL provide input fields for all Hypothesis_Canvas fields
3. WHEN a user clicks a Hypothesis card, THE System SHALL display a detail modal showing all Hypothesis_Canvas fields
4. THE System SHALL display only minimal information on Hypothesis cards in the board view
5. THE System SHALL validate that Hypothesis statement follows the format: "We believe that [X] will result in [Y]. We will know we've succeeded when [Z]."

### Requirement 5: Work Item Management

**User Story:** As a team member, I want to create and manage work items with relevant details, so that I can track tactical execution.

#### Acceptance Criteria

1. THE System SHALL store these fields for each Work_Item: Title, Goals (list), Description, Acceptance Criteria (list), Rigor_Level, Effort_Level, Assignee
2. WHEN a user creates a Work_Item, THE System SHALL provide input fields for all Work_Item fields
3. WHEN a Work_Item is on the Work_Board, THE System SHALL display Title, Rigor_Level, Effort_Level, and Assignee on the card
4. WHEN a user clicks a Work_Item card, THE System SHALL display a detail modal showing all Work_Item fields
5. THE System SHALL allow Rigor_Level values of: High, Medium, Low
6. THE System SHALL allow Effort_Level values of: High, Medium, Low

### Requirement 6: Hypothesis-Experiment Linking

**User Story:** As a strategist, I want to link work items to parent hypotheses, so that I can track which experiments validate which hypotheses.

#### Acceptance Criteria

1. WHEN a Work_Item is created, THE System SHALL require linking to a parent Hypothesis
2. THE System SHALL display visual connectors between Work_Item cards and their parent Hypothesis
3. WHEN a user views a Hypothesis detail modal, THE System SHALL display a list of links to all associated Work_Item cards
4. WHEN a user clicks a Work_Item link in the Hypothesis detail modal, THE System SHALL navigate to that Work_Item's detail modal
5. THE System SHALL display on each Hypothesis card the count of linked Work_Item cards categorized by Rigor_Level and Effort_Level
6. THE System SHALL prevent creating a Work_Item without a parent Hypothesis

### Requirement 7: Hierarchical Work Item Structure

**User Story:** As a team member, I want to create parent-child relationships between work items, so that I can break down complex work into manageable sub-tasks.

#### Acceptance Criteria

1. THE System SHALL allow a Work_Item to have child Work_Item cards
2. THE System SHALL allow a Work_Item to have a parent Work_Item card
3. THE System SHALL support only one level of parent-child relationships
4. THE System SHALL prevent a Work_Item that has a parent from having children
5. THE System SHALL prevent a Work_Item that has children from being assigned a parent
6. WHEN all child Work_Item cards of a parent reach Done stage, THE System SHALL automatically move the parent Work_Item to Done stage
7. WHEN any child Work_Item card of a parent reaches Implementation stage, THE System SHALL automatically move the parent Work_Item to Implementation stage
8. WHEN a child Work_Item card moves to a new stage, THE System SHALL automatically move the parent Work_Item according to the parent stage transition rules
9. THE System SHALL display the count of child Work_Item cards on parent Work_Item cards
10. THE System SHALL display the parent Work_Item link on child Work_Item cards
11. WHEN a user views a Work_Item detail modal, THE System SHALL display links to all child Work_Item cards and the parent Work_Item card

### Requirement 8: Blocking Management

**User Story:** As a team member, I want to mark active stages as blocked with structured information, so that impediments are visible and tracked.

#### Acceptance Criteria

1. WHEN a Work_Item or Hypothesis is in an Active_Stage, THE System SHALL allow marking it as blocked
2. WHEN marking an item as blocked, THE System SHALL require input for: blocker type, severity, owner, and reason
3. THE System SHALL display a visual indicator on blocked cards
4. WHEN a user clicks a blocked card, THE System SHALL display Blocker details in the detail modal
5. THE System SHALL allow unblocking an item by removing the blocked status
6. WHEN an item is unblocked, THE System SHALL record the unblock timestamp

### Requirement 9: Flow Metrics - Cycle Time

**User Story:** As a delivery manager, I want to measure cycle time, so that I can understand how long active work takes.

#### Acceptance Criteria

1. THE System SHALL calculate Cycle_Time as the duration from when a Work_Item enters Design stage until it reaches Done stage
2. THE System SHALL display Cycle_Time metrics on a separate metrics view
3. THE System SHALL provide Cycle_Time statistics: average, median, percentiles (50th, 75th, 90th)
4. THE System SHALL display Cycle_Time trends over time using charts

### Requirement 10: Flow Metrics - Lead Time

**User Story:** As a delivery manager, I want to measure lead time, so that I can understand total time from request to delivery.

#### Acceptance Criteria

1. THE System SHALL calculate Lead_Time as the duration from when a Work_Item enters Queue stage until it reaches Done stage
2. THE System SHALL display Lead_Time metrics on a separate metrics view
3. THE System SHALL provide Lead_Time statistics: average, median, percentiles (50th, 75th, 90th)
4. THE System SHALL display Lead_Time trends over time using charts

### Requirement 11: Flow Metrics - Throughput

**User Story:** As a delivery manager, I want to measure throughput, so that I can understand delivery capacity.

#### Acceptance Criteria

1. THE System SHALL calculate Throughput as the count of Work_Item cards completed (moved to Done) within a configurable time period
2. THE System SHALL allow configuring the time period for Throughput calculation with flexible cadence options: N weeks, N months, or custom date range
3. THE System SHALL display Throughput metrics on a separate metrics view
4. THE System SHALL display Throughput trends over time using charts
5. WHEN the cadence configuration changes, THE System SHALL recalculate and update Throughput metrics immediately

### Requirement 12: Flow Metrics - Blocking Ages

**User Story:** As a delivery manager, I want to measure time spent blocked, so that I can identify and address impediments.

#### Acceptance Criteria

1. THE System SHALL track the duration that Work_Item and Hypothesis cards spend in blocked status
2. WHEN an item is marked as blocked, THE System SHALL record the block start timestamp
3. WHEN an item is unblocked, THE System SHALL record the block end timestamp
4. THE System SHALL calculate Blocking_Age as the sum of all durations between block start and block end timestamps
5. THE System SHALL calculate Blocking_Age separately for Active_Stage and non-active stages
6. THE System SHALL display Blocking_Age metrics on a separate metrics view
7. THE System SHALL display Blocking_Age statistics: total time blocked, average block duration, count of blocks

### Requirement 13: Flow Load Tracking

**User Story:** As a delivery manager, I want to see total effort in the system, so that I can identify throughput risks.

#### Acceptance Criteria

1. THE System SHALL calculate Flow_Load as the sum of Effort_Level units across all Work_Item cards not in Done stage
2. THE System SHALL assign numeric values to Effort_Level: High=3, Medium=2, Low=1
3. THE System SHALL display Flow_Load as a summary metric at the top of the Work_Board
4. THE System SHALL highlight when Flow_Load contains high concentration of High Effort_Level items
5. WHEN Flow_Load changes, THE System SHALL update the display immediately

### Requirement 14: Flow Debt Tracking

**User Story:** As a strategist, I want to track invalidated experiments that created maintenance burden, so that I can understand the cost of failed hypotheses.

#### Acceptance Criteria

1. THE System SHALL allow marking completed Work_Item cards in Strategic Experiments Swimlane as "invalidated"
2. WHEN a Work_Item is marked as invalidated, THE System SHALL prompt whether it created maintenance burden
3. THE System SHALL increment Flow_Debt counter when an invalidated Work_Item created maintenance burden
4. THE System SHALL display Flow_Debt as a separate counter on the Work_Board
5. THE System SHALL allow viewing the list of Work_Item cards contributing to Flow_Debt

### Requirement 15: Metrics Visualization

**User Story:** As a delivery manager, I want to view flow metrics with real-time charts, so that I can analyze trends and make data-driven decisions.

#### Acceptance Criteria

1. THE System SHALL provide a separate metrics page accessible from both boards
2. THE System SHALL display charts for: Cycle_Time trends, Lead_Time trends, Throughput trends, Blocking_Age analysis
3. WHEN Flow_Metrics data changes, THE System SHALL update charts in real-time
4. THE System SHALL allow filtering metrics by Swimlane, date range, and Assignee
5. THE System SHALL allow exporting metrics data in CSV format

### Requirement 16: Data Persistence

**User Story:** As a user, I want all board data to persist, so that I can resume work across sessions.

#### Acceptance Criteria

1. THE System SHALL persist all Hypothesis data to the database
2. THE System SHALL persist all Work_Item data to the database
3. THE System SHALL persist all Flow_Metrics history to the database
4. WHEN a user loads a board, THE System SHALL retrieve current state from the database
5. WHEN a user makes changes, THE System SHALL save changes to the database immediately

### Requirement 17: Stage Transitions

**User Story:** As a user, I want to move cards between stages, so that I can reflect work progress.

#### Acceptance Criteria

1. THE System SHALL allow drag-and-drop movement of cards between adjacent stages
2. WHEN a card is moved to a new stage, THE System SHALL record the transition timestamp
3. THE System SHALL prevent moving cards to non-adjacent stages
4. WHEN a card enters an Active_Stage, THE System SHALL record the active work start time
5. WHEN a card exits an Active_Stage, THE System SHALL record the active work end time

### Requirement 18: Child Work Item Stage Movement

**User Story:** As a team member, I want to move child work items between stages independently, so that I can track sub-task progress while the parent automatically reflects the overall status.

#### Acceptance Criteria

1. THE System SHALL allow drag-and-drop movement of child Work_Item cards between adjacent stages
2. WHEN a child Work_Item card is moved to a new stage, THE System SHALL automatically update the parent Work_Item stage according to these rules:
   - IF all child Work_Item cards are in Done stage, THEN parent moves to Done stage
   - ELSE IF any child Work_Item card is in Implementation stage, THEN parent moves to Implementation stage
   - ELSE parent remains in its current stage or moves to the highest active stage among children
3. THE System SHALL record the transition timestamp for both child and parent stage changes
4. THE System SHALL prevent moving child Work_Item cards to non-adjacent stages
5. WHEN a parent Work_Item stage changes due to child movement, THE System SHALL display a visual indicator showing the automatic transition

### Requirement 19: Detail Page UI Clarity

**User Story:** As a user, I want to view item details in a clear, uncluttered interface, so that I can quickly understand the item's status and information.

#### Acceptance Criteria

1. THE System SHALL display detail pages as a separate full-page view (not a modal overlay)
2. WHEN a user clicks a Work_Item or Hypothesis card, THE System SHALL navigate to a dedicated detail page showing only essential information organized in logical sections
3. THE System SHALL organize detail page content into sections: Basic Info, Status, Relationships, and Metadata
4. THE System SHALL display parent/child relationships and linked hypotheses as clickable links within the detail page
5. WHEN a user clicks a parent, child, or linked hypothesis link on the detail page, THE System SHALL navigate to that item's detail page without requiring the user to go back to the board
6. THE System SHALL provide a clear visual hierarchy on the detail page with primary information prominent and secondary information de-emphasized
7. THE System SHALL display a back button and breadcrumb navigation showing the navigation path (e.g., "Board > Parent Item > Child Item")
8. THE System SHALL display navigation controls to move between related items (previous/next sibling, parent, etc.) without returning to the board

### Requirement 20: Child Item Count Display

**User Story:** As a user, I want to see at a glance how many child items each parent has, so that I can understand the scope of work breakdown.

#### Acceptance Criteria

1. THE System SHALL display the count of child Work_Item cards on parent Work_Item cards in the board view
2. THE System SHALL NOT display child counts on Hypothesis cards
3. THE System SHALL format the child count as a clickable badge or label on the parent card (e.g., "3 children" or "3 tasks")
4. WHEN a parent Work_Item has no children, THE System SHALL not display a child count badge
5. WHEN a user clicks the child count badge on a parent Work_Item card, THE System SHALL expand/collapse the list of child Work_Item cards inline below the parent card
6. WHEN expanded, THE System SHALL display all child Work_Item cards in a nested view below the parent card
7. THE System SHALL update the child count badge in real-time when children are added or removed
8. THE System SHALL display the child count in a visually distinct location on the card (e.g., bottom-right corner)
