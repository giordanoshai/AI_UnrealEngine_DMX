# AetherLight Pro

AetherLight Pro is a Python-based DMX lighting project for managing fixtures, projects, and Unreal Engine integration. The repository combines project-based fixture configuration, GDTF/MVR loading, cue playback, and sACN DMX output, making it useful for lighting design, simulation, and live control workflows.

## Overview

This project focuses on three core workflows:

- Import and manage GDTF fixture definitions
- Organize lighting scenes and projects as reusable saved JSON projects
- Send DMX values to Unreal Engine via sACN / DMX streaming

The main app entry point is `main.py`, and the core logic is organized under the `aetherlight/` package.

## Features

- Project-based configuration with automatic saving
- GDTF library database for shared fixture metadata
- MVR import and fixture linking
- Cue playback and effect examples
- sACN sender for Unreal Engine DMX control
- Qt desktop interface based on PyQt6
- Documentation for project management and sACN workflows

## Repository Structure

```text
.
├── aetherlight/              # Core application package
│   ├── database/            # Database-related code
│   ├── gui/                 # Qt UI components
│   ├── utils/               # Helper utilities
│   ├── cue_player.py        # Cue playback logic
│   ├── fixture_config.py    # Fixture configuration support
│   ├── fixture_translator.py
│   ├── gdtf_parser.py       # GDTF parsing
│   ├── models.py            # Domain models
│   ├── mvr_importer.py      # MVR import support
│   ├── project_manager.py   # Project save/load logic
│   ├── sacn_sender.py       # sACN sending logic
│   └── ...
├── data/                    # Data assets or samples
├── docs/                    # Documentation and notes
├── examples/                # Example usage and user flows
├── mvr_data/                # Sample MVR data
├── projects/                # Saved project JSON files
├── gdtf_library.db          # Local GDTF library database
├── main.py                  # Application entry point
├── effect_examples.py        # Example effect scripts
├── demo_cue_player.py       # Demo cue player usage
├── upload_effects_to_supabase.py
├── pyproject.toml           # Python project metadata
├── README.md                # Project overview
├── README_SACN.md           # sACN setup and usage notes
├── README_项目管理.md       # Project management documentation
├── test_*.py                # Validation and smoke tests
└── ...
```

## Quick Start

### Requirements

- Python 3.12+
- PyQt6
- Optional: sACN-related runtime dependency for network DMX transmission

### Install and run

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install PyQt6
python main.py
```

If you are specifically testing Unreal Engine DMX delivery, see the sACN notes in `README_SACN.md` and the docs under `docs/`.

## Using the Application

### 1. Create or open a project

The app supports project-based management so you can keep fixture definitions and scenes grouped into separate project files.

- New project: create a blank project
- Open project: load an existing saved project
- Save project: persist fixture and scene configuration
- Projects are stored in the `projects/` directory

### 2. Import fixtures and GDTF data

Use the project UI to import GDTF files and related lighting profiles. The program stores imported fixture definitions in the local `gdtf_library.db` database so they can be reused across projects.

### 3. Import MVR / scene data (if applicable)

The project includes MVR import support and related logic for linking imported stage-data to fixture definitions.

### 4. Run cue or effect playback

The repo includes example scripts for effects and cue playback:

```bash
python effect_examples.py
python demo_cue_player.py
```

## Unreal Engine / sACN Workflow

The repository includes specific documentation for sending DMX data to Unreal Engine using sACN.

Key references:

- `README_SACN.md`
- `docs/sacn_ue_guide.md`
- `docs/sacn_implementation_summary.md`
- `docs/multi_fixture_control.md`

These documents cover the protocol setup, UE DMX configuration, and troubleshooting guidance for receiving DMX in Unreal Engine.

## Project Management Notes

The project management guide in `README_项目管理.md` describes how the application:

- reuses the shared GDTF library database
- automatically saves project files
- tracks unsaved changes with a project state indicator
- supports multiple project files while keeping one active project at a time

## Documentation

The repo's documentation is organized in the `docs/` folder and includes notes related to:

- cue player usage
- effect cue editor
- sACN implementation
- fixture configuration
- bug fixes and project maintenance

## Development Notes

This repository is structured as a Python project with a PyQt-based UI and a set of supporting scripts for testing, sample effects, and DMX workflows. It is designed for lighting and stage automation use cases, especially when visualizing or controlling DMX fixtures from Unreal Engine.

## License

No explicit license file is present in the repository root. If you plan to distribute or reuse this project, confirm the repository's licensing status before publication or commercial use.

## Contributing

This project appears to be a personal or experimental DMX tooling repository. If you are extending it, a good workflow is:

1. Keep the `aetherlight/` package as the canonical logic layer
2. Add focused tests for fixture parsing or project behavior
3. Document protocol and UI changes in `docs/`
4. Keep example scripts aligned with the app's current entry points

## Related Files

- `main.py` — UI/application entry point
- `effect_examples.py` — example effect sequences
- `demo_cue_player.py` — cue playback demo
- `README_SACN.md` — Unreal Engine + sACN guide
- `README_项目管理.md` — project management guide


