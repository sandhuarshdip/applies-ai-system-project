# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Implement the AI Schedule Coach described in the architecture diagram, including retrieval,
AI planning, validation, deterministic fallback, Streamlit display, and tests.

**What did the agent do?**

Created `AIScheduleCoach/ai_schedule_coach.py`, connected it to `app.py`, added mock-planner tests,
and documented the `OPENAI_API_KEY` setup in `README.md`.

**What did you have to verify or fix manually?**

Verified existing Streamlit button behavior and the 22 core/UI tests. Confirmed that
AI plans cannot mutate tasks and that provider errors or invalid proposals use the
deterministic fallback.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
