# PawPal+ AI Schedule Coach

## Original project: PawPal+

PawPal+ is a Streamlit pet-care planning application. Its original goals were to help an owner:

- Add pets and describe their basic breed/species information.
- Create, edit through the existing task model, and complete care tasks.
- Record task duration, priority, due date, daily status, and scheduled time.
- Generate schedules for today and tomorrow.
- Exclude completed tasks and automatically create the next daily task instance.
- Sort tasks by high, medium, and low priority while preserving equal-priority order.
- Detect tasks that share the same scheduled time.

The original system separates the application interface in `app.py` from the pet, owner, task, and schedule classes in `pawpal_system.py`. Its core schedule is deterministic and can work without any external AI service.

## New project: AI Schedule Coach

The new project adds an agentic AI Schedule Coach to PawPal+. The owner supplies an available time budget, and the system asks an AI model to select relevant tasks and explain the result.

This matters because the original scheduler can rank and list tasks, but it does not interpret an owner's changeable time constraints or provide individualized planning language. The coach creates a constrained, reviewable recommendation while keeping the existing schedule engine as a reliable fallback.

## System design

The implementation follows the flow shown in `diagrams/architecture.mmd`:

1. **Input:** The human enters the available time, while the app provides owner preferences and task data.
2. **Retriever:** `Retriever` gathers incomplete tasks due today or tomorrow, including task IDs, descriptions, pets, durations, priorities, due dates, and scheduled times.
3. **Planner:** `OpenAIPlanner` sends the retrieved context to an OpenAI-compatible chat-completions API and requests JSON containing `task_ids` and `reasoning`.
4. **Validator:** `Validator` rejects unknown or duplicate IDs, completed tasks, proposals over budget, and schedule-time conflicts.
5. **Fallback planner:** If planning or validation fails, `_fallback` uses priority order and fills the remaining time budget.
6. **Display:** Streamlit shows the AI or fallback proposal and the selected tasks.
7. **Human review:** The owner decides whether to revise the budget or constraints. The AI cannot mark tasks complete or change pet/task records.

```text
Human input -> Retriever -> Planner -> Validator -> Display -> Human review
                                  |
                                  +-> Deterministic fallback on invalid/error

Automated tests validate the planner and validator independently.
```

## Running the code

### 1. Open the project

From a terminal, move into the project directory:

```powershell
cd C:\Users\Sandh\Documents\GitHub\applies-ai-system-project
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Run locally without AI

The deterministic fallback works without an API key:

```powershell
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal.

### 5. Optionally enable live AI

Set the API key and optionally select a model in PowerShell:

```powershell
$env:OPENAI_API_KEY="your-key"
$env:OPENAI_MODEL="gpt-4o-mini"
streamlit run app.py
```

In the app:

1. Add at least one pet.
2. Add one or more care tasks.
3. Enter the owner's available time in minutes.
4. Select **Generate AI plan**.
5. Review the proposed tasks, AI reasoning or fallback warning, and any schedule warnings.

The live provider is optional. Missing keys, provider errors, malformed responses, and invalid proposals fall back to deterministic planning.

## Sample interactions

### 1. Valid plan with enough time

**Input**

- Available time: 45 minutes
- Tasks: Morning walk, 30 minutes, high priority; Medication, 5 minutes, high priority; Grooming, 20 minutes, low priority

**Example AI output**

```text
AI proposal
"Select the Morning walk and Medication first because they are high priority
and fit within the 45-minute budget."

Morning walk: 30 minutes
Medication: 5 minutes
Total: 35 minutes
```

### 2. Unknown or invented task

**Input**

- Available time: 45 minutes
- The model proposes task ID `task-999`, which is not in the retrieved task list.

**Result**

```text
Fallback proposal
"The proposal referenced unknown task ID 'task-999'.
Using the deterministic priority fallback."

The proposed tasks are replaced by validated, in-budget tasks from the real task list.
```

### 3. Provider unavailable

**Input**

- Available time: 20 minutes
- The OpenAI API key is missing or the provider raises an error.

**Result**

```text
Fallback proposal
"Planner unavailable or returned an invalid response.
Using the deterministic priority fallback."

The existing priority sorter selects tasks that fit the 20-minute budget.
```

## Design decisions

### Why this implementation was used

- **Deterministic scheduling remains authoritative:** The model can explain and propose, but the local task objects and existing scheduler provide the fallback.
- **The AI is constrained by data:** The retriever supplies only incomplete tasks due today or tomorrow, and the planner is told to return only supplied task IDs.
- **Validation protects the user:** Invalid IDs, duplicate proposals, completed tasks, over-budget plans, and conflicting start times are rejected.
- **The AI has no write access:** It cannot complete tasks, create recurring tasks, change pets, or modify due dates.
- **Testing uses mock planners:** Unit tests can verify behavior without sending API requests or requiring credentials.

### Trade-offs

- Live planning currently depends on an external OpenAI-compatible API and network availability.
- AI responses are unreviewed for natural-language quality; code-level validation checks structure and scheduling constraints, not tone or every possible preference.
- The planner receives a text/JSON context rather than external pet-care documents, so this is an agentic workflow rather than retrieval-augmented generation over a knowledge base.
- The fallback does not assign start times or optimize around overlapping durations; it uses the existing project's priority and budget behavior.
- The UI allows the owner to review and revise constraints, but it does not yet provide an explicit approve/reject action or save the accepted plan.
- API usage may incur provider cost and has latency, privacy, and availability implications.

## Testing summary

Run the test suite from the project root:

```powershell
python -m pytest tests/test_pawpal.py tests/test_app.py -q
```

### What works

- Task creation, filtering, completion, recurrence, priority sorting, and scheduling tests.
- Unknown task IDs trigger the deterministic fallback.
- Provider exceptions trigger the deterministic fallback.
- Valid AI proposals within budget are accepted.
- Over-budget AI proposals trigger fallback behavior.
- Existing Streamlit UI tests continue to pass.
- At the time of the current implementation, 22 focused core and Streamlit tests passed.

### What does not yet work or is not verified

- A live OpenAI request was not verified without a valid API key and account.
- There is no dedicated test for every possible malformed JSON shape.
- The UI does not yet include an explicit approve/reject button for the AI plan.
- Conflict validation currently compares exact scheduled times; it does not detect overlapping duration ranges.
- Natural-language quality and the human usefulness of AI reasoning require manual review.
- Safety and privacy behavior for real owner data should be reviewed before deploying beyond a local demo.

## Reflection

<!-- Leave this section for personal reflection. -->
