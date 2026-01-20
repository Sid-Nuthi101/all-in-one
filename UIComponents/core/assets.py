"""UI-only assets registry for background presets."""
from dataclasses import dataclass


@dataclass(frozen=True)
class GradientPreset:
  name: str
  colors: tuple[str, ...]


GRADIENT_PRESETS = (
  GradientPreset("nebula", ("#0d1024", "#22113b", "#10264f")),
  GradientPreset("arctic", ("#091028", "#0d304f", "#144e75")),
  GradientPreset("plasma", ("#180b2a", "#3b145c", "#1c2a6d")),
)
