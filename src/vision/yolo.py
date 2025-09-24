from ultralytics import YOLO

from src import const

YOLO_MODEL = YOLO(const.PROJECT_ROOT / "assets" / "yolo_models" / "2000_37_plus.pt")


class YoloClass:
    GEM = "gem-z-out"
    MARCH_IDLE = "march_idle"
    MARCH_MARCHING = "march_marching"
    MARCH_RETURNING = "march_returning"
    MARCH_FARMING = "march_farming"
    MARCH_ATTACKING = "march_attacking"
