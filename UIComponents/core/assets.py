"""UI-only assets registry for background presets."""
from dataclasses import dataclass
from .tokens import TOKENS

@dataclass(frozen=True)
class GradientPreset:
  name: str
  colors: tuple[str, ...]


GRADIENT_PRESETS = (
  GradientPreset("nebula", ("#0d1024", "#22113b", "#10264f")),
  GradientPreset("arctic", ("#091028", "#0d304f", "#144e75")),
  GradientPreset("plasma", ("#180b2a", "#3b145c", "#1c2a6d")),
)

BACKGROUND_PRESETS = {
  "default_gradient": ["#0b0f1a", "#121a2b", "#10182a"],
  "aurora": ["#5ee7ff", "#6f8cff", "#b37bff"],
}


def vignette_style(opacity=0.4):
  return """
    QWidget {{
      background: qradialgradient(
        cx:0.5, cy:0.5, radius:0.7,
        fx:0.5, fy:0.5,
        stop:0 rgba(0, 0, 0, 0),
        stop:1 rgba(0, 0, 0, {alpha})
      );
    }}
  """.format(alpha=int(255 * opacity))


def focus_ring_style():
  return """
    QWidget:focus {{
      outline: none;
      border: 2px solid {accent};
    }}
  """.format(accent=TOKENS["color"]["accent"])