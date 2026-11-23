"""Agentic AI Schedule Coach for PawPal+.

The coach can retrieve task context and ask an external model for a proposal.
It validates every proposed task before displaying it and falls back to the
deterministic scheduler whenever planning or validation fails.
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol

from pawpal_system import Owner, Task


@dataclass(frozen=True)
class ScheduleProposal:
    task_ids: list[str]
    reasoning: str
    source: str


@dataclass(frozen=True)
class RetrievedContext:
    owner_name: str
    preference: str
    available_minutes: int
    tasks: list[dict[str, object]]


class Planner(Protocol):
    def plan(self, context: RetrievedContext) -> ScheduleProposal:
        """Return a proposal for the retrieved context."""


class OpenAIPlanner:
    """Small OpenAI-compatible chat-completions client."""

    def plan(self, context: RetrievedContext) -> ScheduleProposal:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")

        payload = {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a pet-care scheduling assistant. Only choose task IDs "
                        "from the supplied JSON. Do not invent tasks. Return JSON with "
                        'keys "task_ids" and "reasoning".'
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "available_minutes": context.available_minutes,
                            "owner_preference": context.preference,
                            "tasks": context.tasks,
                        }
                    ),
                },
            ],
        }

        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))

        content = result["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        task_ids = parsed.get("task_ids")
        reasoning = parsed.get("reasoning")
        if not isinstance(task_ids, list) or not all(
            isinstance(task_id, str) for task_id in task_ids
        ):
            raise ValueError("The planner returned invalid task_ids.")
        if not isinstance(reasoning, str) or not reasoning.strip():
            raise ValueError("The planner returned invalid reasoning.")

        return ScheduleProposal(task_ids, reasoning.strip(), "AI")


class Retriever:
    def retrieve(self, owner: Owner, available_minutes: int) -> tuple[
        RetrievedContext,
        dict[str, Task],
    ]:
        tasks = [
            task
            for task in owner.get_all_tasks()
            if not task.completed
            and task.due_date <= date.today() + timedelta(days=1)
        ]
        task_map: dict[str, Task] = {}
        context_tasks: list[dict[str, object]] = []

        for index, task in enumerate(tasks):
            task_id = f"task-{index}"
            task_map[task_id] = task
            context_tasks.append(
                {
                    "task_id": task_id,
                    "description": task.description,
                    "pet": task.pet.pet_name if task.pet is not None else "Unassigned",
                    "duration_minutes": task.time_to_complete,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat(),
                    "scheduled_time": (
                        task.scheduled_time.isoformat()
                        if task.scheduled_time is not None
                        else None
                    ),
                }
            )

        return (
            RetrievedContext(
                owner_name=owner.owner_name,
                preference=owner.preference,
                available_minutes=available_minutes,
                tasks=context_tasks,
            ),
            task_map,
        )


class Validator:
    def validate(
        self,
        proposal: ScheduleProposal,
        context: RetrievedContext,
        task_map: dict[str, Task],
    ) -> tuple[list[Task], str | None]:
        if proposal.task_ids != list(dict.fromkeys(proposal.task_ids)):
            return [], "The proposal contained duplicate task IDs."

        selected: list[Task] = []
        total_minutes = 0
        scheduled_times: dict[str, str] = {}

        for task_id in proposal.task_ids:
            task = task_map.get(task_id)
            if task is None:
                return [], f"The proposal referenced unknown task ID {task_id!r}."
            if task.completed:
                return [], f"The proposal included completed task {task.description!r}."

            total_minutes += task.time_to_complete
            if total_minutes > context.available_minutes:
                return [], "The proposal exceeded the owner's available time."

            if task.scheduled_time is not None:
                time_key = task.scheduled_time.isoformat()
                if time_key in scheduled_times:
                    return [], "The proposal included conflicting scheduled times."
                scheduled_times[time_key] = task.description
            selected.append(task)

        return selected, None


class AIScheduleCoach:
    """Coordinates retrieval, planning, validation, display data, and fallback."""

    def __init__(self, planner: Planner | None = None) -> None:
        self.retriever = Retriever()
        self.planner = planner or OpenAIPlanner()
        self.validator = Validator()

    def create_plan(
        self,
        owner: Owner,
        available_minutes: int,
    ) -> tuple[ScheduleProposal, list[Task], str | None]:
        if available_minutes <= 0:
            raise ValueError("Available time must be greater than zero minutes.")

        context, task_map = self.retriever.retrieve(owner, available_minutes)
        try:
            proposal = self.planner.plan(context)
            selected, validation_error = self.validator.validate(
                proposal,
                context,
                task_map,
            )
        except Exception as error:
            validation_error = f"Planner unavailable or returned an invalid response: {error}"
            proposal = None
            selected = []

        if proposal is not None and validation_error is None:
            return proposal, selected, None

        fallback_tasks = self._fallback(context, task_map)
        fallback_reason = (
            validation_error or "The AI proposal could not be used."
        ) + " Using the deterministic priority fallback."
        return (
            ScheduleProposal(
                task_ids=[f"task-{index}" for index, task in enumerate(task_map.values())
                          if task in fallback_tasks],
                reasoning=fallback_reason,
                source="Fallback",
            ),
            fallback_tasks,
            fallback_reason,
        )

    @staticmethod
    def _fallback(
        context: RetrievedContext,
        task_map: dict[str, Task],
    ) -> list[Task]:
        priority_order = {"high": 0, "medium": 1, "low": 2}
        candidates = sorted(
            task_map.values(),
            key=lambda task: priority_order[task.priority.lower()],
        )
        selected: list[Task] = []
        total_minutes = 0
        for task in candidates:
            if total_minutes + task.time_to_complete <= context.available_minutes:
                selected.append(task)
                total_minutes += task.time_to_complete
        return selected
