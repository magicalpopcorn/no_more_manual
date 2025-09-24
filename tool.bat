@echo off
start "" cmd /c "python3 -m uvicorn service:app --host 127.0.0.1 --port 8000"
python3 pyqt_ui.py
