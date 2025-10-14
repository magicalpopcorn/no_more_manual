import subprocess

import requests
from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


# Worker thread for log polling
class LogWorker(QThread):
    new_log = pyqtSignal(str)

    def __init__(self, log_file):
        super().__init__()
        self.log_file = log_file
        self._running = True

    def run(self):
        last_size = 0
        while self._running:
            try:
                with open(self.log_file, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(last_size)
                    new_data = f.read()
                    if new_data:
                        self.new_log.emit(new_data)  # emit signal instead of touching UI
                    last_size = f.tell()
            except FileNotFoundError:
                pass
            self.msleep(1000)  # non-blocking sleep

    def stop(self):
        self._running = False


class RegularTask(QWidget):
    def __init__(self, backend_url):
        super().__init__()

        self.task_id = None
        self.backend_url = backend_url
        regular_task_layout = QVBoxLayout()

        # Call setup methods
        self._setup_server_info(regular_task_layout)
        self._setup_player_instance(regular_task_layout)
        self._setup_mode(regular_task_layout)
        self._setup_tasks(regular_task_layout)
        self._setup_post_actions(regular_task_layout)
        self._setup_buttons(regular_task_layout)
        self._setup_output_box(regular_task_layout)

        self.setLayout(regular_task_layout)

        # Timer for health check
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.healthcheck_once)
        self.timer.start(15000)  # every 15s
        self.healthcheck_once()  # initial check

        self.worker = None  # placeholder for log worker

    def _setup_server_info(self, layout: QVBoxLayout):
        server_layout = QHBoxLayout()
        server_layout.setContentsMargins(0, 0, 0, 0)
        server_layout.setSpacing(4)  # tighten the gap

        self.status_icon = QLabel()
        self.status_icon.setPixmap(self.create_circle_pixmap(QColor("red")))  # default red
        self.url_label = QLabel(f"Server:  {self.backend_url}")

        server_layout.addWidget(self.status_icon)
        server_layout.addWidget(self.url_label)
        server_layout.addStretch(1)
        layout.addLayout(server_layout)

    def _setup_player_instance(self, layout: QVBoxLayout):
        ldplayer_group = QGroupBox("LDPlayer Instance")
        ldplayer_layout = QHBoxLayout()

        self.instance_dropdown = QComboBox()
        self.instance_dropdown.setFixedWidth(200)
        for instance in self.get_ldplayer_instances():
            self.instance_dropdown.addItem(instance)

        ldplayer_layout.addWidget(self.instance_dropdown)
        ldplayer_layout.addStretch(1)
        ldplayer_group.setLayout(ldplayer_layout)
        layout.addWidget(ldplayer_group)

    def _setup_mode(self, layout: QVBoxLayout):
        mode_group = QGroupBox("Mode")
        mode_layout = QHBoxLayout()
        self.mode_char = QRadioButton("Only char")
        self.mode_account = QRadioButton("Only account")
        self.mode_all = QRadioButton("All accounts")
        self.mode_all.setChecked(True)  # default

        mode_layout.addWidget(self.mode_char)
        mode_layout.addWidget(self.mode_account)
        mode_layout.addWidget(self.mode_all)
        mode_layout.addStretch(1)  # push to left, nice spacing
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

    def _setup_tasks(self, layout: QVBoxLayout):
        task_group = QGroupBox("Tasks")
        task_layout = QVBoxLayout()

        self.task1 = QCheckBox("Farm")
        self.task2 = QCheckBox("Use 24h boost gathering")
        self.task3 = QCheckBox("Claim alliance resources")
        self.task4 = QCheckBox("Buy items")
        self.task5 = QCheckBox("Collect info")

        for task in [self.task1, self.task2, self.task3, self.task4, self.task5]:
            task.setChecked(True)  # default all checked
            task_layout.addWidget(task)

        task_group.setLayout(task_layout)
        layout.addWidget(task_group)

    def _setup_output_box(self, layout: QVBoxLayout):
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        layout.addWidget(self.output_box)

    def _setup_buttons(self, layout: QVBoxLayout):
        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("Run Tasks")
        self.run_btn.clicked.connect(self.run_task)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_task)

        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)

    def _setup_post_actions(self, layout: QVBoxLayout):
        post_group = QGroupBox("After Task")
        post_layout = QHBoxLayout()

        self.action_none = QRadioButton("None")
        self.action_none.setChecked(True)  # default
        self.action_sleep = QRadioButton("Sleep")
        self.action_shutdown = QRadioButton("Shutdown")

        post_layout.addWidget(self.action_none)
        post_layout.addWidget(self.action_sleep)
        post_layout.addWidget(self.action_shutdown)

        post_group.setLayout(post_layout)
        layout.addWidget(post_group)

    def append_log(self, text: str):
        self.output_box.setReadOnly(False)
        self.output_box.insertPlainText(text)
        self.output_box.verticalScrollBar().setValue(self.output_box.verticalScrollBar().maximum())
        self.output_box.setReadOnly(True)

    def get_tasks(self):
        selected = []
        if self.task1.isChecked():
            selected.append("farm_rss")
        if self.task2.isChecked():
            selected.append("24h_boost")
        if self.task3.isChecked():
            selected.append("claim_alliance_resources")
        if self.task4.isChecked():
            selected.append("purchase_items")
        if self.task5.isChecked():
            selected.append("collect_info")
        return selected

    def get_mode(self):
        if self.mode_char.isChecked():
            return 1
        elif self.mode_account.isChecked():
            return 2
        else:
            return 3

    def run_task(self):
        tasks = self.get_tasks()

        if not tasks:
            self.append_log("No task selected\n")
            return

        mode = self.get_mode()
        instance = self.instance_dropdown.currentText()

        # send request to backend
        try:
            resp = requests.post(
                f"{self.backend_url}/run_task",
                json={"tasks": tasks, "mode": mode, "instance_name": instance},
                timeout=10,
            )
        except requests.exceptions.RequestException as e:
            self.append_log(f"Request failed: {e}\n")
            return

        if resp.status_code != 200:
            self.append_log(f"Backend error: {resp.status_code}\nMessage: {resp.text}\n")
            return
        else:
            data = resp.json()
            log_file = data["log_file"]
            self.task_id = data["task_id"]

            # Clear old logs
            self.output_box.setReadOnly(False)
            self.output_box.clear()
            self.output_box.setReadOnly(True)

            self.append_log(f"Started tasks: {', '.join(tasks)} with mode={mode}\n")

            self.run_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)

            # start worker
            if self.worker:
                self.worker.stop()
                self.worker.wait()

            self.worker = LogWorker(log_file)
            self.worker.new_log.connect(self.append_log)  # signal -> slot
            self.worker.start()

    def stop_task(self):
        if self.task_id:
            try:
                # Tell backend to stop this task
                resp = requests.post(
                    f"{self.backend_url}/stop_task",
                    params={"task_id": self.task_id},
                    timeout=5,
                )
                if resp.status_code == 200:
                    self.append_log(f"Stop request sent for task_id={self.task_id}\n")
                else:
                    self.append_log(
                        f"Backend stop error: {resp.status_code}\nMessage: {resp.text}\n"
                    )
            except requests.exceptions.RequestException as e:
                self.append_log(f"Stop request failed: {e}\n")
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            self.worker = None
        self.append_log("Stopped log polling.\n")
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def healthcheck_once(self):
        """Ping /health every 5s and update status icon."""
        try:
            r = requests.get(f"{self.backend_url}/api/v1/healthcheck", timeout=2)
            if r.status_code == 200:
                self.status_icon.setPixmap(self.create_circle_pixmap(QColor("green")))
            else:
                self.status_icon.setPixmap(self.create_circle_pixmap(QColor("red")))
        except requests.exceptions.RequestException:
            self.status_icon.setPixmap(self.create_circle_pixmap(QColor("red")))

    def get_ldplayer_instances(self):
        try:
            result = subprocess.check_output(["ldconsole.exe", "list"], text=True, encoding="utf-8")
            instances = [line.strip() for line in result.splitlines() if line.strip()]
            return instances
        except Exception as e:
            return [f"Error: {e}"]

    @staticmethod
    def create_circle_pixmap(color: QColor, size: int = 16):
        """Helper to create a colored circle QPixmap."""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size, size)
        painter.end()
        return pixmap
