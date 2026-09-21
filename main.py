"""
main.py
-------
Entry point for Momentum. This file's only job is to:
1. Make sure runtime folders exist (data/, logs/, backups/)
2. Initialize the database (creates momentum.db + tables on first run)
3. Launch the main window

Run with:  python main.py
Build to .exe with:  pyinstaller --noconfirm --windowed --name Momentum main.py
"""

from __future__ import annotations

from config.settings import ensure_runtime_dirs
from database.db_manager import get_db
from utils.logger import get_logger
from views.main_window import MainWindow

log = get_logger("main")


def main() -> None:
    ensure_runtime_dirs()
    get_db()  # opens connection + applies schema.sql if needed
    log.info("Momentum starting up.")

    app = MainWindow()
    app.mainloop()

    log.info("Momentum shut down cleanly.")


if __name__ == "__main__":
    main()
