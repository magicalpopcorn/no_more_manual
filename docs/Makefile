
YOLO_MODEL_DIR = assests/yolo_model
IMAGE_DIR = tmp/archive/screenshot

train:
	yolo task=detect mode=train \
		model=$(YOLO_MODEL_DIR)/2000_17.pt \
		data=assests/dataset/ds_25/data.yaml \
		epochs=10 imgsz=640

test:
	yolo task=detect mode=predict model=$(YOLO_MODEL_DIR)/2000_25.pt source=$(IMAGE_DIR)/gem1.png conf=0.2 save=True


screenshot:
	adb exec-out screencap -p > tmp/ldp/screen.png

pylint:
	python3 -m pylint --disable=all --enable=E,W src

build:
	python3 -m PyInstaller --noconfirm --onefile --windowed --icon=assets/ico/seondeok.ico --add-data "tools;tools" pyqt_ui.py