# config.py
# Глобальные константы и настройки. Изменяй их здесь, чтобы настроить игру под себя.

# --- Настройки окна ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Snake: Modern Edition"
FPS = 60

# --- Сетка и тайлы ---
TILE_SIZE = 20
GRID_COLS = SCREEN_WIDTH // TILE_SIZE
GRID_ROWS = SCREEN_HEIGHT // TILE_SIZE

# --- Цветовая палитра (RGB / RGBA) ---
# Используем тёмную тему с яркими акцентами для современного вида
COLORS = {
    "background": (26, 26, 46),          # Глубокий тёмно-синий фон
    "grid_line": (35, 40, 60),           # Едва заметные линии сетки
    "snake_head": (0, 255, 136),         # Яркий неоновый мятный
    "snake_body_start": (0, 204, 106),   # Градиент тела (начало)
    "snake_body_end": (0, 136, 68),      # Градиент тела (конец)
    "food": (255, 107, 107),             # Коралловая еда
    "food_glow": (255, 107, 107, 80),    # Полупрозрачное свечение еды
    "text": (224, 224, 224),             # Светло-серый текст
    "button_bg": (74, 144, 226),         # Основной цвет кнопок
    "button_hover": (100, 170, 240),     # Цвет кнопок при наведении
    "panel_bg": (20, 20, 35, 210),       # Фон UI-панелей (полупрозрачный)
}

# --- Уровни сложности ---
# base_speed: время в секундах между ходами змейки (меньше = быстрее)
# acceleration: насколько уменьшается время каждого хода при росте змейки
DIFFICULTY = {
    "Easy":   {"base_speed": 0.15, "acceleration": 0.002},
    "Medium": {"base_speed": 0.10, "acceleration": 0.003},
    "Hard":   {"base_speed": 0.06, "acceleration": 0.004},
}

# --- Состояния игры ---
STATE_START = "START"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"

# --- Пути к звукам ---
# Оставь папку sounds/ пустой. Код будет безопасно пропускать звуки, если файлов нет.
SOUND_PATHS = {
    "eat": "sounds/eat.wav",
    "game_over": "sounds/game_over.wav",
    "click": "sounds/click.wav",
}

# --- Шрифт ---
# Arcade использует системные шрифты. "Arial" есть на большинстве ОС.
FONT_NAME = "Arial"
FONT_SIZE_TITLE = 48
FONT_SIZE_TEXT = 24
FONT_SIZE_BUTTON = 20