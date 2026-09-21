"""
placeholder_view.py
--------------------
Temporary stand-in for feature pages that haven't been built yet in
this step-by-step build process. Once e.g. the real Dashboard view is
built, MainWindow will register DashboardView instead of this stub for
the "dashboard" key.
"""

from __future__ import annotations

import customtkinter as ctk

from themes.dark_theme import COLORS, font_body, font_heading


class PlaceholderView(ctk.CTkFrame):
    def __init__(self, master, page_title: str, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)

        ctk.CTkLabel(
            self,
            text=page_title,
            font=font_heading(),
            text_color=COLORS["text_primary"],
        ).pack(pady=(40, 8))

        ctk.CTkLabel(
            self,
            text="This module will be built in an upcoming step.",
            font=font_body(),
            text_color=COLORS["text_secondary"],
        ).pack()
