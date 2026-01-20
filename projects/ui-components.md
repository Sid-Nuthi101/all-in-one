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
    theme.py           # theme application + defaults (dark glass)
    styles.py          # reusable style builders (glass panel, neon border, gradients)
    assets.py          # paths / registries for background presets (no fetching)
    motion.py          # UI animation helpers (durations, easing names)

  backgrounds/
    __init__.py
    starfield.py       # animated-ish background component (pure UI)
    aurora.py          # gradient aurora background component
    grid3d.py          # perspective grid background component
    particles.py       # lightweight particle layer background component
    vignette.py        # vignette overlay component

  primitives/
    __init__.py
    glass_panel.py     # base glass container w/ blur + border + shadow
    neon_divider.py    # divider with glow and gradients
    text.py            # typography components (H1/H2/Body/Caption/Code)
    icon.py            # icon wrapper w/ sizing + glow
    button.py          # primary/secondary/ghost buttons
    input.py           # text input, search input, multiline
    toggle.py          # switches, segmented controls
    badge.py           # status badges
    tooltip.py         # hover/press tooltips
    spinner.py         # loading indicator
    progress.py        # progress bar / ring
    toast.py           # toast UI (render-only, no global manager logic)
    modal.py           # modal shell (no navigation logic)
    tabs.py            # tabs UI shell
    table.py           # table UI shell (render-only)
    empty_state.py     # empty state illustration + copy

  cards/
    __init__.py
    stat_card.py       # KPI / stat tiles
    info_card.py       # title + body + actions
    media_card.py      # image/video placeholder card
    profile_card.py    # avatar + metadata
    timeline_card.py   # event timeline item card

  layouts/
    __init__.py
    app_shell.py       # top-level layout shell (sidebar/topbar/contents)
    sidebar.py         # futuristic sidebar nav UI (no routing logic)
    topbar.py          # top bar UI (search slot, actions slot)
    split_pane.py      # resizable panes UI wrapper (render-only)
    grid.py            # responsive grid helpers
    section.py         # standard section header + body

  forms/
    __init__.py
    form_shell.py      # common form panel layout
    field_row.py       # label + input + help text
    validation_hint.py # purely visual hints, accepts state flags

  demo/
    __init__.py
    gallery.py         # component gallery screen (UI-only)
    presets.py         # sample props for previewing components (no real logic)

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
- `VignetteOverlay(strength, radius)`

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

### Error
- Red/pink neon accent border + helper text (visual only)
- No validation logic inside the component, only display based on props

---

## Accessibility Requirements (UI-level)

- Ensure focus rings exist for keyboard navigation
- Minimum contrast ratio where possible (token-based)
- Provide `aria_label` / `accessibility_text` props for interactive elements (framework permitting)
- Never rely on color alone: pair with icon/text for status

---

## Theming

Support at least:
- `DarkGlass` (default)
- `MidnightNeon` (more saturated accent)
- `LightGlass` (optional, if it still looks futuristic)

Theme system should allow:
- Set global tokens once
- Override per component via `variant` or `style` prop

---

## What to Build First (Recommended Order)

1) `core/tokens.py`
   - Colors: background, surface, border, text, accent, danger, success
   - Spacing scale: xs/sm/md/lg/xl
   - Radii: sm/md/lg/xl
   - Shadows: ambient + glow
   - Blur levels: glass blur scale
   - Type scale: H1/H2/H3/body/caption/code

2) `primitives/glass_panel.py`
   - The “foundation” component

3) `primitives/text.py`, `primitives/button.py`, `primitives/input.py`
   - Must look cohesive and match the glass spec

4) `layouts/app_shell.py` + `backgrounds/background_stack`
   - A full-screen futuristic baseline

5) Cards and higher-level components
   - `stat_card`, `info_card`, `table`, `modal`

6) `demo/gallery.py`
   - A single place to visually verify everything together

---

## Integration Rules (How App Uses This)

The main app should:
- Import from `UIComponents` only
- Provide data + callbacks
- Never style ad-hoc in the app unless via token overrides

Example usage pattern (conceptual only, no code):
- App creates `AppShell`
- Places `BackgroundStack` behind it
- Uses `Sidebar`, `Topbar`, `GlassPanel`, `StatCard`, etc.
- Passes `on_click` handlers from app logic layer

---

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

## Questions

- None at this time.
