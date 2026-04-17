# ui.py
# Минималистичный UI с анимациями. Исправлен баг с перекрытием игры.

import math
import arcade
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, FONT_NAME,
    STATE_START, STATE_PLAYING, STATE_GAME_OVER
)

# 🎨 Палитра (берем из конфига для согласованности)
BG = COLORS["background"]
CARD = (40, 40, 55)
PRIMARY = (88, 166, 255)
TEXT = (230, 230, 230)
MUTED = (140, 140, 140)
DANGER = (255, 99, 99)


class Button:
    def __init__(self, text, x, y, w, h, callback):
        self.text = text
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.callback = callback
        self.hovered = False
        self.scale = 1.0
        self.text_obj = arcade.Text(
            text, x, y, TEXT, 18,
            anchor_x="center", anchor_y="center",
            font_name=FONT_NAME, bold=False
        )

    def is_inside(self, x, y):
        return (self.x - self.w / 2 <= x <= self.x + self.w / 2 and
                self.y - self.h / 2 <= y <= self.y + self.h / 2)

    def update(self, dt):
        """Плавная анимация масштабирования."""
        target_scale = 1.06 if self.hovered else 1.0
        self.scale += (target_scale - self.scale) * dt * 8.0

    def draw(self):
        w = self.w * self.scale
        h = self.h * self.scale

        color = PRIMARY if self.hovered else CARD
        arcade.draw_lbwh_rectangle_filled(
            self.x - w / 2, self.y - h / 2, w, h, color
        )

        if self.hovered:
            arcade.draw_lbwh_rectangle_outline(
                self.x - w / 2, self.y - h / 2, w, h,
                (255, 255, 255, 100), 2
            )
            arcade.draw_lbwh_rectangle_filled(
                self.x - w / 2 - 2, self.y - h / 2 - 2, w + 4, h + 4,
                (*PRIMARY, 30)
            )

        self.text_obj.position = (self.x, self.y)
        self.text_obj.draw()

    def click(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and self.is_inside(x, y):
            self.callback()
            return True
        return False


class UIManager:
    def __init__(self, state_callback):
        self.state_callback = state_callback
        self.score = 0
        self.high_score = 0
        self.difficulty = "Medium"
        
        self.pulse_time = 0.0
        
        self._create_texts()
        self._setup_buttons()

    def _create_texts(self):
        self.title_text = arcade.Text(
            "Snake", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 120,
            PRIMARY, 48, anchor_x="center", font_name=FONT_NAME
        )
        self.subtitle_text = arcade.Text(
            "Difficulty", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40,
            MUTED, 14, anchor_x="center", font_name=FONT_NAME
        )
        self.current_diff_text = arcade.Text(
            f"Current: {self.difficulty}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 130,
            MUTED, 14, anchor_x="center", font_name=FONT_NAME
        )
        self.go_title = arcade.Text(
            "Game Over", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100,
            DANGER, 40, anchor_x="center", font_name=FONT_NAME
        )
        self.go_score = arcade.Text(
            f"Score: {self.score}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40,
            TEXT, 20, anchor_x="center", font_name=FONT_NAME
        )
        self.go_best = arcade.Text(
            f"Best: {self.high_score}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 10,
            MUTED, 16, anchor_x="center", font_name=FONT_NAME
        )
        self.hud_score = arcade.Text(
            f"{self.score}", 20, SCREEN_HEIGHT - 40, TEXT, 18,
            font_name=FONT_NAME, anchor_x="left"
        )

    def _setup_buttons(self):
        self.start_buttons = [
            Button("Start Game", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 10, 220, 50,
                   lambda: self.state_callback(STATE_PLAYING)),
            Button("Easy", SCREEN_WIDTH / 2 - 120, SCREEN_HEIGHT / 2 - 80, 100, 40,
                   lambda: self._set_diff("Easy")),
            Button("Medium", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 80, 100, 40,
                   lambda: self._set_diff("Medium")),
            Button("Hard", SCREEN_WIDTH / 2 + 120, SCREEN_HEIGHT / 2 - 80, 100, 40,
                   lambda: self._set_diff("Hard")),
        ]
        self.game_over_buttons = [
            Button("Restart", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 60, 200, 50,
                   lambda: self.state_callback(STATE_PLAYING)),
            Button("Menu", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 130, 200, 50,
                   lambda: self.state_callback(STATE_START)),
        ]
        self.buttons = []

    def _set_diff(self, d):
        self.difficulty = d
        self.current_diff_text.value = f"Current: {d}"

    def update(self, dt):
        self.pulse_time += dt
        for btn in self.buttons:
            btn.update(dt)

    def update_hover(self, state, mx, my):
        if state == STATE_START:
            self.buttons = self.start_buttons
        elif state == STATE_GAME_OVER:
            self.buttons = self.game_over_buttons
        else:
            self.buttons = []

        for b in self.buttons:
            b.hovered = b.is_inside(mx, my)

    def draw(self, state):
        # 🔧 ИСПРАВЛЕНИЕ: Рисуем фон ТОЛЬКО в меню (Start / Game Over).
        # Во время игры (STATE_PLAYING) фон очищается через self.clear() в game.py,
        # и если мы нарисуем его здесь, он перекроет змейку.
        if state != STATE_PLAYING:
            arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, BG)

        if state == STATE_START:
            self._draw_start()
        elif state == STATE_GAME_OVER:
            self._draw_game_over()
        elif state == STATE_PLAYING:
            self._draw_hud()

        for b in self.buttons:
            b.draw()

    def _draw_start(self):
        pulse_size = int(48 + 3 * math.sin(self.pulse_time * 2.5))
        self.title_text.font_size = pulse_size
        self.title_text.draw()
        
        dot_y = SCREEN_HEIGHT / 2 + 85
        for i in range(3):
            alpha = int(150 + 100 * math.sin(self.pulse_time * 3 + i * 2))
            arcade.draw_circle_filled(
                SCREEN_WIDTH / 2 - 8 + i * 8, dot_y,
                2, (*PRIMARY, alpha)
            )
        
        self.subtitle_text.draw()
        self.current_diff_text.draw()

    def _draw_game_over(self):
        pulse_size = int(40 + 2 * math.sin(self.pulse_time * 3))
        self.go_title.font_size = pulse_size
        self.go_title.draw()
        
        self.go_score.value = f"Score: {self.score}"
        self.go_score.draw()
        self.go_best.value = f"Best: {self.high_score}"
        self.go_best.draw()

    def _draw_hud(self):
        self.hud_score.value = f"{self.score}"
        self.hud_score.draw()

    def on_mouse_press(self, x, y, button, modifiers, state):
        if state == STATE_PLAYING:
            return False
        for b in self.buttons:
            if b.click(x, y, button, modifiers):
                return True
        return False