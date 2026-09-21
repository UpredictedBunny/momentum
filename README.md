# Momentum

> A polished desktop productivity coach built with Python, CustomTkinter, and SQLite.

Momentum brings everyday productivity workflows into one focused desktop application.

## ✨ Current Release

**Frozen QA baseline — v1.0.0**

The current baseline has been functionally tested and packaged as a Windows executable. The application source, database schema, business logic, and architecture are treated as a stable reference build.

## Features

- **Dashboard** — productivity overview
- **Daily Routine** — recurring routines and daily tracking
- **Habit Tracker** — habit progress and streaks
- **Calendar** — activity planning and review
- **Pomodoro** — focused work sessions
- **Study Tracker** — study activity tracking
- **Statistics** — productivity data and visualizations
- **Goals** — goal management
- **Projects** — project organization
- **Focus Mode** — focused workflow
- **Settings** — application preferences

## 🏗️ Architecture

Momentum uses a layered structure that keeps presentation, coordination, business logic, data models, and persistence separated:

```text
View
  ↓
Controller
  ↓
Service
  ↓
Model
  ↓
DatabaseManager
  ↓
SQLite
```

### Project structure

```text
momentum/
├── config/          # Application configuration
├── controllers/     # UI-to-business coordination
├── database/        # SQLite access and schema
├── models/          # Application data models
├── services/        # Business logic
├── themes/          # UI theme definitions
├── utils/            # Shared utilities and logging
├── views/            # CustomTkinter UI
├── data/             # Application database
├── backups/          # Database backups
├── logs/             # Application logs
├── main.py           # Application entry point
└── requirements.txt  # Python dependencies
```

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Application runtime |
| CustomTkinter | Desktop UI |
| SQLite | Local data storage |
| Matplotlib | Data visualization |
| Pillow | Image handling |
| Plyer | Desktop notifications |
| PyInstaller | Windows packaging |

## 🚀 Run From Source

Clone the repository:

```bash
git clone https://github.com/UpredictedBunny/momentum.git
cd momentum
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

## 🪟 Windows Application

The Windows build is produced separately with PyInstaller.

The intended distribution model is:

- **Source code** → this repository
- **Windows executable** → GitHub Releases

The tested `Momentum.exe` build will be distributed as a release artifact rather than committed into the source tree.

## 🧪 QA & Packaging

The frozen application has been tested from source and packaged as a Windows executable.

The packaged build requires the application's runtime resources, including configuration, database, schema, and theme directories. The working build has been tested after bundling those resources.

## 🔒 Frozen Baseline

This repository represents a stable reference point for Momentum.

Future work should branch from the frozen baseline and preserve:

- Working business logic
- Database schema
- Application architecture
- Existing functionality

Repository documentation, release packaging, and presentation can evolve independently of the application baseline.

## 📸 Screenshots

Screenshots and additional visual documentation will be added as part of the repository presentation.

## 📄 License

License information will be added when the project license is selected.
