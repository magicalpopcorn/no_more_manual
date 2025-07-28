"""
driver package

Low-level input control module for Rise of Kingdoms macros.

This package provides direct access to mouse and keyboard input through Windows APIs
such as SendInput, mouse_event, and ClientToScreen. It is purpose-built to safely simulate
human-like input for interacting with the game Rise of Kingdoms (RoK), which aggressively
filters or blocks synthetic input from high-level Python libraries.

Why not use pyautogui or pynput?
--------------------------------
While libraries like `pyautogui`, `pynput`, and `keyboard` are convenient, they generate
synthetic user input at a high abstraction level (user-mode hooks). These methods are
easily flagged by modern anti-cheat systems or game input filters — especially in games
like RoK that run inside emulators or protected environments.

By using WinAPI directly (via `ctypes` or `pywin32`), this package:
- Emulates native input events more reliably
- Matches the behavior of trusted tools like AutoHotkey (AHK)
- Avoids detection vectors tied to common automation libraries
- Offers finer control over timing, motion, and click patterns

Modules included:
- `mouse.py`     — Movement, click, and hold operations using WinAPI
- `keyboard.py`  — Secure keyboard input via AHK script delegation
- `ctypes_def.py` — Struct definitions for INPUT and MOUSEINPUT (SendInput compatible)

This layer is considered the "hands" of the macro system — reliable, low-level, and undetectable when used correctly.
"""
