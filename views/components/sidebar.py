"""
sidebar.py
----------
Left-hand navigation rail shared by the whole app. Emits a callback
with the page key when a nav button is clicked; MainWindow decides
what to swap into the content area. The sidebar itself knows nothing
about what each page contains -- pure navigation, no business logic.
"""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from themes.dark_theme import COLORS, font_body, font_heading, CORNER_RADIUS

# (page_key, display_label, icon_glyph)
# Icon glyphs are plain unicode placeholders for now; swappable for real
# icon assets later without touching layout logic.
NAV_ITEMS: list[tuple[str, str, str]] = [
    ("dashboard", "Dashboard", "\u25A6"),
    ("routine", "Daily Routine", "\u2600"),
    ("habits", "Habit Tracker", "\u2713"),
    ("calendar", "Calendar", "\u25A4"),
    ("pomodoro", "Pomodoro", "\u23F1"),
    ("study", "Study Tracker", "\u2726"),
    ("statistics", "Statistics", "\u2261"),
    ("goals", "Goals", "\u2691"),
    ("projects", "Projects", "\u2699"),
    ("focus", "Focus Mode", "\u25C9"),
    ("settings", "Settings", "\u2699"),
]


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate: Callable[[str], None], **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            corner_radius=0,
            width=220,
            **kwargs,
        )
        self.on_navigate = on_navigate
        self._buttons: dict[str, ctk.CTkButton] = {}
        self._active_key: str | None = None

        self.pack_propagate(False)
        self._build()

    def _build(self) -> None:
        title = ctk.CTkLabel(
            self,
            text="Momentum",
            font=font_heading(),
            text_color=COLORS["accent"],
        )
        title.pack(pady=(28, 4), padx=20, anchor="w")

        subtitle = ctk.CTkLabel(
            self,
            text="Consistency Coach",
            font=font_body(),
            text_color=COLORS["text_secondary"],
        )
        subtitle.pack(pady=(0, 24), padx=20, anchor="w")

        for key, label, glyph in NAV_ITEMS:
            btn = ctk.CTkButton(
                self,
                text=f"  {glyph}   {label}",
                anchor="w",
                font=font_body(),
                fg_color="transparent",
                hover_color=COLORS["surface_alt"],
                text_color=COLORS["text_primary"],
                corner_radius=CORNER_RADIUS,
                height=40,
                command=lambda k=key: self._handle_click(k),
            )
            btn.pack(fill="x", padx=12, pady=3)
            self._buttons[key] = btn

        self._set_active("dashboard")

    def _handle_click(self, key: str) -> None:
        self._set_active(key)
        self.on_navigate(key)

    def _set_active(self, key: str) -> None:
        if self._active_key and self._active_key in self._buttons:
            self._buttons[self._active_key].configure(fg_color="transparent")
        if key in self._buttons:
            self._buttons[key].configure(fg_color=COLORS["accent"])
        self._active_key = key
