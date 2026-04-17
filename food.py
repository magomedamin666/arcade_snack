# food.py
# Логика и отрисовка еды. Включает безопасный спавн и анимацию пульсации.

import math
import random
import arcade
from config import TILE_SIZE, COLORS


class Food:
    """Класс еды: спавн, анимация появления, пульсация, отрисовка."""

    def __init__(self):
        self.col = 0
        self.row = 0
        self.x = 0.0
        self.y = 0.0
        self.scale = 0.0          # Для анимации появления (0 -> 1)
        self.pulse_time = 0.0     # Время для синусоидальной пульсации
        self.active = False       # Флаг: есть ли еда на поле

    def spawn(self, grid_cols, grid_rows, snake_segments):
        """Находит случайную свободную клетку и активирует еду."""
        max_attempts = grid_cols * grid_rows
        for _ in range(max_attempts):
            self.col = random.randint(0, grid_cols - 1)
            self.row = random.randint(0, grid_rows - 1)
            # Проверяем, не занята ли клетка змейкой
            if not any(seg.col == self.col and seg.row == self.row for seg in snake_segments):
                break
        
        # Центрируем в тайле
        self.x = float(self.col * TILE_SIZE + TILE_SIZE / 2)
        self.y = float(self.row * TILE_SIZE + TILE_SIZE / 2)
        self.active = True
        self.scale = 0.0          # Начинаем с нуля для эффекта "вырастания"
        self.pulse_time = 0.0

    def update(self, dt):
        """Обновляет анимации. Вызывается каждый кадр."""
        if not self.active:
            return

        # Плавное появление (экспоненциальное сглаживание)
        if self.scale < 1.0:
            self.scale = min(1.0, self.scale + dt * 6.0)

        # Накопление времени для пульсации
        self.pulse_time += dt

    def draw(self):
        """Отрисовывает еду с эффектом свечения и пульсации."""
        if not self.active:
            return

        # Пульсация: синусоида от 0.85 до 1.15
        pulse = 1.0 + 0.15 * math.sin(self.pulse_time * 4.0)
        base_radius = (TILE_SIZE / 2 - 2) * self.scale
        current_radius = base_radius * pulse

        # Полупрозрачное свечение (больше радиус, меньше плотность)
        arcade.draw_circle_filled(self.x, self.y, current_radius * 1.8, COLORS["food_glow"])
        # Основная часть
        arcade.draw_circle_filled(self.x, self.y, current_radius, COLORS["food"])