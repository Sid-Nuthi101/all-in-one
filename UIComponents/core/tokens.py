"""Design tokens for the UI kit."""
from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class ColorTokens:
    background: str = "#0A0F1F"
    surface: str = "rgba(20, 28, 45, 0.65)"
    surface_alt: str = "rgba(30, 40, 60, 0.7)"
    border: str = "rgba(120, 150, 255, 0.25)"
    border_active: str = "rgba(120, 190, 255, 0.65)"
    text_primary: str = "#E8EEFF"
    text_secondary: str = "#B8C2DD"
    text_muted: str = "#7A87A8"
    accent: str = "#6EE7FF"
    accent_secondary: str = "#A57CFF"
    danger: str = "#FF6B9A"
    success: str = "#5EFFB1"


@dataclass(frozen=True)
class SpacingTokens:
    xs: int = 4
    sm: int = 8
    md: int = 12
    lg: int = 16
    xl: int = 24
    xxl: int = 32


@dataclass(frozen=True)
class RadiusTokens:
    sm: int = 8
    md: int = 12
    lg: int = 16
    xl: int = 24


@dataclass(frozen=True)
class ShadowTokens:
    ambient: str = "0 12px 32px rgba(0, 0, 0, 0.35)"
    glow: str = "0 0 18px rgba(110, 231, 255, 0.35)"


@dataclass(frozen=True)
class BlurTokens:
    sm: int = 8
    md: int = 16
    lg: int = 24


@dataclass(frozen=True)
class TypographyTokens:
    h1_size: int = 28
    h2_size: int = 22
    h3_size: int = 18
    body_size: int = 14
    caption_size: int = 12
    code_size: int = 12
    font_family: str = "'SF Pro Display', 'Inter', 'Segoe UI', sans-serif"
    mono_family: str = "'SF Mono', 'JetBrains Mono', monospace"


@dataclass(frozen=True)
class DesignTokens:
    colors: ColorTokens = field(default_factory=ColorTokens)
    spacing: SpacingTokens = field(default_factory=SpacingTokens)
    radius: RadiusTokens = field(default_factory=RadiusTokens)
    shadows: ShadowTokens = field(default_factory=ShadowTokens)
    blur: BlurTokens = field(default_factory=BlurTokens)
    typography: TypographyTokens = field(default_factory=TypographyTokens)
    motion: Dict[str, int] = field(
        default_factory=lambda: {"fast": 120, "medium": 200, "slow": 360}
    )


DARK_GLASS = DesignTokens()

MIDNIGHT_NEON = DesignTokens(
    colors=ColorTokens(
        background="#060815",
        surface="rgba(15, 20, 40, 0.72)",
        surface_alt="rgba(25, 32, 55, 0.78)",
        border="rgba(110, 130, 255, 0.35)",
        border_active="rgba(145, 200, 255, 0.8)",
        text_primary="#F1F5FF",
        text_secondary="#C8D0EE",
        text_muted="#8C97B8",
        accent="#7CF9FF",
        accent_secondary="#B88CFF",
        danger="#FF7BB1",
        success="#6CFFC2",
    )
)

LIGHT_GLASS = DesignTokens(
    colors=ColorTokens(
        background="#E9EEF9",
        surface="rgba(255, 255, 255, 0.55)",
        surface_alt="rgba(255, 255, 255, 0.7)",
        border="rgba(120, 150, 255, 0.4)",
        border_active="rgba(90, 160, 255, 0.7)",
        text_primary="#101828",
        text_secondary="#344054",
        text_muted="#667085",
        accent="#2DD4FF",
        accent_secondary="#7C5CFF",
        danger="#F04438",
        success="#12B76A",
    )
)

THEMES = {
    "DarkGlass": DARK_GLASS,
    "MidnightNeon": MIDNIGHT_NEON,
    "LightGlass": LIGHT_GLASS,
}
