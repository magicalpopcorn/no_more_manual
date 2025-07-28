# ROK Macro Automation

**ROK Macro Automation** is a robust, state-aware automation system designed for the game *Rise of Kingdoms (RoK)*. Built with Python and leveraging pixel-based UI logic, it streamlines repetitive in-game tasks with high precision and human-like behavior. The system is modular, extensible, and engineered for reliability, making it ideal for both casual players and power users seeking efficiency and consistency.

---

## 🚀 Overview

ROK Macro Automation automates resource management and gathering in RoK by simulating intelligent user interactions. It avoids redundant actions, adapts to UI state changes, and maintains persistent state across sessions. The architecture is cleanly separated into logical modules, supporting easy maintenance and future feature expansion.

---

## 🧰 Tech Stack

| Component         | Description                                      |
|-------------------|--------------------------------------------------|
| Python 3          | Core automation logic and orchestration          |
| AutoHotkey v2     | (Planned/Optional) Low-level scripting support   |
| Tesseract OCR     | Smart text detection for in-game UI elements     |
| YOLO              | Object detection for robust UI state recognition |
| Win32 API         | Low-level Windows API calls for stealthy input   |
| PyAutoGUI         | Pixel-based UI interaction and automation        |
| OOP Architecture  | Modular classes for actions, UI, and elements    |
| Logging System    | Structured, timestamped logs for all actions     |

---

## ✨ Features

- **Resource Assistance:** Automates the transfer of food, wood, stone, and gold between accounts, intelligently avoiding redundant clicks and selections.
- **Smart Gathering:** Sends up to 5 marches for resource farming, with customizable resource order and adaptive UI state tracking.
- **Persistent State:** Remembers previous actions and UI states to minimize unnecessary operations.
- **Configurable Profiles:** Supports multiple user profiles and action modes (character, account, all accounts).
- **Robust Logging:** Action-level, debug, and error logs with tooltips and timestamps for easy troubleshooting.
- **Resolution & DPI Awareness:** Automatically detects and adapts to client resolution and DPI scaling.
- **Extensible Actions:** Easily register new actions or modify existing ones via the modular walker system.
- **Stealth Automation:** Utilizes low-level Win32 API calls to simulate input, reducing the risk of detection by the game’s anti-cheat systems.
---

## 🏗️ Project Structure

```
├── main.py                # Entry point, orchestrates automation flow
├── controller.py          # (Planned) High-level control logic
├── src/                   # Core modules
│   ├── action/            # Action classes (Gather, Collect, UseItems, etc.)
│   ├── element/           # UI element definitions and helpers
│   ├── logger.py          # Logging and tooltip utilities
│   ├── privilege.py       # Privilege escalation and checks
│   ├── rok_profile.py     # User profile and configuration management
│   ├── window.py          # Window and resolution handling
│   └── ...                # Additional utilities and modules
├── assests/               # Datasets, images, and model files
├── runs/                  # Output and logs from automation runs
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project metadata and build config
└── README.md              # Project documentation
```

---

## ⚙️ How It Works

1. **Initialization:** Elevates privileges, verifies client resolution, and loads user profile.
2. **Action Registration:** Instantiates and registers desired actions (e.g., gathering, using items, collecting resources).
3. **Execution:** Executes actions based on the selected mode (character, account, all accounts), using pixel-based detection and input simulation.
4. **Logging:** All actions and errors are logged with timestamps and tooltips for transparency and debugging.

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
   python3 controller.py
   ```
    Note: Ctrl+Q to stop the script

**Note:**
- The entire repository is developed and tested in a Windows environment.
- YOLO model training is performed in WSL (Windows Subsystem for Linux) and requires additional Python YOLO packages.
- For running automation, only Windows is supported.
---

## 📝 Planned Features

- Auto farm gem (Highest priority)
- Integrate into VM managed by OperatorD (Discord bot service - coming soon)
- Command via OperatorD in discord chat
---

## 📄 License

This project is licensed under the terms of the `LICENSE`.

---

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome! Please open an issue or submit a pull request.

---

## 📬 Contact

For questions or support, please open an issue on GitHub.

## TIP
Resize VM to 1920x1080x32
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "rok1" "setvideomodehint" 1920 1080 32

---

*ROK Macro Automation is an independent project and is not affiliated with or endorsed by Lilith Games or Rise of Kingdoms.*


