# UIComponents

Glassmorphism + futuristic UI kit built with PySide6.

## Usage

```python
from UIComponents.demo import DemoLayout

layout = DemoLayout()
layout.resize(1200, 720)
layout.show()
```

## Run the gallery demo

```bash
python -m UIComponents.demo.run_gallery
```

## Notes
- Components are UI-only and accept props plus callbacks for interactions.
- Styling is driven by `UIComponents.core.tokens` and `UIComponents.core.styles`.
- Backgrounds are lightweight and composable via `BackgroundStack`.
