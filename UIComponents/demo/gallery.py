from __future__ import annotations

from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from ..backgrounds import (
  AuroraGradientBackground,
  BackgroundStack,
  Grid3DBackground,
  ParticleLayerBackground,
  StarfieldBackground,
)
from ..cards import MessageBubble, MessageBubbleRow, ProfileCard
from ..layouts import MessageWindow, Sidebar, SplitPane
from ..core.tokens import COLORS, SPACING, TYPOGRAPHY


class ComponentGallery(QWidget):
  """Demo gallery that lists every component with its name."""

  def __init__(self):
    super().__init__()

    layout = QVBoxLayout()
    layout.setContentsMargins(SPACING.lg, SPACING.lg, SPACING.lg, SPACING.lg)
    layout.setSpacing(SPACING.lg)

    title = QLabel("UIComponents Gallery")
    title.setStyleSheet(
      f"color: {COLORS.text_primary}; font-size: {TYPOGRAPHY.title_size + 6}px; font-weight: 700;"
    )
    layout.addWidget(title)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)

    content = QWidget()
    content_layout = QVBoxLayout()
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(SPACING.lg)

    content_layout.addWidget(_section_label("Backgrounds"))
    content_layout.addWidget(_named_component("AuroraGradientBackground", AuroraGradientBackground()))
    content_layout.addWidget(_named_component("Grid3DBackground", Grid3DBackground()))
    content_layout.addWidget(_named_component("ParticleLayerBackground", ParticleLayerBackground()))
    content_layout.addWidget(_named_component("StarfieldBackground", StarfieldBackground()))
    content_layout.addWidget(_named_component("BackgroundStack", BackgroundStack()))

    content_layout.addWidget(_section_label("Cards"))
    content_layout.addWidget(
      _named_component(
        "ProfileCard",
        ProfileCard(
          name="Nova Garcia",
          last_message="Signal confirmed.",
          timestamp="09:41",
          avatar_text="N",
        ),
      )
    )
    bubble = MessageBubble("Sample message bubble", timestamp="09:42")
    content_layout.addWidget(_named_component("MessageBubble", bubble))
    content_layout.addWidget(_named_component("MessageBubbleRow", MessageBubbleRow(bubble)))

    content_layout.addWidget(_section_label("Layouts"))
    sidebar = Sidebar(
      "Crew",
      [
        {
          "name": "Nova Garcia",
          "last_message": "Signal confirmed.",
          "timestamp": "09:41",
          "avatar_text": "N",
          "is_selected": True,
        }
      ],
    )
    content_layout.addWidget(_named_component("Sidebar", sidebar))

    message_window = MessageWindow(
      "Nova Garcia",
      [
        {"text": "Ready to depart.", "timestamp": "09:40"},
        {"text": "Systems green.", "timestamp": "09:41", "is_own": True},
      ],
    )
    content_layout.addWidget(_named_component("MessageWindow", message_window))

    split_pane = SplitPane(sidebar, message_window)
    content_layout.addWidget(_named_component("SplitPane", split_pane))

    content_layout.addStretch()
    content.setLayout(content_layout)
    scroll.setWidget(content)

    layout.addWidget(scroll)
    self.setLayout(layout)


def _section_label(text: str) -> QLabel:
  label = QLabel(text)
  label.setStyleSheet(
    f"color: {COLORS.text_secondary}; font-size: {TYPOGRAPHY.title_size}px; font-weight: 600;"
  )
  return label


def _named_component(name: str, widget: QWidget) -> QWidget:
  container = QWidget()
  container_layout = QVBoxLayout()
  container_layout.setContentsMargins(0, 0, 0, 0)
  container_layout.setSpacing(SPACING.sm)

  label = QLabel(name)
  label.setStyleSheet(
    f"color: {COLORS.text_primary}; font-size: {TYPOGRAPHY.body_size}px; font-weight: 500;"
  )

  container_layout.addWidget(label)
  container_layout.addWidget(widget)
  container.setLayout(container_layout)
  return container
