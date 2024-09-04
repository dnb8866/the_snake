import pygame

from collections import deque
from random import choice

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

APPLE_COLOR = (0, 255, 0)
POISON_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 0, 255)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Base class for game objects."""

    def __init__(self) -> None:
        self.position = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.body_color = None

    def draw(self):
        """Draw the object on the screen."""
        pass


class Item(GameObject):
    """Class representing item for snake on the game board."""

    def __init__(self) -> None:
        super().__init__()
        self.position = self.randomize_position()
        self.eatable = None

    def randomize_position(self) -> tuple[int, int]:
        """
        Randomly generate a position for the item on the game board.
        :return: tuple of random x and y coordinates.
        """
        self.position = (
            choice(range(0, SCREEN_WIDTH, GRID_SIZE)),
            choice(range(0, SCREEN_HEIGHT, GRID_SIZE))
        )
        return self.position

    def draw(self):
        """Draw the object on the screen."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(Item):
    """Class representing an apple on the game board."""

    def __init__(self) -> None:
        super().__init__()
        self.body_color = APPLE_COLOR
        self.eatable = True


class Poison(Item):
    """Class representing a poison on the game board."""

    def __init__(self) -> None:
        super().__init__()
        self.body_color = POISON_COLOR
        self.eatable = False


class Snake(GameObject):
    """Class representing the snake on the game board."""

    def __init__(self) -> None:
        super().__init__()
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.body_color = SNAKE_COLOR
        # Использовал deque, тк добавление в начало deque
        # со сложностью O(1), а у списков O(n).
        self.positions = deque((self.position,))
        self.length = len(self.positions) - 1
        self.last = None

    def update_direction(self):
        """Update the snake's direction."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Move the snake forward in its current direction."""
        current_x_pos, current_y_pos = self.get_head_position()
        next_x_pos = (
            (current_x_pos + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH
        )
        next_y_pos = (
            (current_y_pos + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        )
        if (next_x_pos, next_y_pos) in self.positions:
            self.reset()
        else:
            self.positions.appendleft(
                (next_x_pos, next_y_pos)
            )
            self.last = self.positions.pop()

    def draw(self):
        """Draw the object on the screen."""
        for position in list(self.positions)[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> tuple[int, int]:
        """
        Get the position of the snake's head.
        :return: tuple of x and y coordinates of the snake's head.
        """
        return self.positions[0]

    def reset(self):
        """Reset the snake to its initial position."""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)
        self.positions = deque(((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),))

    def increase(self):
        """Increase the snake's length by one."""
        self.positions.append((self.get_head_position()))

    def decrease(self):
        """Decrease the snake's length by one."""
        if len(self.positions) > 1:
            rect = pygame.Rect(self.positions.pop(), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)


def handle_keys(game_object: Snake):
    """
    Handle keyboard input to control the game object.
    :param game_object: Game object to control.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Main function for the game.
    Starts the game loop and handles key inputs.
    """
    pygame.init()

    apple = Apple()
    poison = Poison()
    snake = Snake()

    while True:
        if snake.get_head_position() == apple.position:
            snake.increase()
            apple.randomize_position()
        if snake.get_head_position() == poison.position:
            snake.decrease()
            poison.randomize_position()

        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        apple.draw()
        poison.draw()
        snake.draw()
        snake.move()
        pygame.display.update()


if __name__ == '__main__':
    main()
