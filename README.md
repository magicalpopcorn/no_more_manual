# ROK Macro Automation

---

## 🚀 Overview

**ROK Macro Automation** is a robust, state-aware automation system designed for the game *Rise of Kingdoms (RoK)*. Built with Python and leveraging computer vision, it streamlines repetitive in-game tasks with high precision and human-like behavior. The system is modular, extensible, and engineered for reliability, making it ideal for both casual players and power users seeking efficiency and consistency.

- **Stealth Automation:** Reducing the risk of detection by the game’s anti-cheat systems.
- **Persistent State:** Remembers previous actions and UI states to minimize unnecessary operations.
- **Robust Logging:** Action-level, debug, and error logs with timestamps for easy troubleshooting.
- **Android Emulator Integration:** Works with LDPlayer instances via ADB & LDConsole for reliable automation.
- **Extensible Task System:** Easily register new tasks or modify existing ones via the modular agent system.
---

## ✨ Features

- **Resource Assistance:** (WIP) Automates the transfer of food, wood, stone, and gold between accounts, intelligently avoiding redundant clicks and selections.
- **Smart Gathering:** Sends up to 5 marches for resource farming, with customizable resource order and adaptive UI state tracking. Features an advanced fallback mechanism to ensure all 5 marches are always sent to resource nodes.
- **Gem Farming:** (WIP) Automated gem gathering with dedicated script for efficient resource collection.
- **Multi-Account Support:** Supports multiple user profiles and action modes (character, account, all accounts).

---

## 🧰 Tech Stack

| Component         | Description                                      |
|-------------------|--------------------------------------------------|
| Python3           | Core automation logic and orchestration          |
| ADB               | Communication with Android emulator instances    |
| LDPlayer API      | Android emulator management and control          |
| Tesseract OCR     | Smart text detection for in-game UI elements     |
| YOLO (Ultralytics)| Object detection for robust UI state recognition |
| OpenCV            | Computer vision and image processing             |
| OOP Architecture  | Modular classes for tasks, agents, and UI elements |
| Logging System    | Structured, timestamped logs for all actions     |

---

## 🏗️ Project Structure

```
├── worker_z.py            # Main worker script for general automation tasks
├── gem_z.py               # Dedicated gem farming automation script
├── profile.yml            # User configuration and account settings
├── src/                   # Core modules
│   ├── task/              # Task implementations (Gather, Collect, UseItems, etc.)
│   ├── agent/             # Agent system (Walker, Looper)
│   ├── ui/                # UI menu classes and interactions
│   ├── vision/            # Computer vision (YOLO, OCR, OpenCV)
│   ├── api/               # External API integrations (ADB, LDPlayer)
│   ├── element/           # UI element definitions and helpers
│   ├── logger.py          # Logging and debugging utilities
│   ├── rok_profile.py     # User profile and configuration management
│   ├── boot.py            # System initialization and setup
│   └── const.py           # Constants and configuration values
├── assets/                # Datasets, images, and YOLO model files
│   ├── dataset/           # Training datasets for YOLO models
│   ├── yolo_models/       # Trained YOLO model files (.pt)
│   ├── images/            # Reference images and screenshots
│   └── ico/               # Application icons
├── runs/                  # YOLO training outputs and automation logs
├── tmp/                   # Temporary files and screenshots
├── tools/                 # Utility scripts and development tools
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration for code formatting
└── README.md              # Project documentation
```

---

## ⚙️ How It Works

1. **Initialization:** Starts LDPlayer instance, establishes ADB connection, and loads user profile configuration.
2. **Task Registration:** Instantiates and registers desired tasks (e.g., gathering, gem farming, using items, collecting resources).
3. **Agent Execution:** The Walker agent executes tasks based on the selected mode (character, account, all accounts), using computer vision for UI detection.
4. **State Management:** Tracks UI states and adapts to changes, ensuring efficient automation flow.
5. **Logging:** All actions and errors are logged with timestamps for transparency and debugging.

---

## 🛠️ Getting Started

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
2. **Install Tesseract OCR:**
   - Download and install Tesseract for Windows from [here](https://github.com/tesseract-ocr/tesseract/wiki).
   - Add the Tesseract installation path to your system `PATH` environment variable.
3. **Configure your profile:** Edit `profile.yml` as needed.
4. **Run the automation:**
   ```sh
   python3 worker_z.py
   ```
    Note: Ctrl+C to stop the script

**Note:**
- The entire repository is developed and tested in a Windows environment.
- YOLO model training is performed in WSL (Windows Subsystem for Linux) and requires additional Python YOLO packages.
- For running automation, only Windows is supported.
---

## 📝 Current Features & Roadmap

### ✅ Implemented
- **Multi-Account Resource Gathering:** Automated resource collection across multiple accounts and characters
- **Smart Item Usage:** Automated use of boost items and shields
- **Resource Collection:** Automated collection of resources from various in-game sources
- **Profile Management:** Support for multiple account configurations via YAML
- **Computer Vision:** YOLO-based UI element detection and OCR text recognition
- **Android Emulator Integration:** Full LDPlayer and ADB support

### 🚧 In Development
- **Auto Gem Farming:** Enhanced gem collection automation (High Priority)

### 📋 Planned Features
- **CommanderY Integration:** Flask server to serve commands via RestAPI and WindowGUI
- **OperatorX Integration:** Discord bot service for remote command and control
- **Discord Commands:** Control automation via Discord chat interface
- **Advanced Scheduling:** Time-based task scheduling and automation
- **Web Dashboard:** Browser-based monitoring and control interface
---

## 📄 License

This project is licensed under the terms of the `docs/LICENSE` file.

---

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome! Please open an issue or submit a pull request.

---

## 📬 Contact

For questions or support, please open an issue on GitHub.

---

## 💡 Development Notes

### YOLO Model Training
- YOLO model training is performed in WSL (Windows Subsystem for Linux)
- Custom models are trained for ROK-specific UI elements
- Models are stored in `assets/yolo_models/` directory

### LDPlayer Configuration
**Recommended Settings:**
```1920x1080x32```

### Code Quality
- Code formatting with Black (line length: 100)
- Import sorting with isort
- Type hints and docstrings for better maintainability

---

*ROK Macro Automation is an independent project and is not affiliated with or endorsed by Lilith Games or Rise of Kingdoms.*


