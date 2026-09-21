"""
main_window.py
---------------
The application shell. Owns the CTk root window, the persistent
Sidebar, and a content area where individual page views are swapped
in and out. This file stays stable as new feature modules get added --
you only ever add one line to PAGE_REGISTRY.
"""

from __future__ import annotations

import customtkinter as ctk

from config.settings import settings
from themes.dark_theme import COLORS, apply_appearance
from utils.logger import get_logger
from views.components.sidebar import Sidebar, NAV_ITEMS
from views.components.placeholder_view import PlaceholderView
from views.dashboard_view import DashboardView
from views.habit_view import HabitView
from views.routine_view import RoutineView
from views.pomodoro_view import PomodoroView
from views.study_view import StudyView
from views.calendar_view import CalendarView
from views.statistics_view import StatisticsView
from views.goals_view import GoalsView
from views.projects_view import ProjectsView
from views.focus_view import FocusView
from views.settings_view import SettingsView

log = get_logger("views.main_window")

# Maps a page key -> a factory function that builds that page's view.
# As real feature views are built (DashboardView, RoutineView, ...),
# they get registered here, replacing the PlaceholderView entry.
PAGE_REGISTRY: dict[str, callable] = {
    key: (lambda master, label=label: PlaceholderView(master, label))
    for key, label, _ in NAV_ITEMS
}

# Register real views
PAGE_REGISTRY["dashboard"] = lambda master: DashboardView(master)
PAGE_REGISTRY["habits"] = lambda master: HabitView(master)
PAGE_REGISTRY["routine"] = lambda master: RoutineView(master)
PAGE_REGISTRY["calendar"] = lambda master: CalendarView(master)
PAGE_REGISTRY["pomodoro"] = lambda master: PomodoroView(master)
PAGE_REGISTRY["study"] = lambda master: StudyView(master)
PAGE_REGISTRY["statistics"] = lambda master: StatisticsView(master)
PAGE_REGISTRY["goals"] = lambda master: GoalsView(master)
PAGE_REGISTRY["projects"] = lambda master: ProjectsView(master)
PAGE_REGISTRY["focus"] = lambda master: FocusView(master)
PAGE_REGISTRY["settings"] = lambda master: SettingsView(master)


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        # Must run before the root window is created, otherwise the window is
        # built in the system appearance mode and then repainted dark (flash).
        apply_appearance()
        super().__init__()

        self.title(settings.app.name)
        self.geometry(f"{settings.app.window_width}x{settings.app.window_height}")
        self.minsize(settings.app.min_width, settings.app.min_height)
        self.configure(fg_color=COLORS["background"])

        self._current_view: ctk.CTkFrame | None = None
        self._build_layout()
        log.info("MainWindow initialized.")

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, on_navigate=self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.content_area = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        self.show_page("dashboard")

    def show_page(self, page_key: str) -> None:
        """Destroy the current page view and mount the requested one."""
        if page_key not in PAGE_REGISTRY:
            log.warning("Unknown page key requested: %s", page_key)
            return

        if self._current_view is not None:
            self._current_view.destroy()

        factory = PAGE_REGISTRY[page_key]
        view = factory(self.content_area)
        view.grid(row=0, column=0, sticky="nsew")
        self._current_view = view
        log.info("Navigated to page: %s", page_key)
