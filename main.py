# main.py
# Точка входа в игру. Инициализирует окно и запускает игровой цикл Arcade.

import arcade
from game import GameWindow


def main():
    """Создаёт главное окно и запускает цикл обновления/отрисовки."""
    window = GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()