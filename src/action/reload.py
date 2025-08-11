from src.api import ldp
from src.ui import MenuMain


def reload_game():
    """Reload the game and wait for it to be ready."""
    ldp.reload_app()
    MenuMain.wait_for_ingame_ready()
