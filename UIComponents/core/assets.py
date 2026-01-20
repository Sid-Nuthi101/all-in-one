"""Asset registry for UI backgrounds and overlays."""
from dataclasses import dataclass


@dataclass(frozen=True)
class BackgroundAsset:
    name: str
    description: str


NOISE_OVERLAY = BackgroundAsset(
    name="noise",
    description="Subtle noise overlay to prevent color banding.",
)

BACKGROUND_PRESETS = {
    "default": "base-gradient+grid+particles+vignette",
    "minimal": "base-gradient+vignette",
    "neon": "base-gradient+aurora+grid+vignette",
}
