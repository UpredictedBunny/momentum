"""
habit_view.py
-------------
Habit Tracker page.  Builds its layout once; on checkbox toggle only
the affected widget and the header stats update (no full rebuild).
On structural changes (add / deactivate / reactivate) the habit list
section is repopulated in-place without destroying the outer frame.

Layout:
    Header   → title + date + "X/Y done today" + progress bar
    Add card → text entry + Add button
    Tabs     → [Active Habits] [All Habits]
    List     → one row per habit: checkbox | streak badge | action btn
"""

from __future__ import annotations

from datetime import date

import customtkinter as ctk

from controllers.habit_controller import HabitController
from themes.dark_theme import COLORS, CORNER_RADIUS, FONTS
from utils.logger import get_logger

log = get_logger("views.habit_view")


def _font(size: int, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONTS["family"], size=size, weight=weight)


class HabitView(ctk.CTkScrollableFrame):
    """Full Habit Tracker page — scrollable."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(
            master,
            fg_color=COLORS["background"],
            scrollbar_button_color=COLORS["surface_alt"],
            scrollbar_button_hover_color=COLORS["border"],
            **kwargs,
        )
        self.controller = HabitController()
        self.grid_columnconfigure(0, weight=1)

        # View state
        self._show_all: bool = False

        # Widget refs for in-place refresh
        self._progress_bar: ctk.CTkProgressBar | None = None
        self._progress_label: ctk.CTkLabel | None = None
        self._active_tab_btn: ctk.CTkButton | None = None
        self._all_tab_btn: ctk.CTkButton | None = None
        self._list_frame: ctk.CTkFrame | None = None
        self._entry: ctk.CTkEntry | None = None
        self._status_label: ctk.CTkLabel | None = None

        # habit_id → (CTkCheckBox, BooleanVar) — rebuilt on list refresh
        self._habit_widgets: dict[int, tuple[ctk.CTkCheckBox, ctk.BooleanVar]] = {}

        # Grid row where the list frame lives (set during _build)
        self._list_grid_row: int = 4

        self._build()
        log.info("HabitView initialized.")

    # ------------------------------------------------------------------
    # Build skeleton (called once)
    # ------------------------------------------------------------------
    def _build(self) -> None:
        row = 0
        row = self._build_header(row)        # rows 0-1
        row = self._build_add_card(row)      # row 2
        row = self._build_tabs(row)          # row 3
        self._list_grid_row = row
        self._build_list_frame()             # row 4

    # ------------------------------------------------------------------
    # Header: title, date, completion count, progress bar
    # ------------------------------------------------------------------
    def _build_header(self, row: int) -> int:
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=row, column=0, sticky="ew", padx=24, pady=(24, 4))
        hdr.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            hdr,
            text="✓  Habit Tracker",
            font=_font(26, "bold"),
            text_color=COLORS["secondary"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        # Date
        ctk.CTkLabel(
            hdr,
            text=date.today().strftime("%A, %B %d, %Y"),
            font=_font(13),
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Completion count (top-right of header)
        comp, total = self.controller.get_today_completion()
        self._progress_label = ctk.CTkLabel(
            hdr,
            text=self._progress_text(comp, total),
            font=_font(13, "bold"),
            text_color=COLORS["secondary"],
            anchor="e",
        )
        self._progress_label.grid(row=0, column=1, rowspan=2, sticky="e", padx=(16, 0))

        # Progress bar (full width, row below header frame)
        self._progress_bar = ctk.CTkProgressBar(
            self,
            height=6,
            progress_color=COLORS["secondary"],
            fg_color=COLORS["surface_alt"],
            corner_radius=3,
        )
        self._progress_bar.set(comp / total if total > 0 else 0)
        self._progress_bar.grid(row=row + 1, column=0, sticky="ew", padx=24, pady=(6, 12))

        return row + 2

    # ------------------------------------------------------------------
    # Add-habit card
    # ------------------------------------------------------------------
    def _build_add_card(self, row: int) -> int:
        card = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=row, column=0, sticky="ew", padx=24, pady=(0, 8))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="Add New Habit",
            font=_font(12, "bold"),
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 6))

        # NOTE: no textvariable here — CustomTkinter suppresses placeholder_text
        # whenever a textvariable is bound, which left this input with no hint.
        entry = ctk.CTkEntry(
            card,
            placeholder_text="Habit name…",
            font=_font(13),
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            height=36,
        )
        entry.grid(row=1, column=0, sticky="ew", padx=(16, 8), pady=(0, 4))
        entry.bind("<Return>", lambda _e: self._on_add())
        self._entry = entry

        add_btn = ctk.CTkButton(
            card,
            text="+ Add",
            font=_font(13, "bold"),
            fg_color=COLORS["secondary"],
            hover_color=COLORS["secondary_hover"],
            text_color=COLORS["on_accent"],
            height=36,
            width=80,
            corner_radius=CORNER_RADIUS,
            command=self._on_add,
        )
        add_btn.grid(row=1, column=1, padx=(0, 16), pady=(0, 4))

        # Status label (error / success feedback)
        self._status_label = ctk.CTkLabel(
            card,
            text="",
            font=_font(11),
            text_color=COLORS["danger"],
            anchor="w",
        )
        self._status_label.grid(row=2, column=0, columnspan=2, sticky="w",
                                padx=16, pady=(0, 10))

        return row + 1

    # ------------------------------------------------------------------
    # Tab strip
    # ------------------------------------------------------------------
    def _build_tabs(self, row: int) -> int:
        tab_strip = ctk.CTkFrame(self, fg_color="transparent")
        tab_strip.grid(row=row, column=0, sticky="w", padx=24, pady=(0, 6))

        self._active_tab_btn = ctk.CTkButton(
            tab_strip,
            text="Active Habits",
            font=_font(13, "bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["surface_alt"],
            text_color=COLORS["text_primary"],
            height=32,
            width=130,
            corner_radius=CORNER_RADIUS,
            command=self._switch_to_active,
        )
        self._active_tab_btn.pack(side="left", padx=(0, 6))

        self._all_tab_btn = ctk.CTkButton(
            tab_strip,
            text="All Habits",
            font=_font(13),
            fg_color="transparent",
            hover_color=COLORS["surface_alt"],
            text_color=COLORS["text_secondary"],
            height=32,
            width=110,
            corner_radius=CORNER_RADIUS,
            command=self._switch_to_all,
        )
        self._all_tab_btn.pack(side="left")

        return row + 1

    # ------------------------------------------------------------------
    # Habit list frame + population
    # ------------------------------------------------------------------
    def _build_list_frame(self) -> None:
        """Create the list container and populate it. Called once from _build."""
        self._list_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=COLORS["border"],
        )
        self._list_frame.grid(
            row=self._list_grid_row, column=0, sticky="ew", padx=24, pady=(0, 24)
        )
        self._list_frame.grid_columnconfigure(0, weight=1)
        self._populate_list()

    def _populate_list(self) -> None:
        """Clear and repopulate the habit rows inside the list frame."""
        for widget in self._list_frame.winfo_children():
            widget.destroy()
        self._habit_widgets.clear()

        habits = (
            self.controller.get_all_habits_with_stats()
            if self._show_all
            else self.controller.get_habits_with_stats()
        )

        if not habits:
            msg = "No habits yet. Add one above." if not self._show_all else "No habits found."
            ctk.CTkLabel(
                self._list_frame,
                text=msg,
                font=_font(13),
                text_color=COLORS["text_secondary"],
            ).pack(pady=24)
            return

        for i, habit in enumerate(habits):
            if i > 0:
                sep = ctk.CTkFrame(self._list_frame, height=1, fg_color=COLORS["border"])
                sep.pack(fill="x", padx=8)
            self._build_habit_row(habit)

    def _build_habit_row(self, habit: dict) -> None:
        is_active = bool(habit.get("is_active", 1))
        is_done = bool(habit["is_completed"])
        streak = int(habit.get("streak", 0))

        row_frame = ctk.CTkFrame(self._list_frame, fg_color="transparent")
        row_frame.pack(fill="x", padx=8, pady=6)
        row_frame.grid_columnconfigure(0, weight=1)

        # --- Checkbox (col 0) ---
        text_color = (
            COLORS["text_secondary"] if is_done
            else COLORS["border"] if not is_active
            else COLORS["text_primary"]
        )
        var = ctk.BooleanVar(value=is_done)
        cb = ctk.CTkCheckBox(
            row_frame,
            text=habit["name"],
            variable=var,
            font=_font(14),
            text_color=text_color,
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
            fg_color=COLORS["secondary"],
            hover_color=COLORS["secondary_hover"],
            border_color=COLORS["border"],
            state="normal" if is_active else "disabled",
            command=lambda hid=habit["id"], v=var: self._on_toggle(hid, v),
        )
        cb.grid(row=0, column=0, sticky="w")

        if is_active:
            self._habit_widgets[habit["id"]] = (cb, var)

        # --- Streak badge (col 1) ---
        if streak > 0:
            ctk.CTkLabel(
                row_frame,
                text=f"🔥 {streak}d",
                font=_font(12),
                text_color=COLORS["warning"],
                fg_color=COLORS["surface_alt"],
                corner_radius=6,
                padx=8,
                pady=2,
            ).grid(row=0, column=1, padx=(8, 0))

        # --- Action button (col 2) ---
        if self._show_all and not is_active:
            ctk.CTkButton(
                row_frame,
                text="Reactivate",
                font=_font(11),
                fg_color="transparent",
                hover_color=COLORS["surface_alt"],
                text_color=COLORS["secondary"],
                border_width=1,
                border_color=COLORS["secondary"],
                height=28,
                width=90,
                corner_radius=CORNER_RADIUS,
                command=lambda hid=habit["id"]: self._on_reactivate(hid),
            ).grid(row=0, column=2, padx=(8, 0))
        elif is_active:
            ctk.CTkButton(
                row_frame,
                text="Remove",
                font=_font(11),
                fg_color="transparent",
                hover_color=COLORS["surface_alt"],
                text_color=COLORS["danger"],
                border_width=1,
                border_color=COLORS["danger"],
                height=28,
                width=76,
                corner_radius=CORNER_RADIUS,
                command=lambda hid=habit["id"]: self._on_deactivate(hid),
            ).grid(row=0, column=2, padx=(8, 0))

    # ------------------------------------------------------------------
    # Stats refresh (header only — no list rebuild)
    # ------------------------------------------------------------------
    def _refresh_stats(self) -> None:
        comp, total = self.controller.get_today_completion()
        if self._progress_label:
            self._progress_label.configure(text=self._progress_text(comp, total))
        if self._progress_bar:
            self._progress_bar.set(comp / total if total > 0 else 0)

    @staticmethod
    def _progress_text(comp: int, total: int) -> str:
        return f"{comp}/{total} done today"

    # ------------------------------------------------------------------
    # Tab switching
    # ------------------------------------------------------------------
    def _switch_to_active(self) -> None:
        if self._show_all:
            self._show_all = False
            self._active_tab_btn.configure(
                fg_color=COLORS["accent"],
                font=_font(13, "bold"),
                text_color=COLORS["text_primary"],
            )
            self._all_tab_btn.configure(
                fg_color="transparent",
                font=_font(13),
                text_color=COLORS["text_secondary"],
            )
            self._populate_list()

    def _switch_to_all(self) -> None:
        if not self._show_all:
            self._show_all = True
            self._all_tab_btn.configure(
                fg_color=COLORS["accent"],
                font=_font(13, "bold"),
                text_color=COLORS["text_primary"],
            )
            self._active_tab_btn.configure(
                fg_color="transparent",
                font=_font(13),
                text_color=COLORS["text_secondary"],
            )
            self._populate_list()

    # ------------------------------------------------------------------
    # Interaction handlers
    # ------------------------------------------------------------------
    def _on_toggle(self, habit_id: int, var: ctk.BooleanVar) -> None:
        """Checkbox was clicked — var already reflects new state."""
        old_state = not var.get()
        try:
            new_state = self.controller.toggle_habit(habit_id, old_state)
            var.set(new_state)
            if habit_id in self._habit_widgets:
                cb, _ = self._habit_widgets[habit_id]
                cb.configure(
                    text_color=(
                        COLORS["text_secondary"] if new_state else COLORS["text_primary"]
                    )
                )
            self._refresh_stats()
        except Exception:
            log.exception("Error toggling habit %d", habit_id)
            var.set(old_state)  # revert on failure

    def _on_add(self) -> None:
        name = (self._entry.get() if self._entry is not None else "").strip()
        if not name:
            self._set_status("Name cannot be empty.", error=True)
            return
        ok = self.controller.add_habit(name)
        if ok:
            self._entry.delete(0, "end")
            self._set_status(f'"{name}" added.', error=False)
            self._populate_list()
            self._refresh_stats()
        else:
            self._set_status("Could not add (name may already exist).", error=True)

    def _on_deactivate(self, habit_id: int) -> None:
        try:
            self.controller.deactivate_habit(habit_id)
            self._populate_list()
            self._refresh_stats()
        except Exception:
            log.exception("Error deactivating habit %d", habit_id)

    def _on_reactivate(self, habit_id: int) -> None:
        try:
            self.controller.reactivate_habit(habit_id)
            self._populate_list()
            self._refresh_stats()
        except Exception:
            log.exception("Error reactivating habit %d", habit_id)

    def _set_status(self, msg: str, *, error: bool) -> None:
        if self._status_label:
            color = COLORS["danger"] if error else COLORS["secondary"]
            self._status_label.configure(text=msg, text_color=color)
            # Auto-clear after 3 s
            self.after(3000, lambda: (
                self._status_label.configure(text="")
                if self._status_label.winfo_exists() else None
            ))
