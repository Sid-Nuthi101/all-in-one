"""UI animation helpers."""
from dataclasses import dataclass


@dataclass(frozen=True)
class MotionTokens:
    fast: int = 120
    medium: int = 200
    slow: int = 360
    easing_standard: str = "ease-in-out"
    easing_emphasized: str = "cubic-bezier(0.2, 0.8, 0.2, 1)"


MOTION = MotionTokens()
