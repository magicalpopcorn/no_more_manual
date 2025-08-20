# Macro Automation Framework

---

## 🚀 Overview

**Macro Automation Framework** is a robust, state-aware automation system designed for mobile applications. 
Built with Python and leveraging computer vision, it streamlines repetitive tasks with high precision and 
human-like behavior. The system is modular, extensible, and engineered for reliability, making it ideal for 
users seeking efficiency and consistency in managing multi-step workflows.

- **State-Aware Automation:** Tracks previous actions and UI states to minimize unnecessary operations.  
- **Persistent Logging:** Action-level, debug, and error logs with timestamps for easy troubleshooting.  
- **Android Emulator Integration:** Works with LDPlayer instances via ADB & LDConsole for reliable automation.  
- **Extensible Task System:** Easily register new tasks or modify existing ones via the modular agent system.  

---

## ✨ Features

- **Resource Management:** Automates the transfer and collection of resources, intelligently avoiding redundant clicks and selections.  
- **Smart Task Execution:** Executes repetitive workflows (e.g., farming, item usage, collection) with adaptive UI state tracking and fallback mechanisms.  
- **Multi-Profile Support:** Handles multiple user profiles and action modes, enabling automation across accounts.  

---

## 🧰 Tech Stack

| Component         | Description                                      |
|-------------------|--------------------------------------------------|
| Python3           | Core automation logic and orchestration          |
| ADB               | Communication with Android emulator instances    |
| LDPlayer API      | Android emulator management and control          |
| Tesseract OCR     | Smart text detection for mobile UI elements      |
| YOLO (Ultralytics)| Object detection for robust UI state recognition |
| OpenCV            | Computer vision and image processing             |
| OOP Architecture  | Modular classes for tasks, agents, and UI elements |
| Logging System    | Structured, timestamped logs for all actions     |

---

## 📝 Current Features & Roadmap

### ✅ Implemented  
- **Multi-Profile Resource Automation** across multiple accounts  
- **Smart Item Usage** and resource collection  
- **Profile Management** via YAML configs  
- **Computer Vision:** YOLO-based UI element detection + OCR text recognition  
- **Android Emulator Integration** (ADB + LDPlayer)  

### 🚧 In Development  
- **Enhanced Resource Collection** modules  
- **Remote Control APIs** (Flask server, REST API)  
- **Discord Integration** for remote monitoring and commands  
- **Advanced Scheduling** for automation tasks  
- **Web Dashboard** for visualization and control  

---

## 💡 Development Notes

- YOLO model training performed in WSL (Windows Subsystem for Linux).  
- Custom models trained for **mobile UI elements**.  
- Modular OOP architecture ensures maintainability and scalability.  

---
