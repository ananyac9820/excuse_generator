from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class ExcuseRequest:
    category: str
    audience: str
    tone: str
    specificity: int
    length: str
    custom_context: str | None = None
    seed: int | None = None
    persist_history: bool = False
    persist_dir: str | None = None


class ExcuseGenerator:
    def __init__(self) -> None:
        self.random = random.Random()
        self.templates: Dict[str, Dict[str, List[str]]] = self._load_templates()

    def _load_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Return a mapping: category -> tone -> list[template]."""
        # Minimal in-code templates; could be extended to load from JSON assets
        return {
            "General": {
                "Professional": [
                    "Sorry for the short notice. Something unexpected came up, so I can't {action} by {timeframe}. I'll share a simple plan and new time.",
                    "Apologies—an issue popped up and needs my attention. I'll update on {deliverable} by {new_time}.",
                ],
                "Casual": [
                    "Sorry—something came up, so I can't {action} today. Can we do {new_time}?",
                    "Hey, quick heads-up: I'm tied up last minute. Can we move {action} to {new_time}?",
                ],
                "Sincere": [
                    "Thanks for understanding. A personal thing came up, so I can't {action} as planned. I'll follow up by {new_time}.",
                ],
                "Brief": [
                    "Sorry—unexpected issue. Can't {action} by {timeframe}. Update by {new_time}.",
                ],
                "Light-hearted": [
                    "Looks like I double-booked myself. Can we move {action} to {new_time}?",
                ],
            },
            "Work Deadline": {
                "Professional": [
                    "I hit a blocker on {deliverable}. I won't make today's deadline. I'll send a simple plan and new ETA by {new_time}.",
                ],
                "Sincere": [
                    "I'm sorry—something urgent slowed down {deliverable}. I'll focus on it and share a new time by {new_time}.",
                ],
                "Brief": [
                    "Delay on {deliverable} due to a blocker. New ETA {new_time}.",
                ],
            },
            "School Assignment": {
                "Professional": [
                    "I ran into an issue and need a short extension for {deliverable}. I can submit by {new_time} if that's okay.",
                ],
                "Sincere": [
                    "A personal situation came up and I couldn't finish {deliverable}. May I submit by {new_time}?",
                ],
            },
            "Social Event": {
                "Casual": [
                    "I'm really sorry—I can't make it to {event} tonight. Can we catch up this weekend?",
                ],
                "Light-hearted": [
                    "My day did a plot twist. I have to miss {event}. Rain check for {new_time}?",
                ],
            },
            "Appointment": {
                "Professional": [
                    "I need to reschedule today's appointment due to a conflict. Could we move it to {new_time}?",
                ],
            },
            "Travel/Commute": {
                "Professional": [
                    "Travel delays are slowing me down. I should be there by {new_time}. Sorry for the hassle.",
                ],
                "Brief": [
                    "Running late due to traffic. ETA {new_time}.",
                ],
            },
        }

    def _choose_template(self, category: str, tone: str) -> str:
        categories = self.templates
        chosen_category = category if category in categories else "General"
        tones = categories[chosen_category]
        chosen_tone = tone if tone in tones else next(iter(tones))
        return self.random.choice(tones[chosen_tone])

    def _build_context(self, request: ExcuseRequest) -> Dict[str, str]:
        now = datetime.now()
        default_action = "complete the task"
        default_deliverable = "the deliverable"
        default_event = "the event"

        # Specificity toggles detail richness
        if request.specificity >= 7:
            timeframe = now.strftime("%A %I:%M %p")
            new_time = (now.replace(minute=(now.minute // 15) * 15) if True else now).strftime("%A %I:%M %p")
        elif request.specificity >= 4:
            timeframe = now.strftime("%A")
            new_time = (now.replace(hour=(now.hour + 3) % 24)).strftime("%A %I %p")
        else:
            timeframe = "today"
            new_time = "tomorrow"

        context = {
            "action": default_action,
            "deliverable": default_deliverable,
            "event": default_event,
            "timeframe": timeframe,
            "new_time": new_time,
        }

        # Incorporate custom context heuristically
        if request.custom_context:
            text = request.custom_context
            if len(text) < 120 and "," not in text and " " in text:
                context["deliverable"] = text
            else:
                context["notes"] = text

        return context

    def _vary(self, text: str, request: ExcuseRequest) -> str:
        # Simple variation knobs by length
        if request.length == "Short":
            if len(text) > 140:
                text = text.split(". ")[0] + "."
        elif request.length == "Long":
            addons = [
                " Thank you for your patience.",
                " I appreciate your understanding and will keep you informed.",
                " Please let me know if a different time works better.",
            ]
            text = text + self.random.choice(addons)
        return text.strip()

    def generate(self, request: ExcuseRequest) -> str:
        if request.seed is not None:
            self.random.seed(request.seed)
        template = self._choose_template(request.category, request.tone)
        context = self._build_context(request)
        try:
            text = template.format(**context)
        except KeyError:
            text = template
        text = self._vary(text, request)
        return text

    def rephrase(self, request: ExcuseRequest, base_text: str) -> str:
        # Re-roll the template while preserving prior context knobs
        if request.seed is not None:
            self.random.seed(request.seed + 1)
        template = self._choose_template(request.category, request.tone)
        context = self._build_context(request)
        text = template.format(**context)
        text = self._vary(text, request)
        return text

    def persist(self, text: str) -> None:
        persist_dir = Path(".history")
        persist_dir.mkdir(exist_ok=True, parents=True)
        file = persist_dir / f"history_{datetime.now().strftime('%Y%m%d')}.jsonl"
        record = {"timestamp": datetime.now().isoformat(), "text": text}
        with file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


