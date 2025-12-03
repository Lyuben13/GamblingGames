"""
Минимален 3-символен слот – аркаден стил, подходящ за демо и малък проект.
"""

import random
import sys
from typing import Tuple, List

import pygame


WIDTH, HEIGHT = 700, 500
FPS = 30

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


def init_pygame() -> Tuple[pygame.Surface, pygame.time.Clock]:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🎰 Python Casino Slot Machine – Mini")
    clock = pygame.time.Clock()
    return screen, clock


def get_fonts() -> Tuple[pygame.font.Font, pygame.font.Font]:
    big = pygame.font.SysFont("arial", 50, bold=True)
    small = pygame.font.SysFont("arial", 25)
    return big, small


SYMBOLS: List[str] = ["★", "☆", "♠", "♥", "♦", "♣"]


def spin_slot() -> Tuple[str, str, str]:
    return random.choice(SYMBOLS), random.choice(SYMBOLS), random.choice(SYMBOLS)


def calculate_win(bet: int, s1: str, s2: str, s3: str) -> int:
    if s1 == s2 == s3:
        return bet * 10
    if s1 == s2 or s2 == s3 or s1 == s3:
        return bet * 3
    return 0


def main() -> None:
    screen, clock = init_pygame()
    font, small_font = get_fonts()

    balance = 200
    bet = 10
    slot_result: List[str] = ["★", "☆", "♠"]
    message = ""
    flash_color = WHITE

    running = True
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and balance >= bet:
                    balance -= bet

                    for _ in range(10):
                        slot_result = list(spin_slot())
                        screen.fill(BLACK)
                        for i, sym in enumerate(slot_result):
                            x = 150 + i * 180
                            pygame.draw.rect(screen, GOLD, (x - 50, 150, 100, 100), 3)
                            text_surface = font.render(sym, True, WHITE)
                            screen.blit(text_surface, (x - 20, 160))
                        balance_text = small_font.render(f"Баланс: {balance} лв.", True, GOLD)
                        screen.blit(balance_text, (20, 20))
                        pygame.display.update()
                        pygame.time.delay(50)

                    s1, s2, s3 = slot_result
                    win = calculate_win(bet, s1, s2, s3)
                    if win > 0:
                        balance += win
                        message = f"🎉 Печалба +{win} лв!"
                        flash_color = GREEN if win > bet * 3 else BLUE
                    else:
                        message = "❌ Губиш..."
                        flash_color = RED

        balance_text = small_font.render(f"Баланс: {balance} лв.", True, GOLD)
        screen.blit(balance_text, (20, 20))
        info_text = small_font.render("Натисни SPACE за завъртане", True, WHITE)
        screen.blit(info_text, (20, 60))

        x_positions = [150, 330, 510]
        for i, sym in enumerate(slot_result):
            slot_box = pygame.Rect(x_positions[i] - 50, 150, 100, 100)
            pygame.draw.rect(screen, flash_color, slot_box, 4)
            text_surface = font.render(sym, True, WHITE)
            screen.blit(text_surface, (x_positions[i] - 20, 160))

        msg_text = small_font.render(message, True, flash_color)
        screen.blit(msg_text, (20, HEIGHT - 50))

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
