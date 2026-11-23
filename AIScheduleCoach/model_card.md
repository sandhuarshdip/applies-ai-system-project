# PawPal+ AI Reflection and Model Card

## Learning to Use AI While Building Software

This project taught me how to use AI as a programming partner rather than as someone who should simply produce the finished code. I used AI to brainstorm the system design, create parts of the implementation, debug errors, and add or update tests. I learned that good prompts need clear goals and useful context. For example, a prompt with details about PawPal+'s classes, constraints, and expected behavior produced a more accurate change than a vague request to "fix the code."

## Problem-Solving Process

When I encountered a problem, I first described the expected behavior and identified the relevant classes or tests. I then asked AI to propose a solution or explain a likely cause. I did not treat its answer as automatically correct. I reviewed the changed lines, considered whether they matched my design, ran the tests, and ran the application when needed. This process helped me catch incorrect assumptions and separate a real implementation problem from a test that had the wrong expectations.

## Accepted AI Suggestion

One useful suggestion I accepted was to add an explicit time constraint to tasks and a relationship from each task to a pet. In the earlier skeleton, tasks did not clearly belong to a particular pet, and the model did not account for a scheduled task time. I accepted this suggestion because PawPal+ is designed for an owner who may manage several pets, so task ownership and a daily schedule need to be represented clearly. The resulting design uses `Pet.add_task` to attach a task to a pet and a task's `scheduled_time` for conflict detection.

## Verifying AI-Generated Work

AI generated code often needed verification. I checked changes in the affected files, ran targeted and full pytest suites, and looked for behavior that could violate project requirements. I also rejected suggestions that conflicted with the project goals. For example, I did not accept an extended repeating-task feature that introduced an arbitrary interval. A simpler daily-task recurrence model better matched the scenario and was easier to explain and test.

## System Limitations

AI systems can misunderstand a prompt, produce plausible-looking code that contains subtle bugs, or make changes outside the requested scope. They do not reliably know whether a design choice is appropriate unless that choice and its constraints are explained. The AI schedule coach also depends on an external OpenAI-compatible provider, so network or API failures are possible. PawPal+ limits this risk by validating proposed task IDs and time budgets and falling back to a deterministic priority-sorted schedule when AI output is unavailable or invalid.

The scheduling system has broader limitations as well. It sorts incomplete tasks by priority for today and tomorrow, but it does not optimize around every possible preference or produce exact conflict-free start times. Its total-time budget is a constraint for the AI coach, not a complete capacity model: task durations and overlapping scheduled times can still require owner judgment. Tests and manual review improve confidence, but they do not prove every possible real-world schedule is correct.

## Potential Misuse and Prevention

The AI could be misused if someone relies on it without checking the proposal, if task or owner text contains malicious instructions, or if private planning data is sent to a provider unnecessarily. A user could also be shown a schedule that is harmful or inappropriate because the model is not an expert in pet health or emergency care. I prevent this by limiting the model to a JSON planning response, sending only the task fields needed for scheduling, keeping API credentials in environment variables, and never allowing the AI to edit pets or tasks directly. The owner must review the result, while the validator rejects unknown task IDs, completed tasks, duplicate IDs, time conflicts, and proposals over budget. Any provider failure or invalid result uses the deterministic fallback.

## What Surprised Me About AI Reliability

I was surprised that testing the AI was less about whether it returned one correct answer and more about whether the application stayed safe when it was wrong. Invalid or unavailable AI output was handled naturally when the provider returned an error, the proposal named an unknown task, or the proposal exceeded the available time. The tests showed that the system could remain reliable even though the model itself was not perfect. I also learned that a fallback can be a good feature rather than a failure: it keeps the app useful and makes it clear to the user when the deterministic system took over.
