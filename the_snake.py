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

SPEED = 10

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill(BOARD_BACKGROUND_COLOR)

clock = pg.time.Clock()


class GameObject:
    """Base class for game objects."""

    def __init__(self, body_color: tuple = None) -> None:
        self.position = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.body_color = body_color

    def draw_cell(self, position: tuple, body_color: tuple = None,
                  clean: bool = False) -> None:
        """Draw the cell on the screen."""
        body_color = body_color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, body_color, rect)
        if not clean:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    @abstractmethod
    def draw(self) -> None:
        """Draw the object on the screen."""


class Apple(GameObject):
    """Class representing an apple on the game board."""

    def __init__(self, body_color: tuple = None) -> None:
        super().__init__(body_color)
        self.position = None

    def randomize_position(self, used_cells) -> tuple:
        """
        Randomly generate a position for the item on the game board.
        :param used_cells: List of used cells on the game board.
        :return: Randomized position.
        """
        used_cells = used_cells or []
        position = (
            choice(range(0, SCREEN_WIDTH, GRID_SIZE)),
            choice(range(0, SCREEN_HEIGHT, GRID_SIZE))
        )
        self.position = (position if position not in used_cells
                         else self.randomize_position(used_cells))
        return position

    def draw(self):
        """Draw the object on the screen."""
        self.draw_cell(self.position)


class Poison(Apple):
    """Class representing a poison on the game board."""


class Snake(GameObject):
    """Class representing the snake on the game board."""

    def __init__(self, direction: tuple = RIGHT,
                 body_color: tuple = None, speed: int = 10) -> None:
        super().__init__(body_color)
        self.direction = direction
        self.body_color = body_color
        self.speed = speed
        self.positions = [self.position]
        self.last = None
        self._max_length = 1

    def update_direction(self, direction: tuple) -> None:
        """
        Update the snake's direction.
        :param direction: New direction to set for the snake.
        """
        if direction == UP:
            self.direction = UP if direction != DOWN else DOWN
        elif direction == DOWN:
            self.direction = DOWN if direction != UP else UP
        elif direction == LEFT:
            self.direction = LEFT if direction != RIGHT else RIGHT
        elif direction == RIGHT:
            self.direction = RIGHT if direction != LEFT else LEFT

    def move(self) -> None:
        """Move the snake forward in its current direction."""
        new_head_position = self.get_head_position(self.direction)
        self.positions.insert(0, new_head_position)
        self.last = self.positions.pop()

    def draw(self) -> None:
        """Draw the object on the screen."""
        self.draw_cell(self.get_head_position())
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, clean=True)

    def get_head_position(self, direction: tuple = None) -> tuple[int, int]:
        """
        Get the position of the snake's head.
        :param direction: New direction to consider
        when calculating the head position.
        :return: tuple of x and y coordinates of the snake's head.
        """
        if direction:
            current_x_pos, current_y_pos = self.get_head_position()
            direction_x, direction_y = direction
            new_position = (
                (current_x_pos + direction_x * GRID_SIZE) % SCREEN_WIDTH,
                (current_y_pos + direction_y * GRID_SIZE) % SCREEN_HEIGHT
            )
            return new_position
        else:
            return self.positions[0]

    def reset(self, direction: tuple, body_color: tuple = None) -> None:
        """Reset the snake to its initial position."""
        self.positions = [self.position]
        self.direction = direction
        self.body_color = body_color

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

    def change_speed(self, value: int) -> None:
        """Change the snake's speed."""
        if not self.speed + value <= 0:
            self.speed += value or self.speed


def get_used_cells(*args) -> list:
    """
    Get a list of used cells from the game objects.
    :param args: Game objects that use cells.
    Takes a lists and tuples with coordinates.
    :return: List of used cells.
    """
    if not args:
        return []

    used_cells = []
    for obj in args:
        if isinstance(obj[0], tuple):
            used_cells.extend(obj)
        else:
            used_cells.append(obj)
    return used_cells


def update_display_caption(speed: int, max_length: int) -> None:
    """
    Update the display caption with the current score and speed.
    :param speed: Current game speed.
    :param max_length: Current maximum length of the snake.
    """
    pg.display.set_caption(
        f'Скорость (кнопки Q и Z): {speed}. '
        f'Максимальная длина змейки: {max_length}. '
        f'Выход - ESC.')


def handle_keys(game_object: Snake):
    """
    Handle keyboard input to control the game object.
    :param game_object: Game object to control.
    """
    key_mapping = {
        pg.K_UP: (game_object.update_direction, UP),
        pg.K_LEFT: (game_object.update_direction, LEFT),
        pg.K_RIGHT: (game_object.update_direction, RIGHT),
        pg.K_DOWN: (game_object.update_direction, DOWN),
        pg.K_q: (game_object.change_speed, 1),
        pg.K_z: (game_object.change_speed, -1)
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
                action = key_mapping.get(event.key)
                if action:
                    action[0](action[1])


def main():
    """
    Main function for the game.
    Starts the game loop and handles key inputs.
    """
    pg.init()

    snake = Snake(body_color=SNAKE_COLOR)
    apple = Apple(APPLE_COLOR)
    poison = Poison(POISON_COLOR)

    pg.display.set_caption(
        f'Скорость (кнопки Q и Z): {snake.speed}. '
        f'Максимальная длина змейки: {snake.max_length}. '
        f'Выход - ESC.'
    )

    apple.randomize_position(snake.get_head_position())
    poison.randomize_position(get_used_cells(snake.positions, apple.position))

    while True:

        handle_keys(snake)
        snake.move()

        snake_head_position = snake.get_head_position()

        snake.draw()

        if snake_head_position in snake.positions[1:]:
            snake.reset(RIGHT, SNAKE_COLOR)
            apple.randomize_position(snake.positions)
            poison.randomize_position(
                get_used_cells(snake.positions, apple.position)
            )
            screen.fill(color=BOARD_BACKGROUND_COLOR)
        elif snake_head_position == apple.position:
            snake.positions.insert(0, snake.get_head_position())
            apple.randomize_position(snake.positions)
        elif snake_head_position == poison.position:
            if len(snake.positions) > 1:
                snake.draw_cell(
                    snake.positions.pop(), BOARD_BACKGROUND_COLOR, clean=True
                )
            poison.randomize_position(snake.positions)

        apple.draw()
        poison.draw()

        pg.display.update()
        update_display_caption(snake.speed, snake.max_length)

        clock.tick(snake.speed)


if __name__ == '__main__':
    main()
