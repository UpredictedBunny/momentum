import customtkinter as ctk

from config.settings import settings
from controllers.pomodoro_controller import PomodoroController
from themes.dark_theme import COLORS, font_display, font_body
from views.page_common import card, title


class PomodoroView(ctk.CTkFrame):
    """Pomodoro timer with session tracking and daily statistics."""

    def __init__(self, master):
        super().__init__(
            master,
            fg_color=COLORS["background"],
        )

        self.controller = PomodoroController()

        self.running = False
        self.remaining = 0
        self.preset_data = None
        self._timer_job = None

        self._build()

    def _build(self):
        title(
            self,
            "Pomodoro",
            "Focused work sessions with automatic logging.",
        )

        # Timer card
        timer_card = card(self)
        timer_card.pack(
            fill="x",
            padx=28,
            pady=12,
        )

        self.preset = ctk.CTkComboBox(
            timer_card,
            values=[
                preset["name"]
                for preset in settings.pomodoro.presets
            ],
            command=self._preset_changed,
        )
        self.preset.pack(pady=(24, 10))

        # IMPORTANT:
        # Create the timer BEFORE calling _preset_changed().
        self.timer = ctk.CTkLabel(
            timer_card,
            text="00:00",
            font=font_display(48),
            text_color=COLORS["accent"],
        )
        self.timer.pack(pady=12)

        self.status = ctk.CTkLabel(
            timer_card,
            text="Ready",
            font=font_body(),
            text_color=COLORS["text_secondary"],
        )
        self.status.pack()

        button_frame = ctk.CTkFrame(
            timer_card,
            fg_color="transparent",
        )
        button_frame.pack(pady=20)

        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start",
            command=self._start,
        )
        self.start_button.pack(
            side="left",
            padx=5,
        )

        self.reset_button = ctk.CTkButton(
            button_frame,
            text="Reset",
            command=self._reset,
            fg_color=COLORS["surface_alt"],
        )
        self.reset_button.pack(
            side="left",
            padx=5,
        )

        # Statistics card
        stats_card = card(self)
        stats_card.pack(
            fill="x",
            padx=28,
            pady=12,
        )

        self.stats = ctk.CTkLabel(
            stats_card,
            text="",
            font=font_body(),
        )
        self.stats.pack(pady=18)

        # Initialize preset only AFTER all widgets exist.
        if settings.pomodoro.presets:
            default_preset = settings.pomodoro.presets[0]["name"]
            self.preset.set(default_preset)
            self._preset_changed(default_preset)

        self._refresh_stats()

    def _preset_changed(self, name):
        """Load the selected Pomodoro preset."""
        if self.running:
            return

        presets = settings.pomodoro.presets

        if not presets:
            self.preset_data = None
            self.remaining = 0
            self._display()
            return

        self.preset_data = next(
            (
                preset
                for preset in presets
                if preset["name"] == name
            ),
            presets[0],
        )

        self.remaining = (
            int(self.preset_data["focus_minutes"]) * 60
        )

        self._display()
        self.status.configure(text="Ready")

    def _start(self):
        """Start the Pomodoro timer."""
        if self.running:
            return

        if not self.preset_data:
            return

        if self.remaining <= 0:
            self.remaining = (
                int(self.preset_data["focus_minutes"]) * 60
            )

        self.running = True

        self.preset.configure(state="disabled")
        self.start_button.configure(state="disabled")

        self.status.configure(
            text="Focusing…",
        )

        self._tick()

    def _tick(self):
        """Update the countdown every second."""
        if not self.running:
            return

        self._display()

        if self.remaining <= 0:
            self._complete_session()
            return

        self.remaining -= 1

        self._timer_job = self.after(
            1000,
            self._tick,
        )

    def _complete_session(self):
        """Record a completed Pomodoro session."""
        self.running = False
        self._timer_job = None

        self.remaining = 0
        self._display()

        self.status.configure(
            text="Session complete!",
        )

        if self.preset_data:
            self.controller.record(
                self.preset_data["name"],
                int(self.preset_data["focus_minutes"]),
                int(self.preset_data["break_minutes"]),
            )

        self.preset.configure(state="normal")
        self.start_button.configure(state="normal")

        self._refresh_stats()

    def _reset(self):
        """Reset the current Pomodoro timer."""
        self.running = False

        if self._timer_job is not None:
            try:
                self.after_cancel(self._timer_job)
            except Exception:
                pass

            self._timer_job = None

        self.preset.configure(state="normal")
        self.start_button.configure(state="normal")

        self._preset_changed(
            self.preset.get(),
        )

        self.status.configure(
            text="Ready",
        )

    def _display(self):
        """Update the countdown display."""
        minutes, seconds = divmod(
            max(0, int(self.remaining)),
            60,
        )

        self.timer.configure(
            text=f"{minutes:02d}:{seconds:02d}",
        )

    def _refresh_stats(self):
        """Refresh today's Pomodoro statistics."""
        stats = self.controller.stats()

        sessions = int(
            stats.get("sessions", 0)
        )

        focus_minutes = int(
            stats.get("focus_minutes", 0)
        )

        self.stats.configure(
            text=(
                f"Today: {sessions} session{'' if sessions == 1 else 's'} "
                f"· {focus_minutes} focused minute{'' if focus_minutes == 1 else 's'}"
            ),
        )
