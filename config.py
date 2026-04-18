# config.py
# Глобальные константы и настройки

# --- Настройки окна ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Snake: Modern Edition"
FPS = 60

# --- Сетка ---
TILE_SIZE = 20
GRID_COLS = SCREEN_WIDTH // TILE_SIZE
GRID_ROWS = SCREEN_HEIGHT // TILE_SIZE

# --- Звуки ---
SOUND_VOLUME = 0.5 # Громкость от 0.0 до 1.0
SOUND_PATHS = {
    "eat": "sounds/eat.wav",
    "die": "sounds/die.wav",
    "click": "sounds/click.wav",
}

# --- Цвета ---
COLORS = {
    "background": (18, 18, 28),
    "snake_head": (0, 255, 136),
    "snake_body_start": (0, 204, 106),
    "snake_body_end": (0, 136, 68),
    "food": (255, 107, 107),
    "food_glow": (255, 107, 107, 80),
    "text": (224, 224, 224),
}

# --- Сложность ---
DIFFICULTY = {
    "Easy":   {"base_speed": 0.15, "acceleration": 0.002},
    "Medium": {"base_speed": 0.10, "acceleration": 0.003},
    "Hard":   {"base_speed": 0.06, "acceleration": 0.004},
}

# --- Состояния ---
STATE_START = "START"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"

# --- Шрифт ---
FONT_NAME = "Arial"
FONT_SIZE_TITLE = 48
FONT_SIZE_TEXT = 24
FONT_SIZE_BUTTON = 20