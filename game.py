# game.py
# Главный класс окна. Управляет состояниями, игровым циклом, вводом и связывает все модули.
# Полная совместимость с Arcade 3.3.3

import os
import json
import arcade
from config import *
from snake import Snake
from food import Food
from ui import UIManager


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=False)
        arcade.set_background_color(COLORS["background"])

        # Инициализация компонентов
        self.ui = UIManager(self._change_state)
        self.snake = Snake(GRID_COLS // 2, GRID_ROWS // 2)
        self.food = Food()

        # Состояние и переменные игры
        self.current_state = STATE_START
        self.score = 0
        self.high_score = self._load_high_score()
        self.difficulty = "Medium"
        self.move_timer = 0.0
        self.move_interval = DIFFICULTY["Medium"]["base_speed"]
        self.acceleration = DIFFICULTY["Medium"]["acceleration"]

        # Отслеживание мыши для UI
        self.mouse_x = SCREEN_WIDTH // 2
        self.mouse_y = SCREEN_HEIGHT // 2

        # Загрузка звуков (безопасная)
        self.sounds = self._load_sounds()

    def _load_sounds(self) -> dict:
        """Пытается загрузить звуки. Если файлов нет, возвращает пустой dict."""
        sounds = {}
        for name, path in SOUND_PATHS.items():
            full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
            if os.path.exists(full_path):
                try:
                    sounds[name] = arcade.load_sound(full_path)
                except Exception:
                    pass
        return sounds

    def _play_sound(self, name: str):
        """Воспроизводит звук, если он был загружен."""
        if name in self.sounds:
            arcade.play_sound(self.sounds[name])

    def _load_high_score(self) -> int:
        """Загружает лучший счёт из файла."""
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "high_score.json")
        try:
            with open(path, "r") as f:
                return int(json.load(f).get("high_score", 0))
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            return 0

    def _save_high_score(self):
        """Сохраняет лучший счёт."""
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "high_score.json")
        try:
            with open(path, "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except Exception:
            pass

    def _change_state(self, new_state: str):
        """Переключает состояние игры по запросу UI."""
        self.current_state = new_state
        self._play_sound("click")

        if new_state == STATE_PLAYING:
            self._start_game()
        elif new_state == STATE_START:
            self.difficulty = self.ui.difficulty

    def _start_game(self):
        """Сбрасывает игровые переменные и запускает новую сессию."""
        self.score = 0
        self.ui.score = 0
        self.ui.high_score = self.high_score
        self.difficulty = self.ui.difficulty

        diff = DIFFICULTY[self.difficulty]
        self.move_interval = diff["base_speed"]
        self.acceleration = diff["acceleration"]

        self.snake.reset(GRID_COLS // 2, GRID_ROWS // 2)
        self.food.spawn(GRID_COLS, GRID_ROWS, self.snake.segments)
        self.move_timer = 0.0

    def _game_over(self):
        """Завершает игру, обновляет рекорд и меняет состояние."""
        self._play_sound("game_over")
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()
        self.ui.high_score = self.high_score
        self.current_state = STATE_GAME_OVER

    def _update_speed(self):
        """Увеличивает скорость движения в зависимости от счёта."""
        base = DIFFICULTY[self.difficulty]["base_speed"]
        new_interval = base - self.acceleration * (self.score // 10)
        self.move_interval = max(0.04, new_interval)

    def _check_collisions(self):
        """Проверяет столкновения после каждого логического шага змейки."""
        head_col, head_row = self.snake.get_head_pos()

        # Столкновение со стенами
        if head_col < 0 or head_col >= GRID_COLS or head_row < 0 or head_row >= GRID_ROWS:
            self._game_over()
            return

        # Столкновение с собой
        if self.snake.check_self_collision():
            self._game_over()
            return

        # Столкновение с едой
        if head_col == self.food.col and head_row == self.food.row:
            self.snake.grow()
            self.score += 10
            self.ui.score = self.score
            self._update_speed()
            self._play_sound("eat")
            self.food.spawn(GRID_COLS, GRID_ROWS, self.snake.segments)

    def on_update(self, delta_time: float):
        """Игровой цикл. Вызывается каждый кадр."""
        self.ui.update_hover(self.current_state, self.mouse_x, self.mouse_y)
        self.ui.update(delta_time)

        if self.current_state != STATE_PLAYING:
            return

        self.move_timer += delta_time
        if self.move_timer >= self.move_interval:
            self.snake.move()
            self.move_timer = 0.0
            self._check_collisions()

        self.snake.update(delta_time)
        self.food.update(delta_time)

    def on_draw(self):
        """Отрисовка всего содержимого окна. Arcade 3.x API."""
        # ✅ В Arcade 3.x используем clear() вместо start_render()
        self.clear()

        if self.current_state == STATE_PLAYING:
            self._draw_grid()
            self.food.draw()
            self.snake.draw()
            self.ui.draw(self.current_state)
        else:
            self.ui.draw(self.current_state)

        # ✅ finish_render() в Arcade 3.x не нужен для оконных приложений

    def _draw_grid(self):
        """Рисует тонкую сетку для визуальной привязки."""
        for x in range(0, SCREEN_WIDTH + 1, TILE_SIZE):
            arcade.draw_line(x, 0, x, SCREEN_HEIGHT, COLORS["grid_line"])
        for y in range(0, SCREEN_HEIGHT + 1, TILE_SIZE):
            arcade.draw_line(0, y, SCREEN_WIDTH, y, COLORS["grid_line"])

    def on_key_press(self, symbol: int, modifiers: int):
        """Обработка нажатий клавиш."""
        if self.current_state == STATE_PLAYING:
            if symbol == arcade.key.UP or symbol == arcade.key.W:
                self.snake.change_direction((0, 1))
            elif symbol == arcade.key.DOWN or symbol == arcade.key.S:
                self.snake.change_direction((0, -1))
            elif symbol == arcade.key.LEFT or symbol == arcade.key.A:
                self.snake.change_direction((-1, 0))
            elif symbol == arcade.key.RIGHT or symbol == arcade.key.D:
                self.snake.change_direction((1, 0))
            elif symbol == arcade.key.ESCAPE:
                self._change_state(STATE_START)
        elif symbol == arcade.key.ENTER and self.current_state in (STATE_START, STATE_GAME_OVER):
            self._change_state(STATE_PLAYING)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """Отслеживает курсор для подсветки кнопок."""
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Делегирует клик мышью в UI."""
        self.ui.on_mouse_press(x, y, button, modifiers, self.current_state)