# game.py
# Главный игровой цикл.

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

        # Компоненты
        self.ui = UIManager(self._change_state)
        self.snake = Snake(GRID_COLS // 2, GRID_ROWS // 2)
        self.food = Food()

        # Переменные игры
        self.current_state = STATE_START
        self.score = 0
        self.high_score = self._load_high_score()
        self.difficulty = "Medium"
        self.move_timer = 0.0
        self.move_interval = DIFFICULTY["Medium"]["base_speed"]
        self.acceleration = DIFFICULTY["Medium"]["acceleration"]
        self.mouse_x = SCREEN_WIDTH // 2
        self.mouse_y = SCREEN_HEIGHT // 2

        # Загрузка звуков
        self.sounds = self._load_sounds()

    def _load_sounds(self):
        """Безопасная загрузка звуков."""
        sounds = {}
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for name, path in SOUND_PATHS.items():
            full_path = os.path.join(base_dir, path)
            if os.path.exists(full_path):
                try:
                    sounds[name] = arcade.load_sound(full_path)
                    print(f"✅ Звук загружен: {name}")
                except Exception as e:
                    print(f"❌ Ошибка загрузки {name}: {e}")
        return sounds

    def _play_sound(self, name):
        """Воспроизводит звук с проверкой и громкостью."""
        if name in self.sounds:
            arcade.play_sound(self.sounds[name], volume=SOUND_VOLUME)

    def _load_high_score(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "high_score.json")
        try:
            with open(path, "r") as f:
                return int(json.load(f).get("high_score", 0))
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def _save_high_score(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "high_score.json")
        with open(path, "w") as f:
            json.dump({"high_score": self.high_score}, f)

    def _change_state(self, new_state):
        self.current_state = new_state
        self._play_sound("click")
        
        if new_state == STATE_PLAYING:
            self._start_game()
        elif new_state == STATE_START:
            self.difficulty = self.ui.difficulty

    def _start_game(self):
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
        self._play_sound("die")
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()
        self.ui.high_score = self.high_score
        self.current_state = STATE_GAME_OVER

    def _update_speed(self):
        base = DIFFICULTY[self.difficulty]["base_speed"]
        new_interval = base - self.acceleration * (self.score // 10)
        self.move_interval = max(0.04, new_interval)

    def _check_collisions(self):
        head_col, head_row = self.snake.get_head_pos()

        if head_col < 0 or head_col >= GRID_COLS or head_row < 0 or head_row >= GRID_ROWS:
            self._game_over()
            return

        if self.snake.check_self_collision():
            self._game_over()
            return

        if head_col == self.food.col and head_row == self.food.row:
            self.snake.grow()
            self.score += 10
            self.ui.score = self.score
            self._update_speed()
            self._play_sound("eat") # 🔊 ЗВУК ЕДЫ
            self.food.spawn(GRID_COLS, GRID_ROWS, self.snake.segments)

    def on_update(self, delta_time):
        self.ui.update(delta_time)
        self.ui.update_hover(self.current_state, self.mouse_x, self.mouse_y)

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
        self.clear()
        
        if self.current_state == STATE_PLAYING:
            self._draw_grid()
            self.food.draw()
            self.snake.draw()
            self.ui.draw(self.current_state)
        else:
            self.ui.draw(self.current_state)

    def _draw_grid(self):
        for x in range(0, SCREEN_WIDTH + 1, TILE_SIZE):
            arcade.draw_line(x, 0, x, SCREEN_HEIGHT, (35, 40, 60))
        for y in range(0, SCREEN_HEIGHT + 1, TILE_SIZE):
            arcade.draw_line(0, y, SCREEN_WIDTH, y, (35, 40, 60))

    def on_key_press(self, symbol, modifiers):
        if self.current_state == STATE_PLAYING:
            if symbol in (arcade.key.UP, arcade.key.W):
                self.snake.change_direction((0, 1))
            elif symbol in (arcade.key.DOWN, arcade.key.S):
                self.snake.change_direction((0, -1))
            elif symbol in (arcade.key.LEFT, arcade.key.A):
                self.snake.change_direction((-1, 0))
            elif symbol in (arcade.key.RIGHT, arcade.key.D):
                self.snake.change_direction((1, 0))
            elif symbol == arcade.key.ESCAPE:
                self._change_state(STATE_START)
        elif symbol == arcade.key.ENTER and self.current_state in (STATE_START, STATE_GAME_OVER):
            self._change_state(STATE_PLAYING)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        if self.ui.on_mouse_press(x, y, button, modifiers, self.current_state):
            self._play_sound("click") # 🔊 ЗВУК КЛИКА (дублируем для надежности)