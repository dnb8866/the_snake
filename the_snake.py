import pygame as pg

from abc import abstractmethod
from random import choice

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (189, 188, 183)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (0, 255, 0)
POISON_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 0, 255)

speed = 10

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pg.time.Clock()


class GameObject:
    """Base class for game objects."""

    def __init__(self, body_color: tuple = None) -> None:
        self.position = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.body_color = body_color

    def draw_cell(self, position: tuple, body_color: tuple = None) -> None:
        """Draw the cell on the screen."""
        body_color = body_color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, body_color, rect)
        if body_color != BOARD_BACKGROUND_COLOR:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    @abstractmethod
    def draw(self) -> None:
        """Draw the object on the screen."""


class Apple(GameObject):
    """Class representing an apple on the game board."""

    def __init__(self, *used_cells, body_color: tuple = APPLE_COLOR) -> None:
        super().__init__(body_color=body_color)
        self.used_cells = set(used_cells)
        self.randomize_position(*used_cells)

    def randomize_position(self, *args) -> None:
        """
        Randomly generate a position for the item on the game board.
        :param args: Used cells. Tuple.
        """
        all_cells = set(
            (pos_x, pos_y)
            for pos_x in range(0, SCREEN_WIDTH, GRID_SIZE)
            for pos_y in range(0, SCREEN_HEIGHT, GRID_SIZE)
        )
        used_cells = set(args) or self.used_cells
        unused_cells = all_cells - used_cells

        position = choice(tuple(unused_cells))
        self.position = (position if position not in used_cells
                         else self.randomize_position())

    def draw(self):
        """Draw the object on the screen."""
        self.draw_cell(self.position)


class Poison(Apple):
    """Class representing a poison on the game board."""

    def __init__(self, *used_cells, body_color: tuple = POISON_COLOR) -> None:
        super().__init__(body_color=body_color)
        self.randomize_position(*used_cells)


class Snake(GameObject):
    """Class representing the snake on the game board."""

    def __init__(self, body_color: tuple = SNAKE_COLOR) -> None:
        super().__init__(body_color)
        self.direction = RIGHT
        self.body_color = body_color
        self.positions = [self.position]
        self.last = None
        self._max_length = 1

    def update_direction(self, direction: tuple) -> None:
        """
        Update the snake's direction.
        :param direction: New direction to set for the snake.
        """
        self.direction = direction

    def move(self) -> None:
        """Move the snake forward in its current direction."""
        new_head_position = self.get_head_position(self.direction)
        self.positions.insert(0, new_head_position)
        self.last = self.positions.pop()

    def draw(self) -> None:
        """Draw the object on the screen."""
        self.draw_cell(self.get_head_position())
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)

    def get_head_position(self, direction: tuple = None) -> tuple[int, int]:
        """
        Get the position of the snake's head.
        :param direction: New direction to consider
        when calculating the head position.
        :return: tuple of x and y coordinates of the snake's head.
        """
        current_x_pos, current_y_pos = self.positions[0]
        if direction:
            direction_x, direction_y = direction
            return (
                (current_x_pos + direction_x * GRID_SIZE) % SCREEN_WIDTH,
                (current_y_pos + direction_y * GRID_SIZE) % SCREEN_HEIGHT
            )
        else:
            return current_x_pos, current_y_pos

    def reset(self) -> None:
        """Reset the snake to its initial position."""
        self.direction = RIGHT
        self.positions = [self.position]
        self.last = None

    @property
    def max_length(self) -> int:
        """
        Get the maximum length of the snake.
        :return: Maximum length of the snake.
        """
        self._max_length = (len(self.positions)
                            if len(self.positions) > self._max_length
                            else self._max_length)
        return self._max_length


def change_speed(value: int) -> None:
    """
    Change game speed.
    :param value: Value for changing the speed.
    """
    global speed
    speed += value


def update_display_caption(max_length: int) -> None:
    """
    Update the display caption with the current score and speed.
    :param max_length: Current maximum length of the snake.
    """
    pg.display.set_caption(
        f'Скорость: {speed}. '
        f'Max длина: {max_length}. '
        f'Выход - ESC.')


def handle_keys(game_object: Snake):
    """
    Handle keyboard input to control the game object.
    :param game_object: Game object to control.
    """
    direction_mapping = {
        (pg.K_UP, LEFT): UP,
        (pg.K_UP, RIGHT): UP,
        (pg.K_DOWN, LEFT): DOWN,
        (pg.K_DOWN, RIGHT): DOWN,
        (pg.K_LEFT, UP): LEFT,
        (pg.K_LEFT, DOWN): LEFT,
        (pg.K_RIGHT, UP): RIGHT,
        (pg.K_RIGHT, DOWN): RIGHT
    }
    speed_mapping = {
        pg.K_q: 1,
        pg.K_z: -1
    }

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit
            else:
                if event.key in speed_mapping:
                    change_speed(
                        speed_mapping.get(event.key)
                    )
                else:
                    game_object.update_direction(
                        direction_mapping.get(
                            (event.key, game_object.direction),
                            game_object.direction
                        )
                    )


def main():
    """
    Main function for the game.
    Starts the game loop and handles key inputs.
    """
    pg.init()
    screen.fill(BOARD_BACKGROUND_COLOR)

    snake = Snake()
    apple = Apple(*snake.positions)
    poison = Poison(*snake.positions)

    while True:
        handle_keys(snake)
        snake.move()

        snake_head_position = snake.get_head_position()

        if snake_head_position in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(*snake.positions)
            poison.randomize_position(*snake.positions, apple.position)
            screen.fill(color=BOARD_BACKGROUND_COLOR)
        elif snake_head_position == apple.position:
            snake.positions.insert(0, snake.get_head_position())
            apple.randomize_position(*snake.positions)
            poison.draw_cell(poison.position, BOARD_BACKGROUND_COLOR)
            poison.randomize_position(*snake.positions, apple.position)
        elif snake_head_position == poison.position:
            if len(snake.positions) > 1:
                snake.draw_cell(
                    snake.positions.pop(), BOARD_BACKGROUND_COLOR
                )
            apple.draw_cell(apple.position, BOARD_BACKGROUND_COLOR)
            apple.randomize_position(*snake.positions)
            poison.randomize_position(*snake.positions, apple.position)

        snake.draw()
        apple.draw()
        poison.draw()

        pg.display.update()
        update_display_caption(snake.max_length)

        clock.tick(speed)


if __name__ == '__main__':
    main()
