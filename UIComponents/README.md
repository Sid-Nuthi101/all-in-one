# UIComponents

Glassmorphism-focused UI kit built with PySide6. This package is **UI-only** and contains reusable, plug-and-play widgets backed by shared design tokens.

## Usage

```python
from UIComponents.layouts.split_pane import SplitPane
from UIComponents.layouts.sidebar import Sidebar
from UIComponents.layouts.messages import MessagesView

sidebar = Sidebar(items=[])
messages = MessagesView(title="Demo", subtitle="Active")
root = SplitPane(left=sidebar, right=messages)
```

## Structure

- `core/`: design tokens and reusable glass panel styles
- `backgrounds/`: drop-in background layers
- `cards/`: reusable UI cards and message bubbles
- `layouts/`: composed layouts (sidebar, messages view, split pane)
- `demo/`: demo layout showcasing components
