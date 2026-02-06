## Role: 
act as a senior fronend engineer.

## context: 
i want to develop kanban board system that allow me to track my strategic hypothesis and its tactical experiments.

each hypothesis can have multiple experiments.

each hypothesis have the following template.

## **Hypothesis Canvas**

**Business value**

*What is the business value associated with this hypothesis?*

[Enter your answer here]

**Problem**

*What is the problem we are trying to solve?*

[Enter your answer here]

**Customers**

*Who is impacted by this problem?*

[Enter your answer here]

---

**Hypothesis**

*What do we believe?*

We believe that **[__________________]** will result in **[__________________]**.

We will know we’ve succeeded when **[_______________]**.

---

**Metrics**

*Record a baseline of key metrics for this hypothesis.*

[Enter your answer here]

---

**Solutions/Ideas**

*How might we solve this problem?*

[Enter your answer here]

**Lessons learned**

*Record our lessons learned.*

[Enter your answer here]

each experiment should have the following template

**Title**

*Name your experiment*

[Enter your experiment name here]

---

**Goals**

*Which of your goals does this experiment align to? List all that apply.*

- [Goal 1]
- [Goal 2]

---

**Description**

*Describe the experiment. Provide some background on the current state and what it is you want to do.*

[Enter the experiment description here]

---

**Acceptance Criteria**

*List your acceptance criteria*

- [Acceptance Criterion 1]
- [Acceptance Criterion 2]

So i should have two board views:
1. Strategic Hypothesis Board: check the strategic hypothesis.
2. Work delivery Board: the experiment delivery board.

Stages:
Strategic hypothesis board: [In Queue, review, execution, review, done.]
Work delivery Board: [queue, design, design-review, implementation, cr-review, deploy, release, Done.]

Rigor level:
Work Delivery Board: each work item should have a rigor level and effort with (H,M,L)

Effort level: 
Work Delivery Board: each work item should have a effort level and effort with (H,M,L)

Active Stages: 
Work delivery Board[in active stages: design review, cr review, deploy, release]
Strategic Hypothesis: [active stages: design, implementation]

Status:
Each active stages have blocker, once clicked, the blocker reasons must be proavided.

Swimlanes:
**1. Strategic Experiments (Value Drivers):**
This lane is strictly for work items linked to your **Hypothesis Canvas**. This is your "Offense."

**2. Tactical Debt & Cleanup (Value Enablers):**
This lane is for refactoring, documentation, and tooling. This is your 
"Maintenance." It doesn't have a strategic outcome, but it reduces 
future **Lead Time (LT)**.

**3. Defects & Support (Failure Demand):**
This lane is for bugs and production issues. This is your "Defense." High volume here indicates a need to increase the **Rigor Level** on your Experiments.


Metric Views:
1. cycle time: starts from design to Done.
2. lead time: starts from queue to Done.
3. throughput: number of dones within a given cadence e.g. 1 week, 2 week, x week.
4. blocking ages for in active and active stages. [active stages can also be blocked and become inactive too.]

Additional Requirements:
1. i want both boards (Strategic Hypothesis + Work Delivery) to switch between them via tabs?
2. **Flow Load (WIP on Steroids):** Instead of just counting cards, calculate the total "Effort" units in the system. If your Experiment Board has a high concentration of "High Effort" (H) items in the "Implementation" stage, your throughput will plummet regardless of your card count.
3. **Flow Debt:** Track how many experiments in "Done" were invalidated (i.e., the hypothesis failed) but resulted in code or processes that now require maintenance.
4. delivery work item must be visually linked to their parent hypothesis (like cards with connectors).
5. For the strategic hypothesis cards - all those canvas fields be only visible in a detail modal?
6. For work item cards - how much info should be visible at a glance? Just title + stage, and rigor/effort levels, assigner.
7. swimlanes could be collapsible? no color preference
8. When marking something as blocked -  a structured form (blocker type, severity, owner).
9.  metrics must be on a separate view/page, I want real-time charts 
10. Flow Load be displayed as a summary metric at the top of the board.
11. For Flow Debt - i want to track this as a separate counter.

## Tasks: 
can we start iterate on the ui design and plan and ask me questions about the specific ui detail.
