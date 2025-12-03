import pygame
import random
import sys

pygame.init()

# Начални размери
window_x, window_y = 720, 480

# Създаване на прозорец, който може да се преоразмерява
game_window = pygame.display.set_mode((window_x, window_y), pygame.RESIZABLE)
pygame.display.set_caption('Змейка (Responsive)')

# Цветове
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)












fps = pygame.time.Clock()

# Начална големина на клетката (ще се променя според размера)
cell_size = 20

def show_score(score, surface):
    font = pygame.font.SysFont('Arial', 24)
    score_surface = font.render(f'Резултат: {score}', True, white)
    surface.blit(score_surface, (10, 10))

def game_over_screen(score, surface, width, height):
    font_big = pygame.font.SysFont('Arial', 72)
    font_small = pygame.font.SysFont('Arial', 36)

    surface.fill(black)
    game_over_surface = font_big.render('Game Over', True, red)
    score_surface = font_small.render(f'Вашият резултат: {score}', True, white)
    restart_surface = font_small.render('Натиснете R за рестарт или Q за изход', True, white)

    surface.blit(game_over_surface, (width // 2 - game_over_surface.get_width() // 2, height // 3))
    surface.blit(score_surface, (width // 2 - score_surface.get_width() // 2, height // 3 + 100))
    surface.blit(restart_surface, (width // 2 - restart_surface.get_width() // 2, height // 3 + 160))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def main():
    global game_window, window_x, window_y, cell_size

    # Позиция и тяло на змейката в клетки
    snake_position = [10, 10]
    snake_body = [snake_position[:], [9, 10], [8, 10]]

    fruit_position = [random.randint(0, (window_x // cell_size) - 1), random.randint(0, (window_y // cell_size) - 1)]
    fruit_spawn = True

    direction = 'RIGHT'
    change_to = direction

    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.VIDEORESIZE:
                # Когато прозорецът се променя, обновяваме размерите
                window_x, window_y = event.w, event.h
                game_window = pygame.display.set_mode((window_x, window_y), pygame.RESIZABLE)
                # Преизчисляваме size на клетка според новия размер (например 20 пиксела, или по-голяма)
                # Оптимално да е така, че да има около 30 клетки по ширина (примерно)
                cell_size = max(10, min(window_x // 30, window_y // 20))  # Ограничаваме минимален размер на клетката

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != 'DOWN':
                    change_to = 'UP'
                elif event.key == pygame.K_DOWN and direction != 'UP':
                    change_to = 'DOWN'
                elif event.key == pygame.K_LEFT and direction != 'RIGHT':
                    change_to = 'LEFT'
                elif event.key == pygame.K_RIGHT and direction != 'LEFT':
                    change_to = 'RIGHT'

        direction = change_to

        # Преместване на змейката
        if direction == 'UP':
            snake_position[1] -= 1
        elif direction == 'DOWN':
            snake_position[1] += 1
        elif direction == 'LEFT':
            snake_position[0] -= 1
        elif direction == 'RIGHT':
            snake_position[0] += 1

        snake_body.insert(0, list(snake_position))

        if snake_position == fruit_position:
            score += 1
            fruit_spawn = False
        else:
            snake_body.pop()

        if not fruit_spawn:
            # Генерираме плод в нова позиция, според новия размер
            max_cells_x = window_x // cell_size
            max_cells_y = window_y // cell_size
            fruit_position = [random.randint(0, max_cells_x - 1), random.randint(0, max_cells_y - 1)]
            fruit_spawn = True

        # Размер на мрежата в клетки спрямо текущия прозорец
        max_cells_x = window_x // cell_size
        max_cells_y = window_y // cell_size

        # Wrap около ръбовете вместо Game Over
        if snake_position[0] < 0:
            snake_position[0] = max_cells_x - 1
        elif snake_position[0] >= max_cells_x:
            snake_position[0] = 0
        if snake_position[1] < 0:
            snake_position[1] = max_cells_y - 1
        elif snake_position[1] >= max_cells_y:
            snake_position[1] = 0

        # Проверка за удари в тялото (оставяме Game Over)
        for block in snake_body[1:]:
            if snake_position == block:
                game_over_screen(score, game_window, window_x, window_y)

        game_window.fill(black)

        # Рисуваме змейката
        for block in snake_body:
            pygame.draw.rect(game_window, green,
                             pygame.Rect(block[0] * cell_size, block[1] * cell_size, cell_size, cell_size))

        # Рисуваме плода
        pygame.draw.rect(game_window, red,
                         pygame.Rect(fruit_position[0] * cell_size, fruit_position[1] * cell_size, cell_size, cell_size))

        show_score(score, game_window)

        pygame.display.update()

        fps.tick(10)

if __name__ == "__main__":
    main()
