# Implementation Plan: Dual-Board Kanban System

## Overview

This implementation plan breaks down the dual-board kanban system into discrete, manageable coding tasks organized by architectural layer. The approach follows clean architecture principles, starting with domain layer foundations, moving through application services, infrastructure persistence, and finally UI components. Each task builds incrementally on previous work, with property-based tests validating correctness properties throughout.

## Tasks

- [x] 1. Set up project structure and core infrastructure
  - Create directory structure for domain, application, infrastructure, and UI layers
  - Set up testing framework (pytest, hypothesis for property-based testing)
  - Create base classes and interfaces for repositories and services
  - Set up SQLite database connection and migration system
  - _Requirements: 16.1, 16.2, 16.3_

- [ ] 2. Implement domain layer - Value Objects and Stage management
  - [x] 2.1 Implement Stage value object with board type and adjacency logic
    - Create Stage class with name, board_type, is_active, order attributes
    - Implement get_strategic_stages() and get_work_delivery_stages() static methods
    - Implement is_adjacent_to() method for stage transition validation
    - _Requirements: 2.1, 3.1, 17.3_
  
  - [ ]* 2.2 Write property test for Stage adjacency validation
    - **Property 3: Adjacent Stage Transitions**
    - **Validates: Requirements 2.3, 3.4, 17.3**
  
  - [x] 2.3 Implement Blocker value object
    - Create Blocker class with blocker_type, severity, owner, reason, blocked_at, unblocked_at
    - Implement get_blocking_duration() method
    - _Requirements: 8.1, 8.2, 12.1_
  
  - [ ]* 2.4 Write property test for Blocker duration calculation
    - **Property 12: Blocking Age Calculation**
    - **Validates: Requirements 12.1, 12.4**

- [ ] 3. Implement domain layer - Hypothesis entity
  - [x] 3.1 Create Hypothesis entity class
    - Implement id, business_value, problem_statement, customers_impacted, hypothesis_statement, metrics_baseline, solutions_ideas, lessons_learned attributes
    - Implement stage and stage_transitions tracking
    - Implement move_to_stage() method
    - Implement is_in_active_stage() method
    - Implement get_linked_work_items_summary() method
    - _Requirements: 2.2, 2.3, 2.4, 4.1_
  
  - [ ]* 3.2 Write property test for Hypothesis creation initialization
    - **Property 1: Hypothesis Creation Initialization**
    - **Validates: Requirements 2.2**
  
  - [ ]* 3.3 Write property test for Hypothesis statement format validation
    - **Property 5: Hypothesis Statement Format Validation**
    - **Validates: Requirements 4.5**
  
  - [ ]* 3.4 Write property test for Active stage classification
    - **Property 4: Active Stage Classification**
    - **Validates: Requirements 2.4, 3.5**

- [ ] 4. Implement domain layer - WorkItem entity
  - [x] 4.1 Create WorkItem entity class
    - Implement id, title, goals, description, acceptance_criteria attributes
    - Implement rigor_level, effort_level, assignee, swimlane attributes
    - Implement stage, parent_hypothesis_id, parent_work_item_id, child_work_item_ids
    - Implement blocker, is_invalidated, created_maintenance_burden attributes
    - Implement move_to_stage() method
    - Implement is_in_active_stage() method
    - Implement mark_blocked() and unblock() methods
    - Implement can_have_children() and can_have_parent() methods
    - Implement add_child() and set_parent() methods
    - Implement check_children_completion() method
    - Implement get_effort_units() method (High=3, Medium=2, Low=1)
    - Implement get_child_count() method
    - _Requirements: 3.3, 5.1, 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ]* 4.2 Write property test for WorkItem creation initialization
    - **Property 2: Work Item Creation Initialization**
    - **Validates: Requirements 3.3**
  
  - [ ]* 4.3 Write property test for Effort level value mapping
    - **Property 6: Effort Level Value Mapping**
    - **Validates: Requirements 13.2**
  
  - [ ]* 4.4 Write property test for Parent-child hierarchy depth limit
    - **Property 8: Parent-Child Hierarchy Depth Limit**
    - **Validates: Requirements 7.3, 7.4, 7.5**
  
  - [ ]* 4.5 Write property test for Work item requires parent hypothesis
    - **Property 7: Work Item Requires Parent Hypothesis**
    - **Validates: Requirements 6.1, 6.6**

- [ ] 5. Implement domain layer - FlowMetrics service
  - [x] 5.1 Create FlowMetrics domain service
    - Implement calculate_cycle_time() method (Design → Done)
    - Implement calculate_lead_time() method (Queue → Done)
    - Implement calculate_throughput() method with cadence support
    - Implement calculate_blocking_ages() method
    - Implement calculate_flow_load() method (sum of effort units not in Done)
    - Implement calculate_flow_debt() method (invalidated experiments with maintenance burden)
    - _Requirements: 9.1, 10.1, 11.1, 12.1, 13.1, 14.3_
  
  - [ ]* 5.2 Write property test for Cycle time calculation
    - **Property 13: Cycle Time Calculation**
    - **Validates: Requirements 9.1**
  
  - [ ]* 5.3 Write property test for Lead time calculation
    - **Property 14: Lead Time Calculation**
    - **Validates: Requirements 10.1**
  
  - [ ]* 5.4 Write property test for Throughput calculation
    - **Property 15: Throughput Calculation**
    - **Validates: Requirements 11.1**
  
  - [ ]* 5.5 Write property test for Flow load calculation
    - **Property 16: Flow Load Calculation**
    - **Validates: Requirements 13.1**
  
  - [ ]* 5.6 Write property test for Flow load high concentration detection
    - **Property 17: Flow Load High Concentration Detection**
    - **Validates: Requirements 13.4**
  
  - [ ]* 5.7 Write property test for Flow debt increment
    - **Property 18: Flow Debt Increment**
    - **Validates: Requirements 14.3**

- [ ] 6. Implement infrastructure layer - Database schema and repositories
  - [x] 6.1 Create database schema
    - Create hypotheses table with all canvas fields
    - Create work_items table with all work item fields
    - Create work_item_children junction table for parent-child relationships
    - Create stage_transitions table for tracking all transitions
    - Create blockers table for tracking blocking information
    - Create flow_metrics_snapshots table for metrics history
    - Set up foreign key constraints and indexes
    - _Requirements: 16.1, 16.2, 16.3_
  
  - [x] 6.2 Implement HypothesisRepository
    - Implement save() method
    - Implement find_by_id() method
    - Implement find_all() method
    - Implement find_by_stage() method
    - _Requirements: 16.1, 16.4_
  
  - [ ]* 6.3 Write property test for Hypothesis persistence round trip
    - **Property 19: Hypothesis Persistence Round Trip**
    - **Validates: Requirements 16.1, 16.4**
  
  - [x] 6.4 Implement WorkItemRepository
    - Implement save() method
    - Implement find_by_id() method
    - Implement find_all() method
    - Implement find_by_hypothesis() method
    - Implement find_by_parent() method
    - Implement find_not_done() method
    - Implement find_completed_in_period() method
    - _Requirements: 16.2, 16.4_
  
  - [ ]* 6.5 Write property test for WorkItem persistence round trip
    - **Property 20: Work Item Persistence Round Trip**
    - **Validates: Requirements 16.2, 16.4**
  
  - [x] 6.6 Implement FlowHistoryRepository
    - Implement save_snapshot() method
    - Implement find_snapshots_in_period() method
    - _Requirements: 16.3_

- [ ] 7. Implement application layer - Board service
  - [x] 7.1 Create BoardService
    - Implement get_strategic_board() method returning StrategicBoardView
    - Implement get_work_delivery_board() method returning WorkDeliveryBoardView
    - Implement move_hypothesis() method with stage validation
    - Implement move_work_item() method with stage validation and parent auto-update logic
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.3, 3.1, 3.4, 17.1, 17.2, 17.3_
  
  - [ ]* 7.2 Write property test for Stage transition recording
    - **Property 21: Stage Transition Recording**
    - **Validates: Requirements 17.2**
  
  - [ ]* 7.3 Write property test for Active stage time recording
    - **Property 22: Active Stage Time Recording**
    - **Validates: Requirements 17.4, 17.5**

- [ ] 8. Implement application layer - Hypothesis service
  - [x] 8.1 Create HypothesisService
    - Implement create_hypothesis() method with canvas data validation
    - Implement update_hypothesis() method
    - Implement get_hypothesis_details() method returning HypothesisDetailView
    - Implement get_linked_work_items_summary() method
    - Implement mark_blocked() method with blocker validation
    - Implement unblock() method
    - _Requirements: 4.2, 4.3, 6.2, 6.3, 8.1, 8.2, 8.5, 8.6_
  
  - [ ]* 8.2 Write property test for Hypothesis work items summary accuracy
    - **Property 23: Hypothesis Work Items Summary Accuracy**
    - **Validates: Requirements 6.5**

- [ ] 9. Implement application layer - WorkItem service
  - [x] 9.1 Create WorkItemService
    - Implement create_work_item() method with parent hypothesis requirement
    - Implement update_work_item() method
    - Implement get_work_item_details() method returning WorkItemDetailView
    - Implement mark_blocked() method with blocker validation
    - Implement unblock() method
    - Implement add_child_work_item() method with hierarchy validation
    - Implement remove_child_work_item() method
    - Implement set_parent_work_item() method with hierarchy validation
    - Implement mark_invalidated() method with maintenance burden tracking
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 6.1, 6.6, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.5, 8.6, 14.1, 14.2_
  
  - [ ]* 9.2 Write property test for Parent completion on all children done
    - **Property 9: Parent Completion on All Children Done**
    - **Validates: Requirements 7.6**
  
  - [ ]* 9.3 Write property test for Blocking requires active stage
    - **Property 10: Blocking Requires Active Stage**
    - **Validates: Requirements 8.1**
  
  - [ ]* 9.4 Write property test for Blocking requires complete information
    - **Property 11: Blocking Requires Complete Information**
    - **Validates: Requirements 8.2**

- [ ] 10. Implement application layer - Metrics service
  - [x] 10.1 Create MetricsService
    - Implement get_cycle_time_metrics() method with filters
    - Implement get_lead_time_metrics() method with filters
    - Implement get_throughput_metrics() method with cadence and filters
    - Implement get_blocking_age_metrics() method with filters
    - Implement get_flow_load() method
    - Implement get_flow_debt() method
    - Implement export_metrics_csv() method
    - _Requirements: 9.2, 9.3, 10.2, 10.3, 11.2, 11.3, 11.4, 11.5, 12.6, 12.7, 13.3, 13.4, 13.5, 14.4, 14.5, 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [ ]* 10.2 Write property test for Metrics filter application
    - **Property 24: Metrics Filter Application**
    - **Validates: Requirements 15.4**
  
  - [ ]* 10.3 Write property test for Cadence recalculation reactivity
    - **Property 25: Cadence Recalculation Reactivity**
    - **Validates: Requirements 11.5**

- [ ] 11. Implement application layer - DetailPage service
  - [x] 11.1 Create DetailPageService
    - Implement get_work_item_detail() method returning WorkItemDetailView
    - Implement get_hypothesis_detail() method returning HypothesisDetailView
    - Implement get_breadcrumb_path() method for navigation history
    - Implement get_sibling_navigation() method for previous/next navigation
    - _Requirements: 19.2, 19.3, 19.4, 19.5, 19.7, 19.8_
  
  - [ ]* 11.2 Write property test for Child work item stage movement
    - **Property 26: Child Work Item Stage Movement**
    - **Validates: Requirements 18.1**
  
  - [ ]* 11.3 Write property test for Parent auto-update on child stage change
    - **Property 27: Parent Auto-Update on Child Stage Change**
    - **Validates: Requirements 18.2**
  
  - [ ]* 11.4 Write property test for Stage transition recording for parent-child
    - **Property 28: Stage Transition Recording for Parent-Child**
    - **Validates: Requirements 18.3**
  
  - [ ]* 11.5 Write property test for Child stage movement adjacency validation
    - **Property 29: Child Stage Movement Adjacency Validation**
    - **Validates: Requirements 18.4**
  
  - [ ]* 11.6 Write property test for Detail page data completeness
    - **Property 30: Detail Page Data Completeness**
    - **Validates: Requirements 19.3**
  
  - [ ]* 11.7 Write property test for Detail page relationship links
    - **Property 31: Detail Page Relationship Links**
    - **Validates: Requirements 19.4, 19.5**
  
  - [ ]* 11.8 Write property test for Breadcrumb navigation data
    - **Property 32: Breadcrumb Navigation Data**
    - **Validates: Requirements 19.7**
  
  - [ ]* 11.9 Write property test for Sibling navigation data
    - **Property 33: Sibling Navigation Data**
    - **Validates: Requirements 19.8**

- [ ] 12. Implement child count badge functionality
  - [x] 12.1 Add child count display logic to WorkItemCardView
    - Implement child_count field in card view model
    - Implement logic to populate child count from work item entity
    - _Requirements: 20.1, 20.3_
  
  - [ ]* 12.2 Write property test for Child count display on parent cards
    - **Property 34: Child Count Display on Parent Cards**
    - **Validates: Requirements 20.1**
  
  - [ ]* 12.3 Write property test for No child count on hypothesis cards
    - **Property 35: No Child Count on Hypothesis Cards**
    - **Validates: Requirements 20.2**
  
  - [ ]* 12.4 Write property test for Child count badge formatting
    - **Property 36: Child Count Badge Formatting**
    - **Validates: Requirements 20.3**
  
  - [ ]* 12.5 Write property test for No child count badge for childless items
    - **Property 37: No Child Count Badge for Childless Items**
    - **Validates: Requirements 20.4**
  
  - [ ]* 12.6 Write property test for Child count badge expandable data
    - **Property 38: Child Count Badge Expandable Data**
    - **Validates: Requirements 20.5, 20.6**
  
  - [ ]* 12.7 Write property test for Child count real-time update
    - **Property 39: Child Count Real-Time Update**
    - **Validates: Requirements 20.7**

- [x] 13. Checkpoint - Verify domain and application layers
  - Ensure all domain entities and value objects are implemented correctly
  - Ensure all application services are wired together properly
  - Ensure all property tests pass (minimum 100 iterations each)
  - Ensure all unit tests pass for domain and application layers
  - _Requirements: All domain and application layer requirements_

- [ ] 14. Implement UI layer - Board views and navigation
  - [x] 14.1 Create board UI components
    - Implement tab-based navigation between Strategic Board and Work Board
    - Implement Strategic Board view with stages: In Queue, Review, Execution, Done
    - Implement Work Board view with stages: Queue, Design, Design-Review, Implementation, CR-Review, Deploy, Release, Done
    - Implement swimlane display: Strategic Experiments, Tactical Debt & Cleanup, Defects & Support
    - Implement swimlane collapse/expand functionality
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 3.1, 3.2, 3.6_
  
  - [x] 14.2 Create card components
    - Implement Hypothesis card display with hypothesis statement and work items summary
    - Implement Work Item card display with title, rigor, effort, assignee
    - Implement blocked indicator display on cards
    - Implement child count badge on parent work item cards
    - _Requirements: 3.2, 5.3, 6.5, 8.3, 20.1, 20.3_
  
  - [x] 14.3 Implement drag-and-drop stage transitions
    - Implement drag-and-drop movement between adjacent stages
    - Implement visual feedback during drag operations
    - Implement stage transition validation (adjacent stages only)
    - Implement parent auto-update on child stage change
    - _Requirements: 17.1, 18.1, 18.2, 18.4_

- [ ] 15. Implement UI layer - Detail pages
  - [x] 15.1 Create detail page layout and navigation
    - Implement full-page detail view (not modal)
    - Implement back button and breadcrumb navigation
    - Implement navigation controls (previous/next sibling, parent)
    - Implement section organization: Basic Info, Status, Relationships, Metadata
    - _Requirements: 19.1, 19.2, 19.3, 19.6, 19.7, 19.8_
  
  - [x] 15.2 Implement Work Item detail page
    - Display title, goals, description, acceptance criteria
    - Display rigor level, effort level, assignee, swimlane
    - Display current stage and stage history
    - Display parent hypothesis link (clickable)
    - Display parent work item link if applicable (clickable)
    - Display child work items list (clickable)
    - Display blocker information if blocked
    - Display created/updated dates
    - Display invalidation status
    - _Requirements: 5.4, 6.3, 7.11, 19.2, 19.3, 19.4, 19.5_
  
  - [x] 15.3 Implement Hypothesis detail page
    - Display all canvas fields: business value, problem statement, customers impacted, hypothesis statement, metrics baseline, solutions/ideas, lessons learned
    - Display current stage and stage history
    - Display linked work items list (clickable)
    - Display blocker information if blocked
    - Display created/updated dates
    - _Requirements: 4.3, 6.3, 19.2, 19.3, 19.4, 19.5_

- [ ] 16. Implement UI layer - Child count badge expansion
  - [x] 16.1 Implement child count badge interaction
    - Display child count as clickable badge on parent cards
    - Implement expand/collapse toggle on badge click
    - Display child work items inline below parent when expanded
    - Update child count in real-time when children added/removed
    - _Requirements: 20.3, 20.4, 20.5, 20.6, 20.7_

- [ ] 17. Implement UI layer - Blocking management
  - [x] 17.1 Create blocking UI components
    - Implement blocked indicator display on cards
    - Implement blocking modal/form for marking items as blocked
    - Implement blocker type, severity, owner, reason input fields
    - Implement unblock button on blocked items
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [ ] 18. Implement UI layer - Metrics dashboard
  - [x] 18.1 Create metrics page layout
    - Implement separate metrics page accessible from both boards
    - Implement chart display for: Cycle Time trends, Lead Time trends, Throughput trends, Blocking Age analysis
    - Implement real-time chart updates when metrics data changes
    - _Requirements: 15.1, 15.2, 15.3_
  
  - [x] 18.2 Implement metrics filtering and export
    - Implement filter controls: swimlane, date range, assignee
    - Implement CSV export functionality
    - _Requirements: 15.4, 15.5_

- [x] 19. Checkpoint - Verify UI layer and end-to-end flows
  - Ensure all UI components render correctly
  - Ensure board navigation works between Strategic and Work boards
  - Ensure drag-and-drop stage transitions work correctly
  - Ensure detail page navigation works (breadcrumbs, sibling navigation, parent/child links)
  - Ensure child count badge expansion works
  - Ensure metrics dashboard displays correctly
  - Ensure all integration tests pass
  - _Requirements: All UI layer requirements_

- [x] 20. Implement data persistence and migrations
  - [x] 20.1 Create database migration system
    - Implement migration runner for schema creation
    - Implement migration versioning
    - _Requirements: 16.1, 16.2, 16.3_
  
  - [x] 20.2 Implement data export and backup
    - Implement CSV export for all entities
    - Implement backup functionality
    - _Requirements: 15.5_

- [x] 21. Final checkpoint - Complete system validation
  - Ensure all 39 property-based tests pass (100+ iterations each)
  - Ensure all unit tests pass with minimum 80% code coverage
  - Ensure all integration tests pass
  - Ensure all error handling works correctly
  - Ensure data persistence works end-to-end
  - Ensure metrics calculations are accurate
  - Ensure UI is responsive and functional
  - _Requirements: All requirements_

## Notes

- Tasks marked with `*` are optional property-based tests and can be skipped for faster MVP, but are strongly recommended for correctness validation
- Each task references specific requirements for traceability
- Property-based tests use the `hypothesis` library with minimum 100 iterations per test
- All tests should follow the tag format: `# Feature: dual-board-kanban, Property {number}: {property_text}`
- Checkpoints ensure incremental validation and catch issues early
- Parent auto-update logic is critical for maintaining data consistency when children move between stages
- Detail page navigation should allow users to explore related items without returning to the board
- Child count badge expansion provides inline visibility of work breakdown without leaving the board view
