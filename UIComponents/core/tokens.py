"""Design tokens for the glassmorphism UI kit."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ColorTokens:
  background: str = "#0b0f1a"
  surface: str = "rgba(18, 24, 38, 0.72)"
  surface_alt: str = "rgba(27, 34, 52, 0.68)"
  surface_light: str = "rgba(40, 52, 78, 0.55)"
  border: str = "rgba(140, 170, 255, 0.28)"
  border_active: str = "rgba(120, 214, 255, 0.65)"
  glow: str = "rgba(108, 217, 255, 0.4)"
  text_primary: str = "#e6f0ff"
  text_secondary: str = "#9fb2d9"
  accent: str = "#7a7dff"
  accent_alt: str = "#5cf3ff"
  success: str = "#6dffa8"
  error: str = "#ff6b8a"


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
  lg: int = 18
  xl: int = 24


@dataclass(frozen=True)
class ShadowTokens:
  soft: str = "0 12px 30px rgba(5, 10, 20, 0.45)"
  lift: str = "0 18px 40px rgba(10, 18, 35, 0.55)"
  glow: str = "0 0 20px rgba(110, 210, 255, 0.35)"


@dataclass(frozen=True)
class TypographyTokens:
  font_family: str = "'Inter', 'SF Pro Display', 'Segoe UI', sans-serif"
  title_size: int = 16
  body_size: int = 13
  caption_size: int = 11


@dataclass(frozen=True)
class MotionTokens:
  fast_ms: int = 120
  base_ms: int = 200
  slow_ms: int = 360


@dataclass(frozen=True)
class EffectTokens:
  blur_radius: int = 18
  border_width: int = 1
  border_width_active: int = 2


COLORS = ColorTokens()
SPACING = SpacingTokens()
RADII = RadiusTokens()
SHADOWS = ShadowTokens()
TYPOGRAPHY = TypographyTokens()
MOTION = MotionTokens()
EFFECTS = EffectTokens()
