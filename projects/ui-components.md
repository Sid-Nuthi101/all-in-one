# UIComponents (Python-only) — Glassmorphism Futuristic UI Kit

This folder is **UI-only**. It must contain **zero business logic** and **zero data-fetching**.  
Every file in `UIComponents/` is a **reusable, plug-and-play UI component** built in Python that can be imported and rendered by the app.

The goal: a cohesive **glassmorphism**, **futuristic** interface with shared styling primitives so everything feels integrated.

---

## Principles (Non-negotiable)

### 1) UI-only boundary
Components may:
- Render layout, typography, icons, animation, and visuals
- Accept props/inputs like `title`, `subtitle`, `items`, `is_loading`, `error_text`
- Emit UI events via **callbacks** (e.g., `on_click`, `on_submit`) *without handling logic inside*

Components must NOT:
- Call APIs, read databases, query files, or mutate global state
- Contain domain rules (matching logic, parsing, etc.)
- Perform auth, network IO, or business decision-making

### 2) One cohesive look
- **Glass panels**, blurred backgrounds, subtle neon accents
- Rounded corners, soft shadows, light borders
- Consistent spacing and type scale

### 3) Plug-and-play imports
- Each component should be importable as a single class/function
- No app-specific imports inside UI components (only UI framework + local UI kit imports)

### 4) Single “design tokens” source of truth
All colors, radii, shadows, spacing, typography, and animation timing live in one place (design tokens).  
Everything else references tokens.

---

## Folder Layout

Create this folder structure:

UIComponents/
  README.md
  __init__.py

  core/
    __init__.py
    tokens.py          # design tokens: colors, spacing, radii, shadows, typography
    styles.py          # reusable style builders (glass panel, gradients)
    assets.py          # paths / registries for background presets (no fetching)

  backgrounds/
    __init__.py
    starfield.py       # animated-ish background component (pure UI)
    aurora.py          # gradient aurora background component
    grid3d.py          # perspective grid background component
    particles.py       # lightweight particle layer background component

  cards/
    __init__.py
    profile_card.py    # like on iMessage - icon, name, last message, last message time (apply glassmorphism)
    message_bubbles.py # should display a text message bubble in glassmorphism

  layouts/
    __init__.py
    sidebar.py         # futuristic sidebar nav UI which houses a list of profile cards (no routing logic)
    messages.py        # a message window that displays all the messages within a chat with a person (like iMessage - top should display name and information icon that can be pressed [functionality for icon is out of scope for this project])
    split_pane.py      # resizable panes UI wrapper (render-only) [This is eventually going to resize between the sidebar and the message window]
  
  demo/
    __init__.py
    layout.py - this is where we demo the split pane. make the left half of the screen be a sidebar with profile cards that can be pressed into and the right side should be the messages screen with sample messages loaded. 

---

## Component Contract (Standard)

Every component should follow the same UI API conventions:

### Required
- `class_name` or `style` override hook (so apps can tweak)
- `variant` (e.g., "primary", "secondary", "ghost") where relevant
- `size` (e.g., "sm", "md", "lg") where relevant

### Optional but recommended
- `leading` / `trailing` slots for icons or small elements
- `state` flags: `is_loading`, `is_disabled`, `is_selected`, `is_error`
- `on_*` callback props for interaction (no logic inside)

### Design consistency
- Spacing uses tokens only
- Color uses tokens only
- Corners/shadows use tokens only

---

## Glassmorphism Spec (What “Glass” Means Here)

All “glass” surfaces follow these rules:

- Background: semi-transparent (dark) with subtle gradient
- Blur: consistent blur radius (token-driven)
- Border: 1px/2px translucent border, optional neon edge highlight
- Shadow: soft ambient shadow + faint glow for “active” states
- Noise: optional subtle noise overlay (pure UI asset) to prevent banding

Define:
- `GlassPanel` as the base primitive used everywhere
- All cards, modals, sidebars, and shells compose `GlassPanel`

---

## Futuristic Backgrounds (UI Components)

Backgrounds are **components** you can drop behind the app shell. They must:
- Be lightweight and performant
- Avoid heavy GPU effects unless optional
- Provide variants and opacity controls

### Background presets
Create these background components with configurable intensity:
- `StarfieldBackground(intensity, speed, density)`
- `AuroraGradientBackground(palette, motion_level)`
- `Grid3DBackground(depth, glow_level)`
- `ParticleLayerBackground(particle_count, drift, blur)`

Also provide `BackgroundStack()` that composes:
- Base gradient + grid + particles + vignette
- All intensities token-driven

---

## State & Interaction Styling (UI-only)

Standard states must be visually consistent across all components:

### Hover
- Slightly brighter border glow
- Subtle lift (shadow increase) or gradient shift

### Pressed
- Slight compress (shadow reduce, translate down)
- Border glow reduced briefly

### Focus (keyboard)
- Visible focus ring (neon outline)
- Must be accessible and consistent

### Disabled
- Lower opacity
- No glow
- Cursor/interaction visuals muted

## Testing & QA (UI-only)

Create a visual checklist for the demo gallery:

- Typography looks consistent across components
- Glass panels have consistent blur/border/shadow
- Buttons show hover/pressed/focus/disabled properly
- Inputs show focus and error styles properly
- Backgrounds don’t overpower foreground readability
- Responsive behavior looks acceptable at common widths

---

## Definition of Done

This folder is complete when:

- `UIComponents/` contains a coherent set of UI components as specified above
- A `demo/gallery` screen renders every component using sample props
- No UI file performs network IO or business logic
- All styling is token-driven and consistent
- The look is unmistakably glassmorphism + futuristic, with background presets included

---
