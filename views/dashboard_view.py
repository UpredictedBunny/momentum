"""
dashboard_view.py
-----------------
The main Dashboard page. Builds the layout once and refreshes
individual sections in-place — no full window recreation.
"""

from __future__ import annotations

import customtkinter as ctk

from controllers.dashboard_controller import DashboardController
from services.dashboard_service import DashboardSummary
from themes.dark_theme import COLORS, FONTS, CORNER_RADIUS, font_body, font_heading
from utils.logger import get_logger

log = get_logger("views.dashboard_view")

# Section font helpers
def _font(size: int, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONTS["family"], size=size, weight=weight)


class DashboardView(ctk.CTkScrollableFrame):
    """Full Dashboard page — scrollable."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["background"],
            scrollbar_button_color=COLORS["surface_alt"],
            scrollbar_button_hover_color=COLORS["border"],
            **kwargs,
        )
        self.controller = DashboardController()
        self.grid_columnconfigure(0, weight=1)

        # Mutable state — maps (type, id) -> (checkbox_widget, state_var)
        self._habit_widgets: dict[int, tuple[ctk.CTkCheckBox, ctk.BooleanVar]] = {}
        self._routine_widgets: dict[int, tuple[ctk.CTkCheckBox, ctk.BooleanVar]] = {}

        # References to label widgets updated on refresh
        self._progress_label: ctk.CTkLabel | None = None
        self._progress_bar: ctk.CTkProgressBar | None = None
        self._today_progress_label: ctk.CTkLabel | None = None
        self._xp_label: ctk.CTkLabel | None = None
        self._streak_label: ctk.CTkLabel | None = None
        self._habits_done_label: ctk.CTkLabel | None = None
        self._level_label: ctk.CTkLabel | None = None
        self._pomo_label: ctk.CTkLabel | None = None
        self._focus_label: ctk.CTkLabel | None = None
        self._study_label: ctk.CTkLabel | None = None
        self._weekly_bars: list[tuple[ctk.CTkProgressBar, ctk.CTkLabel]] = []
        self._weekly_day_labels: list[ctk.CTkLabel] = []

        self._build()
        log.info("DashboardView initialized.")

    # ------------------------------------------------------------------
    # Build skeleton once
    # ------------------------------------------------------------------
    def _build(self) -> None:
        summary = self.controller.get_summary()
        row = 0

        # ---- Header ----
        row = self._build_header(row, summary)

        # ---- Summary cards ----
        row = self._build_summary_cards(row, summary)

        # ---- Body: routine + habits side-by-side, focus/study ----
        row = self._build_body(row, summary)

        # ---- Weekly overview ----
        row = self._build_weekly(row, summary)

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    def _build_header(self, row: int, summary: DashboardSummary) -> int:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=row, column=0, sticky="ew", padx=24, pady=(24, 8))
        header.grid_columnconfigure(1, weight=1)

        # Greeting + date
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        self._greeting_label = ctk.CTkLabel(
            left,
            text=f"{summary.greeting} 👋",
            font=_font(26, "bold"),
            text_color=COLORS["text_primary"],
        )
        self._greeting_label.pack(anchor="w")

        self._date_label = ctk.CTkLabel(
            left,
            text=summary.date_str,
            font=font_body(),
            text_color=COLORS["text_secondary"],
        )
        self._date_label.pack(anchor="w")

        # Progress on the right
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")

        self._progress_label = ctk.CTkLabel(
            right,
            text=self._progress_text(summary),
            font=_font(13),
            text_color=COLORS["text_secondary"],
        )
        self._progress_label.pack(anchor="e")

        self._progress_bar = ctk.CTkProgressBar(
            right,
            width=200,
            height=8,
            progress_color=COLORS["accent"],
            fg_color=COLORS["surface_alt"],
            corner_radius=4,
        )
        self._progress_bar.set(self._progress_pct(summary))
        self._progress_bar.pack(anchor="e", pady=(4, 0))

        return row + 1

    # ------------------------------------------------------------------
    # Summary cards
    # ------------------------------------------------------------------
    def _build_summary_cards(self, row: int, summary: DashboardSummary) -> int:
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=row, column=0, sticky="ew", padx=24, pady=(8, 4))
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)

        def make_card(parent, col, icon, label, value_text, color):
            card = ctk.CTkFrame(
                parent,
                fg_color=COLORS["surface"],
                corner_radius=CORNER_RADIUS,
                border_width=1,
                border_color=COLORS["border"],
            )
            card.grid(row=0, column=col, sticky="ew", padx=6, pady=4)
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(card, text=icon, font=_font(22), text_color=color).grid(
                row=0, column=0, padx=16, pady=(14, 0), sticky="w"
            )
            ctk.CTkLabel(
                card, text=label, font=_font(11), text_color=COLORS["text_secondary"]
            ).grid(row=1, column=0, padx=16, sticky="w")

            val_lbl = ctk.CTkLabel(
                card, text=value_text, font=_font(20, "bold"), text_color=color
            )
            val_lbl.grid(row=2, column=0, padx=16, pady=(2, 14), sticky="w")
            return val_lbl

        # Card 0: Today's Progress
        prog_txt = f"{summary.habits_completed + summary.routine_completed}/{summary.habits_total + summary.routine_total}"
        self._today_progress_label = make_card(
            cards_frame, 0, "📊", "Today's Progress", prog_txt, COLORS["accent"]
        )

        # Card 1: Habits done
        hab_txt = f"{summary.habits_completed}/{summary.habits_total}"
        self._habits_done_label = make_card(
            cards_frame, 1, "✓", "Habits Done", hab_txt, COLORS["secondary"]
        )

        # Card 2: Streak
        self._streak_label = make_card(
            cards_frame, 2, "🔥", "Best Streak", f"{summary.streak} days", COLORS["warning"]
        )

        # Card 3: XP Today
        self._xp_label = make_card(
            cards_frame, 3, "⚡", "XP Earned Today", f"{summary.xp_today} XP", COLORS["accent"]
        )

        return row + 1

    # ------------------------------------------------------------------
    # Body: routine left, habits right, then focus/study row
    # ------------------------------------------------------------------
    def _build_body(self, row: int, summary: DashboardSummary) -> int:
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=row, column=0, sticky="ew", padx=24, pady=4)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        self._routine_frame = self._build_section_card(
            body, 0, 0, "☀  Today's Routine", COLORS["accent"]
        )
        self._habits_frame = self._build_section_card(
            body, 0, 1, "✓  Habits", COLORS["secondary"]
        )
        self._populate_routine(summary)
        self._populate_habits(summary)

        # Focus + Study row
        focus_study = ctk.CTkFrame(self, fg_color="transparent")
        focus_study.grid(row=row + 1, column=0, sticky="ew", padx=24, pady=4)
        focus_study.grid_columnconfigure(0, weight=1)
        focus_study.grid_columnconfigure(1, weight=1)

        self._focus_card = self._build_section_card(
            focus_study, 0, 0, "⏱  Focus", COLORS["accent"]
        )
        self._study_card = self._build_section_card(
            focus_study, 0, 1, "📚  Study", COLORS["accent_alt"]
        )
        self._populate_focus(summary)
        self._populate_study(summary)

        return row + 2

    def _build_section_card(
        self, parent, grid_row: int, col: int, title: str, title_color: str
    ) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["surface"],
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=grid_row, column=col, sticky="nsew", padx=6, pady=6)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=title,
            font=_font(15, "bold"),
            text_color=title_color,
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        sep = ctk.CTkFrame(card, height=1, fg_color=COLORS["border"])
        sep.grid(row=1, column=0, sticky="ew", padx=12)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=8, pady=(4, 12))
        content.grid_columnconfigure(0, weight=1)
        card._content = content
        return card

    # ------------------------------------------------------------------
    # Populate routine checkboxes
    # ------------------------------------------------------------------
    def _populate_routine(self, summary: DashboardSummary) -> None:
        content = self._routine_frame._content
        for w in content.winfo_children():
            w.destroy()
        self._routine_widgets.clear()

        items = summary.routine_items
        if not items:
            ctk.CTkLabel(
                content, text="No routine items.", font=font_body(),
                text_color=COLORS["text_secondary"]
            ).grid(row=0, column=0, padx=8, pady=8)
            return

        for i, item in enumerate(items):
            var = ctk.BooleanVar(value=bool(item["is_completed"]))
            cb = ctk.CTkCheckBox(
                content,
                text=item["name"],
                variable=var,
                font=font_body(),
                text_color=COLORS["text_primary"] if not item["is_completed"] else COLORS["text_secondary"],
                checkmark_color=COLORS["background"],
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent"],
                border_color=COLORS["border"],
                corner_radius=6,
                command=lambda iid=item["id"], v=var: self._on_routine_toggle(iid, v),
            )
            cb.grid(row=i, column=0, sticky="w", padx=8, pady=4)
            self._routine_widgets[item["id"]] = (cb, var)

    # ------------------------------------------------------------------
    # Populate habit checkboxes
    # ------------------------------------------------------------------
    def _populate_habits(self, summary: DashboardSummary) -> None:
        content = self._habits_frame._content
        for w in content.winfo_children():
            w.destroy()
        self._habit_widgets.clear()

        habits = summary.habits
        if not habits:
            ctk.CTkLabel(
                content, text="No habits defined.", font=font_body(),
                text_color=COLORS["text_secondary"]
            ).grid(row=0, column=0, padx=8, pady=8)
            return

        for i, habit in enumerate(habits):
            var = ctk.BooleanVar(value=bool(habit["is_completed"]))
            cb = ctk.CTkCheckBox(
                content,
                text=f"{habit['icon']}  {habit['name']}" if habit.get("icon") else habit["name"],
                variable=var,
                font=font_body(),
                text_color=COLORS["text_primary"] if not habit["is_completed"] else COLORS["text_secondary"],
                checkmark_color=COLORS["background"],
                fg_color=COLORS["secondary"],
                hover_color=COLORS["secondary"],
                border_color=COLORS["border"],
                corner_radius=6,
                command=lambda hid=habit["id"], v=var: self._on_habit_toggle(hid, v),
            )
            cb.grid(row=i, column=0, sticky="w", padx=8, pady=4)
            self._habit_widgets[habit["id"]] = (cb, var)

    # ------------------------------------------------------------------
    # Populate focus
    # ------------------------------------------------------------------
    def _populate_focus(self, summary: DashboardSummary) -> None:
        content = self._focus_card._content
        for w in content.winfo_children():
            w.destroy()

        self._pomo_label = ctk.CTkLabel(
            content,
            text=f"🍅  {summary.pomodoro_sessions} session{'s' if summary.pomodoro_sessions != 1 else ''} completed",
            font=font_body(),
            text_color=COLORS["text_primary"],
        )
        self._pomo_label.grid(row=0, column=0, sticky="w", padx=8, pady=(6, 2))

        self._focus_label = ctk.CTkLabel(
            content,
            text=f"⏱  {summary.focus_minutes} focus minutes",
            font=font_body(),
            text_color=COLORS["text_secondary"],
        )
        self._focus_label.grid(row=1, column=0, sticky="w", padx=8, pady=(0, 6))

    # ------------------------------------------------------------------
    # Populate study
    # ------------------------------------------------------------------
    def _populate_study(self, summary: DashboardSummary) -> None:
        content = self._study_card._content
        for w in content.winfo_children():
            w.destroy()

        hours = summary.study_hours
        display = f"{hours:.1f}h" if hours != int(hours) else f"{int(hours)}h"
        self._study_label = ctk.CTkLabel(
            content,
            text=f"📖  {display} studied today",
            font=font_body(),
            text_color=COLORS["text_primary"],
        )
        self._study_label.grid(row=0, column=0, sticky="w", padx=8, pady=(6, 2))

        self._level_label = ctk.CTkLabel(
            content,
            text=f"⚡  Level {summary.level}  ·  {summary.xp_total} XP total",
            font=font_body(),
            text_color=COLORS["text_secondary"],
        )
        self._level_label.grid(row=1, column=0, sticky="w", padx=8, pady=(0, 6))

    # ------------------------------------------------------------------
    # Weekly overview
    # ------------------------------------------------------------------
    def _build_weekly(self, row: int, summary: DashboardSummary) -> int:
        card = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=row, column=0, sticky="ew", padx=24, pady=(4, 24))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="📅  Weekly Overview",
            font=_font(15, "bold"),
            text_color=COLORS["accent"],
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        sep = ctk.CTkFrame(card, height=1, fg_color=COLORS["border"])
        sep.grid(row=1, column=0, sticky="ew", padx=12)

        bars_frame = ctk.CTkFrame(card, fg_color="transparent")
        bars_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(10, 14))
        for i in range(7):
            bars_frame.grid_columnconfigure(i, weight=1)

        self._weekly_bars = []
        self._weekly_day_labels = []

        for i, day_data in enumerate(summary.weekly_progress):
            col_frame = ctk.CTkFrame(bars_frame, fg_color="transparent")
            col_frame.grid(row=0, column=i, padx=4, sticky="n")

            pct_lbl = ctk.CTkLabel(
                col_frame,
                text=f"{int(day_data['pct'])}%",
                font=_font(10),
                text_color=COLORS["text_secondary"],
            )
            pct_lbl.pack()

            bar = ctk.CTkProgressBar(
                col_frame,
                width=10,
                height=80,
                orientation="vertical",
                progress_color=COLORS["accent"],
                fg_color=COLORS["surface_alt"],
                corner_radius=4,
            )
            bar.set(day_data["pct"] / 100)
            bar.pack(pady=4)

            day_lbl = ctk.CTkLabel(
                col_frame,
                text=day_data["label"],
                font=_font(11),
                text_color=COLORS["text_secondary"],
            )
            day_lbl.pack()

            self._weekly_bars.append((bar, pct_lbl))

        return row + 1

    # ------------------------------------------------------------------
    # Interaction handlers
    # ------------------------------------------------------------------
    def _on_habit_toggle(self, habit_id: int, var: ctk.BooleanVar) -> None:
        # var has already been toggled by the checkbox widget
        old_state = not var.get()  # state before toggle
        try:
            new_state = self.controller.toggle_habit(habit_id, old_state)
            var.set(new_state)
            cb, _ = self._habit_widgets[habit_id]
            cb.configure(
                text_color=COLORS["text_secondary"] if new_state else COLORS["text_primary"]
            )
            self._refresh_header_and_cards()
            log.info("Habit %d toggled to %s", habit_id, new_state)
        except Exception:
            log.exception("Error toggling habit %d", habit_id)
            # Revert the checkbox on error
            var.set(old_state)

    def _on_routine_toggle(self, item_id: int, var: ctk.BooleanVar) -> None:
        old_state = not var.get()
        try:
            new_state = self.controller.toggle_routine_item(item_id, old_state)
            var.set(new_state)
            cb, _ = self._routine_widgets[item_id]
            cb.configure(
                text_color=COLORS["text_secondary"] if new_state else COLORS["text_primary"]
            )
            self._refresh_header_and_cards()
            log.info("Routine item %d toggled to %s", item_id, new_state)
        except Exception:
            log.exception("Error toggling routine item %d", item_id)
            var.set(old_state)

    # ------------------------------------------------------------------
    # Partial refresh — update labels without rebuilding layout
    # ------------------------------------------------------------------
    def _refresh_header_and_cards(self) -> None:
        try:
            summary = self.controller.get_summary()

            # Progress bar / label
            if self._progress_bar:
                self._progress_bar.set(self._progress_pct(summary))
            if self._progress_label:
                self._progress_label.configure(text=self._progress_text(summary))

            # Summary card values
            if self._today_progress_label:
                prog_total = summary.habits_total + summary.routine_total
                prog_done = summary.habits_completed + summary.routine_completed
                self._today_progress_label.configure(
                    text=f"{prog_done}/{prog_total}"
                )
            if self._habits_done_label:
                self._habits_done_label.configure(
                    text=f"{summary.habits_completed}/{summary.habits_total}"
                )
            if self._streak_label:
                self._streak_label.configure(text=f"{summary.streak} days")
            if self._xp_label:
                self._xp_label.configure(text=f"{summary.xp_today} XP")
            if self._level_label:
                self._level_label.configure(
                    text=f"⚡  Level {summary.level}  ·  {summary.xp_total} XP total"
                )

            # Weekly bars
            for i, (bar, pct_lbl) in enumerate(self._weekly_bars):
                if i < len(summary.weekly_progress):
                    d = summary.weekly_progress[i]
                    bar.set(d["pct"] / 100)
                    pct_lbl.configure(text=f"{int(d['pct'])}%")
        except Exception:
            log.exception("Error refreshing dashboard cards")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _progress_pct(summary: DashboardSummary) -> float:
        total = summary.habits_total + summary.routine_total
        done = summary.habits_completed + summary.routine_completed
        return (done / total) if total > 0 else 0.0

    @staticmethod
    def _progress_text(summary: DashboardSummary) -> str:
        total = summary.habits_total + summary.routine_total
        done = summary.habits_completed + summary.routine_completed
        return f"Daily progress: {done}/{total}"
