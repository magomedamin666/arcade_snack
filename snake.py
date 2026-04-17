# snake.py
# Логика и отрисовка змейки. Разделена на сеточные шаги (логика) и плавную анимацию (визуал).
# Совместим с Arcade 3.3.3

import math
import arcade
from config import TILE_SIZE, COLORS


class SnakeSegment:
    """Один сегмент тела змейки. Хранит сеточную позицию и текущие пиксельные координаты."""
    
    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.x = col * TILE_SIZE + TILE_SIZE / 2
        self.y = row * TILE_SIZE + TILE_SIZE / 2
        self.target_x = self.x
        self.target_y = self.y

    def update_smooth(self, dt):
        """Плавно приближает текущие координаты к целевым каждый кадр."""
        interpolation_speed = 12.0
        alpha = 1.0 - math.exp(-interpolation_speed * dt)
        self.x += (self.target_x - self.x) * alpha
        self.y += (self.target_y - self.y) * alpha

    def set_target(self, col, row):
        """Задаёт новую сеточную позицию и пересчитывает пиксельную цель."""
        self.col = col
        self.row = row
        self.target_x = col * TILE_SIZE + TILE_SIZE / 2
        self.target_y = row * TILE_SIZE + TILE_SIZE / 2


class Snake:
    """Класс змейки: управление, рост, отрисовка, проверка столкновений."""

    def __init__(self, start_col, start_row, length=3):
        self.segments = []
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.grow_pending = False
        self.reset(start_col, start_row, length)

    def reset(self, start_col, start_row, length=3):
        """Сбрасывает змейку в начальное состояние. length — опционален (по умолчанию 3)."""
        self.segments.clear()
        for i in range(length):
            seg = SnakeSegment(start_col - i, start_row)
            self.segments.append(seg)
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.grow_pending = False

    def change_direction(self, new_dir):
        """Обрабатывает нажатие клавиш. Запрещает разворот на 180°."""
        if (new_dir[0] * -1, new_dir[1] * -1) == self.direction:
            return
        self.next_direction = new_dir

    def move(self):
        """Выполняет один логический шаг по сетке."""
        self.direction = self.next_direction

        for i in range(len(self.segments) - 1, 0, -1):
            prev = self.segments[i - 1]
            self.segments[i].set_target(prev.col, prev.row)

        head = self.segments[0]
        head.set_target(head.col + self.direction[0], head.row + self.direction[1])

        if self.grow_pending:
            tail = self.segments[-1]
            new_seg = SnakeSegment(tail.col, tail.row)
            new_seg.x = tail.x
            new_seg.y = tail.y
            self.segments.append(new_seg)
            self.grow_pending = False

    def update(self, dt):
        """Обновляет плавные координаты всех сегментов. Вызывается каждый кадр."""
        for seg in self.segments:
            seg.update_smooth(dt)

    def grow(self):
        """Откладывает рост до следующего логического шага."""
        self.grow_pending = True

    def check_self_collision(self):
        """Проверяет, не врезалась ли голова в тело."""
        head = self.segments[0]
        for i in range(1, len(self.segments)):
            if self.segments[i].col == head.col and self.segments[i].row == head.row:
                return True
        return False

    def get_head_pos(self):
        """Возвращает текущие сеточные координаты головы (col, row)."""
        return self.segments[0].col, self.segments[0].row

    def draw(self):
        """Отрисовывает змейку с градиентом и округлыми сегментами. Arcade 3.3.3 API."""
        total = len(self.segments)
        for i, seg in enumerate(reversed(self.segments)):
            ratio = i / max(total - 1, 1)
            r = int(COLORS["snake_body_start"][0] * (1 - ratio) + COLORS["snake_body_end"][0] * ratio)
            g = int(COLORS["snake_body_start"][1] * (1 - ratio) + COLORS["snake_body_end"][1] * ratio)
            b = int(COLORS["snake_body_start"][2] * (1 - ratio) + COLORS["snake_body_end"][2] * ratio)
            color = (r, g, b)

            # Arcade 3.3.3: draw_circle_filled(center_x, center_y, radius, color)
            arcade.draw_circle_filled(seg.x, seg.y, TILE_SIZE // 2 - 2, color)

        # Голова — ярче и чуть крупнее
        head = self.segments[0]
        arcade.draw_circle_filled(head.x, head.y, TILE_SIZE // 2, COLORS["snake_head"])