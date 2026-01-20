import sys
from PySide6 import QtWidgets

from UIComponents.backgrounds.aurora import AuroraGradientBackground
from UIComponents.backgrounds.background_stack import BackgroundStack
from UIComponents.backgrounds.grid3d import Grid3DBackground
from UIComponents.backgrounds.particles import ParticleLayerBackground
from UIComponents.backgrounds.starfield import StarfieldBackground
from UIComponents.backgrounds.vignette import VignetteOverlay
from UIComponents.cards.info_card import InfoCard
from UIComponents.cards.media_card import MediaCard
from UIComponents.cards.message_bubble import MessageBubble
from UIComponents.cards.message_card import MessageCard
from UIComponents.cards.profile_card import ProfileCard
from UIComponents.cards.stat_card import StatCard
from UIComponents.cards.timeline_card import TimelineCard
from UIComponents.demo.gallery import Gallery
from UIComponents.forms.field_row import FieldRow
from UIComponents.forms.form_shell import FormShell
from UIComponents.forms.validation_hint import ValidationHint
from UIComponents.layouts.app_shell import AppShell
from UIComponents.layouts.grid import Grid
from UIComponents.layouts.section import Section
from UIComponents.layouts.sidebar import Sidebar
from UIComponents.layouts.split_pane import SplitPane
from UIComponents.layouts.topbar import Topbar
from UIComponents.primitives.badge import StatusBadge
from UIComponents.primitives.button import GlassButton
from UIComponents.primitives.empty_state import EmptyState
from UIComponents.primitives.glass_panel import GlassPanel
from UIComponents.primitives.icon import NeonIcon
from UIComponents.primitives.input import GlassInput, GlassTextArea
from UIComponents.primitives.modal import ModalShell
from UIComponents.primitives.neon_divider import NeonDivider
from UIComponents.primitives.progress import ProgressBar, ProgressRing
from UIComponents.primitives.spinner import Spinner
from UIComponents.primitives.tabs import GlassTabs
from UIComponents.primitives.table import GlassTable
from UIComponents.primitives.text import Body, Caption, Code, H1, H2, H3
from UIComponents.primitives.toast import Toast
from UIComponents.primitives.toggle import GlassToggle, SegmentedControl
from UIComponents.primitives.tooltip import GlassTooltip


class ComponentRow(QtWidgets.QFrame):
    def __init__(self, name: str, widget: QtWidgets.QWidget):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QtWidgets.QLabel(name)
        label.setStyleSheet("color: #E8EEFF; font-weight: 600; font-size: 14px;")
        layout.addWidget(label)
        layout.addWidget(widget)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UIComponents Test Harness")
        self.setStyleSheet(
            "background-color: #0A0F1F;"
            "QScrollBar:vertical {"
            "background: #0A0F1F;"
            "width: 10px;"
            "margin: 0px;"
            "}"
            "QScrollBar::handle:vertical {"
            "background: rgba(110, 231, 255, 0.35);"
            "border-radius: 5px;"
            "min-height: 20px;"
            "}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
            "height: 0px;"
            "}"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {"
            "background: transparent;"
            "}"
            "QScrollBar:horizontal {"
            "background: #0A0F1F;"
            "height: 10px;"
            "margin: 0px;"
            "}"
            "QScrollBar::handle:horizontal {"
            "background: rgba(110, 231, 255, 0.35);"
            "border-radius: 5px;"
            "min-width: 20px;"
            "}"
            "QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {"
            "width: 0px;"
            "}"
            "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {"
            "background: transparent;"
            "}"
        )

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setSpacing(24)

        container_layout.addWidget(H1("UIComponents Test Harness"))
        container_layout.addWidget(Body("Each component is listed with its name and preview."))

        background_section = QtWidgets.QVBoxLayout()
        background_section.addWidget(ComponentRow("BackgroundStack", self._fixed_height(BackgroundStack(), 140)))
        background_section.addWidget(ComponentRow("StarfieldBackground", self._fixed_height(StarfieldBackground(), 140)))
        background_section.addWidget(ComponentRow("AuroraGradientBackground", self._fixed_height(AuroraGradientBackground(), 140)))
        background_section.addWidget(ComponentRow("Grid3DBackground", self._fixed_height(Grid3DBackground(), 140)))
        background_section.addWidget(ComponentRow("ParticleLayerBackground", self._fixed_height(ParticleLayerBackground(), 140)))
        background_section.addWidget(ComponentRow("VignetteOverlay", self._fixed_height(VignetteOverlay(), 140)))
        container_layout.addLayout(background_section)

        container_layout.addWidget(ComponentRow("GlassPanel", self._glass_panel_sample()))
        container_layout.addWidget(ComponentRow("NeonDivider", self._fixed_height(NeonDivider(), 8)))

        text_group = QtWidgets.QVBoxLayout()
        text_group.addWidget(H1("H1 Heading"))
        text_group.addWidget(H2("H2 Heading"))
        text_group.addWidget(H3("H3 Heading"))
        text_group.addWidget(Body("Body text style"))
        text_group.addWidget(Caption("Caption text style"))
        text_group.addWidget(Code("Code text style"))
        text_widget = QtWidgets.QWidget()
        text_widget.setLayout(text_group)
        container_layout.addWidget(ComponentRow("Text (H1/H2/H3/Body/Caption/Code)", text_widget))

        icon = NeonIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon), size=24)
        container_layout.addWidget(ComponentRow("NeonIcon", icon))

        buttons = QtWidgets.QHBoxLayout()
        buttons.addWidget(GlassButton("Primary"))
        buttons.addWidget(GlassButton("Secondary", variant="secondary"))
        buttons.addWidget(GlassButton("Ghost", variant="ghost"))
        buttons_widget = QtWidgets.QWidget()
        buttons_widget.setLayout(buttons)
        container_layout.addWidget(ComponentRow("GlassButton", buttons_widget))

        container_layout.addWidget(ComponentRow("GlassInput", GlassInput("Type here")))
        container_layout.addWidget(ComponentRow("GlassTextArea", self._fixed_height(GlassTextArea("Multiline input"), 120)))

        toggles = QtWidgets.QHBoxLayout()
        toggles.addWidget(GlassToggle("GlassToggle"))
        toggles.addWidget(SegmentedControl(["One", "Two", "Three"]))
        toggles_widget = QtWidgets.QWidget()
        toggles_widget.setLayout(toggles)
        container_layout.addWidget(ComponentRow("Toggle + SegmentedControl", toggles_widget))

        container_layout.addWidget(ComponentRow("StatusBadge", StatusBadge("Active", variant="success")))
        container_layout.addWidget(ComponentRow("GlassTooltip", GlassTooltip("Tooltip preview")))
        container_layout.addWidget(ComponentRow("Spinner", Spinner()))
        container_layout.addWidget(ComponentRow("ProgressBar", ProgressBar(65)))
        container_layout.addWidget(ComponentRow("ProgressRing", ProgressRing("72%")))
        container_layout.addWidget(ComponentRow("Toast", Toast("Toast preview", variant="info")))

        tabs = GlassTabs()
        tabs.addTab(EmptyState("Empty", "Nothing to show"), "Empty State")
        tabs.addTab(Body("Tab content"), "Second")
        container_layout.addWidget(ComponentRow("GlassTabs", self._fixed_height(tabs, 200)))

        table = GlassTable(3, 3)
        table.setHorizontalHeaderLabels(["Col A", "Col B", "Col C"])
        for row in range(3):
            for col in range(3):
                table.setItem(row, col, QtWidgets.QTableWidgetItem(f"{row},{col}"))
        container_layout.addWidget(ComponentRow("GlassTable", self._fixed_height(table, 160)))

        container_layout.addWidget(ComponentRow("EmptyState", EmptyState("No messages", "Connect a device to see updates.")))

        container_layout.addWidget(ComponentRow("StatCard", StatCard("Open Threads", "42", "+6%")))
        info_actions = [GlassButton("Action")]
        container_layout.addWidget(ComponentRow("InfoCard", InfoCard("Info", "Some descriptive text", actions=info_actions)))
        container_layout.addWidget(ComponentRow("MediaCard", MediaCard("Media", "Preview")))
        container_layout.addWidget(ComponentRow("ProfileCard", ProfileCard("Nova Lane", "Designer")))
        container_layout.addWidget(
            ComponentRow("MessageBubble (incoming)", MessageBubble("Incoming message preview.", timestamp="09:41"))
        )
        container_layout.addWidget(
            ComponentRow(
                "MessageBubble (outgoing)",
                MessageBubble("Outgoing message preview.", is_outgoing=True, timestamp="09:42"),
            )
        )
        container_layout.addWidget(
            ComponentRow(
                "MessageCard",
                MessageCard("Alex Rivera", "Let’s sync on the latest draft.", timestamp="10:12"),
            )
        )
        container_layout.addWidget(
            ComponentRow(
                "MessageCard (outgoing)",
                MessageCard("You", "Share the latest edits before lunch.", timestamp="10:13", is_outgoing=True),
            )
        )
        container_layout.addWidget(ComponentRow("TimelineCard", TimelineCard("09:30", "Update", "A timeline entry")))

        app_shell = AppShell()
        app_shell.setMinimumHeight(200)
        container_layout.addWidget(ComponentRow("AppShell", app_shell))
        container_layout.addWidget(ComponentRow("Sidebar", Sidebar()))
        container_layout.addWidget(ComponentRow("Topbar", Topbar("Topbar")))

        split = SplitPane()
        split.addWidget(GlassPanel())
        split.addWidget(GlassPanel())
        split.setFixedHeight(160)
        container_layout.addWidget(ComponentRow("SplitPane", split))

        grid = Grid(columns=3)
        grid.add_widget(StatCard("One", "1"))
        grid.add_widget(StatCard("Two", "2"))
        grid.add_widget(StatCard("Three", "3"))
        container_layout.addWidget(ComponentRow("Grid", grid))

        section = Section("Section Title")
        section.layout().addWidget(Body("Section content"))
        container_layout.addWidget(ComponentRow("Section", section))

        form = FormShell("FormShell")
        form.layout().addWidget(FieldRow("Email", GlassInput("name@domain.com")))
        form.layout().addWidget(ValidationHint("Looks good", state="success"))
        container_layout.addWidget(ComponentRow("FormShell/FieldRow/ValidationHint", form))

        modal_button = GlassButton("Open Modal")
        modal = ModalShell("ModalShell")
        modal.layout().addWidget(Body("Modal content preview."))
        modal_button.clicked.connect(modal.show)
        container_layout.addWidget(ComponentRow("ModalShell", modal_button))

        container_layout.addWidget(ComponentRow("Gallery", self._fixed_height(Gallery(), 500)))

        container_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

    @staticmethod
    def _fixed_height(widget: QtWidgets.QWidget, height: int) -> QtWidgets.QWidget:
        widget.setMinimumHeight(height)
        widget.setMaximumHeight(height)
        return widget

    @staticmethod
    def _glass_panel_sample() -> QtWidgets.QWidget:
        panel = GlassPanel()
        panel.layout().addWidget(Body("Glass panel content"))
        return panel


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.resize(900, 800)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
