# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Let a user mark tasks complete; completed tasks are excluded from new schedules
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
#Today's Schedule for Jordan
- Breakfast for Nori: 10 min (high priority)
- Morning walk for Mochi: 30 min (high priority)
- Playtime for Nori: 15 min (medium priority)
- Grooming for Mochi: 20 min (low priority)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
=========================================== test session starts ===========================================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Sandh\Documents\GitHub\ai110-module2show-pawpal-starter
plugins: anyio-4.14.2
collected 18 items                                                                                         

tests\test_app.py ..                                                                                 [ 11%]
tests\test_pawpal.py ................                                                                [100%]

=========================================== 18 passed in 6.46s ============================================
PS C:\Users\Sandh\Documents\GitHub\ai110-module2show-pawpal-starter> 
```
"Confidence Level: 5 Stars"

## AI Schedule Coach

PawPal+ includes an agentic AI schedule-coach workflow in
[`AIScheduleCoach/ai_schedule_coach.py`](AIScheduleCoach/ai_schedule_coach.py). The coach:

1. Retrieves incomplete tasks due today or tomorrow and the owner's available time.
2. Sends a constrained task list to an OpenAI-compatible planner.
3. Validates task IDs, completion status, duplicate conflicts, and the time budget.
4. Displays an AI result or a deterministic priority-sorted fallback.
5. Never modifies pets or tasks; the owner reviews the proposal before acting.

Set `OPENAI_API_KEY` to enable live AI planning. `OPENAI_MODEL` is optional and
defaults to `gpt-4o-mini`. Without a key or when the provider fails, the app uses
its local priority fallback.

```powershell
$env:OPENAI_API_KEY="your-key"
$env:OPENAI_MODEL="gpt-4o-mini"
streamlit run app.py
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Schedule.create_schedule` | Sorts tasks by priority: high, then medium, then low. Tasks with equal priority keep their existing order. Sorting does not assign start times. |
| Schedule dates and completion filtering | `Owner.create_schedule`, `Schedule.create_schedule` | Builds lists for today and tomorrow, excluding completed tasks. Overdue tasks are included in today's list; tasks due after tomorrow are not included. |
| Task filtering | `Owner.get_all_tasks`, `Owner.filter_tasks` | Retrieves all tasks across the owner's pets, then optionally filters by completion status, pet name, or both. Pet names are matched case-insensitively after trimming whitespace; an empty pet name raises `ValueError`. |
| Time conflict detection | `Schedule.get_conflict_warnings` | On each scheduled date, warns when at least two tasks have the exact same non-empty scheduled start time, including tasks for the same or different pets. It does not detect overlapping durations. |
| Daily recurring tasks | `Task.mark_complete`, `Pet.add_task` | Completing a daily task creates and attaches a new, incomplete instance due tomorrow, retaining its description, duration, priority, daily setting, and scheduled time. Completing it again does not create another instance; non-daily tasks do not recur. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
