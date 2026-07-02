"""Configuration for the essay writer workflow."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Style = Literal["academic", "persuasive", "narrative"]


@dataclass(frozen=True)
class EssayWriterConfig:
    """Configuration object for the essay writer state machine."""

    target_word_count: int = 1200
    style: Style = "academic"
    max_reflect_cycles: int = 2
    pause_for_human_approval: bool = True
