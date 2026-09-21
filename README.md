# Momentum — Personal Productivity Coach

A desktop app (Python + CustomTkinter + SQLite) built as a real coach, not a to-do list.

## Architecture (Step 1 — this delivery)

```
momentum/
├── main.py                  # Entry point: init dirs, init DB, launch window
├── requirements.txt
├── config/
│   ├── config.json          # ALL tunable values live here (colors, times, habit names...)
│   └── settings.py          # Loads config.json once, exposes settings.theme.accent etc.
├── database/
│   ├── schema.sql           # Every table for every feature (see mapping below)
│   └── db_manager.py        # Single sqlite3 connection, query helpers, backups
├── models/
│   └── base_model.py        # Shared base class every future model (Habit, Goal...) extends
├── controllers/             # Business logic layer (populated as each feature is built)
├── views/
│   ├── main_window.py        # App shell: sidebar + swappable content area
│   └── components/
│       ├── sidebar.py         # Left nav rail, page-agnostic
│       └── placeholder_view.py# Stand-in for pages not yet built
├── themes/
│   └── dark_theme.py         # Colors/fonts pulled from config, used everywhere
├── utils/
│   └── logger.py             # Rotating file logger (works after PyInstaller packaging)
├── data/                    # momentum.db lives here (gitignored)
├── logs/                    # momentum.log
└── backups/                 # daily .db backups
```

### Why this shape
- **No hardcoded values** — every color, reminder time, habit name, XP amount lives in `config/config.json`. Change behavior without touching code.
- **MVC separation** — `models/` (data + SQL), `controllers/` (logic, will call models and feed views), `views/` (CustomTkinter UI only, no SQL).
- **One database entry point** — `DatabaseManager` is a singleton; nothing else opens a raw sqlite3 connection.
- **Registry-based navigation** — `main_window.py` has a `PAGE_REGISTRY` dict. Adding a real feature later means writing `views/dashboard_view.py` and swapping one line in the registry — the shell itself never changes.
- **Logging over print()** — matters once this is packaged into a windowed .exe with PyInstaller, where stdout disappears.

### Database schema (already created and verified working)
`routine_items`/`routine_logs`, `habits`/`habit_logs`, `calendar_days`, `pomodoro_sessions`, `study_logs`, `daily_reviews`, `goals`/`goal_milestones`, `projects`, `gamification_state`, `achievements`, `coach_notes` — covering routine, habits, calendar, pomodoro, study tracker, daily review, goals, projects, gamification, and AI coach notes.

### Verified so far
- `config/settings.py` loads correctly, dot-access works (`settings.theme.accent`).
- `database/db_manager.py` connects and creates all 14 tables from `schema.sql` cleanly.
- App shell (`main_window.py` + `sidebar.py`) wires up navigation between 11 pages, each currently a placeholder.

### Not yet installable in this sandbox
This sandbox has no network access, so `customtkinter` couldn't be pip-installed here to launch the actual window. The code itself follows the standard CustomTkinter API and will run as-is once you `pip install -r requirements.txt` on your machine.

## How to run
```bash
pip install -r requirements.txt
python main.py
```

## Build order (next steps — one module per response, as requested)
1. **Dashboard** (feature 1 + 19) — real widgets: date/time, streak, scores
2. **Daily Routine** (feature 2) — checklist UI wired to `routine_items`/`routine_logs`
3. **Habit Tracker** (feature 3) — streaks, missed days
4. **Calendar** (feature 4)
5. **Pomodoro Timer** (feature 5)
6. **Study Tracker** (feature 6) + matplotlib graphs
7. **Statistics** (feature 7)
8. **Daily/Weekly/Monthly Review** (features 8, 11, 12)
9. **Reminders & Motivation Engine** (features 9, 10, 13, 14) — plyer notifications
10. **Goals & Projects** (features 15, 16)
11. **Focus Mode, Gamification, AI Coach, Backup** (features 17, 18, 20, 21)

Tell me which one to build next — I'd suggest starting with the **Dashboard**, since it's the first thing you'll see and pulls data from most other modules.
