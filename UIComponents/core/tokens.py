"""Design tokens for the glassmorphism UI kit."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ColorTokens:
  background: str = "#0b0f1a"
  surface: str = "rgba(18, 24, 38, 0.22)"
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

TOKENS = {
  "color": {
    "background": "#0b0f1a",
    "panel": "rgba(18, 25, 45, 0.65)",
    "panel_strong": "rgba(18, 25, 45, 0.8)",
    "border": "rgba(255, 255, 255, 0.12)",
    "border_active": "rgba(125, 209, 255, 0.45)",
    "text_primary": "#eaf6ff",
    "text_secondary": "#9fb3c8",
    "accent": "#7dd1ff",
    "accent_soft": "rgba(125, 209, 255, 0.2)",
    "success": "#66f2c2",
    "danger": "#ff6b8a",
  },
  "radius": {
    "sm": 10,
    "md": 16,
    "lg": 22,
  },
  "shadow": {
    "soft": (0, 18, 48, 80),
    "glow": (125, 209, 255, 140),
  },
  "spacing": {
    "xs": 6,
    "sm": 10,
    "md": 16,
    "lg": 24,
    "xl": 32,
  },
  "typography": {
    "title": 16,
    "subtitle": 12,
    "body": 11,
    "caption": 10,
  },
  "blur": {
    "panel": 18,
  },
}