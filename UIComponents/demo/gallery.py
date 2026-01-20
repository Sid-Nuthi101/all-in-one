"""Component gallery screen."""
from PySide6 import QtWidgets

from UIComponents.backgrounds.background_stack import BackgroundStack
from UIComponents.cards.info_card import InfoCard
from UIComponents.cards.media_card import MediaCard
from UIComponents.cards.profile_card import ProfileCard
from UIComponents.cards.stat_card import StatCard
from UIComponents.cards.timeline_card import TimelineCard
from UIComponents.cards.message_bubble import MessageBubble
from UIComponents.cards.message_card import MessageCard
from UIComponents.demo.presets import INFO_CARD, STAT_CARDS, TIMELINE_ITEMS
from UIComponents.forms.field_row import FieldRow
from UIComponents.forms.form_shell import FormShell
from UIComponents.forms.validation_hint import ValidationHint
from UIComponents.layouts.app_shell import AppShell
from UIComponents.layouts.grid import Grid
from UIComponents.primitives.badge import StatusBadge
from UIComponents.primitives.button import GlassButton
from UIComponents.primitives.empty_state import EmptyState
from UIComponents.primitives.input import GlassInput
from UIComponents.primitives.progress import ProgressBar
from UIComponents.primitives.spinner import Spinner
from UIComponents.primitives.tabs import GlassTabs
from UIComponents.primitives.text import H1, H2, Body
from UIComponents.primitives.toast import Toast
from UIComponents.primitives.toggle import GlassToggle, SegmentedControl


class Gallery(QtWidgets.QFrame):
    def __init__(self, *, class_name: str = "") -> None:
        super().__init__()
        self.setObjectName(class_name or "Gallery")
        layout = QtWidgets.QStackedLayout(self)
        layout.setStackingMode(QtWidgets.QStackedLayout.StackAll)
        layout.addWidget(BackgroundStack())
        content = QtWidgets.QScrollArea()
        content.setWidgetResizable(True)
        container = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(container)
        content_layout.setSpacing(24)
        content_layout.addWidget(H1("UIComponents Gallery"))
        content_layout.addWidget(Body("Preview of glassmorphism UI primitives."))
        stat_grid = Grid(columns=3)
        for stat in STAT_CARDS:
            stat_grid.add_widget(StatCard(**stat))
        content_layout.addWidget(stat_grid)
        content_layout.addWidget(InfoCard(**INFO_CARD, actions=[GlassButton("Action")]))
        content_layout.addWidget(MediaCard("Media Preview", "Futuristic placeholder"))
        content_layout.addWidget(ProfileCard("Nova Lane", "Interaction Designer"))
        content_layout.addWidget(MessageBubble("Incoming message preview.", is_outgoing=False, timestamp="09:41"))
        content_layout.addWidget(MessageBubble("Outgoing message preview.", is_outgoing=True, timestamp="09:42"))
        content_layout.addWidget(MessageCard("Alex Rivera", "Let’s sync on the latest draft.", timestamp="10:12"))
        content_layout.addWidget(
            MessageCard(
                "You",
                "Share the latest edits before lunch.",
                timestamp="10:13",
                is_outgoing=True,
            )
        )
        for item in TIMELINE_ITEMS:
            content_layout.addWidget(TimelineCard(**item))
        form = FormShell("Contact")
        form.layout().addWidget(FieldRow("Email", GlassInput("name@domain.com")))
        form.layout().addWidget(ValidationHint("Looks good", state="success"))
        content_layout.addWidget(form)
        controls = QtWidgets.QHBoxLayout()
        controls.addWidget(GlassButton("Primary"))
        controls.addWidget(GlassButton("Secondary", variant="secondary"))
        controls.addWidget(GlassButton("Ghost", variant="ghost"))
        content_layout.addLayout(controls)
        toggles = QtWidgets.QHBoxLayout()
        toggles.addWidget(GlassToggle("Notifications"))
        toggles.addWidget(SegmentedControl(["Today", "Week", "Month"]))
        content_layout.addLayout(toggles)
        content_layout.addWidget(StatusBadge("LIVE", variant="success"))
        content_layout.addWidget(ProgressBar(68))
        content_layout.addWidget(Spinner())
        tabs = GlassTabs()
        tabs.addTab(EmptyState("No messages", "Connect a device to view updates."), "Empty")
        tabs.addTab(AppShell(), "Shell")
        content_layout.addWidget(tabs)
        content_layout.addWidget(Toast("Sync complete", variant="success"))
        content_layout.addStretch()
        content.setWidget(container)
        layout.addWidget(content)
