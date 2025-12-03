"""
Оригиналният по-прост 3-ролков слот – лек, със стари бутони, но вече структуриран за репо.
"""

import random
import sys
from typing import Dict, List, Tuple

import pygame


WIDTH, HEIGHT = 900, 700
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 180, 0)
DARK_GREEN = (0, 100, 0)
RED = (220, 20, 60)
GOLD = (255, 215, 0)
LIGHT_BLUE = (70, 130, 255)

EMOJIS: List[str] = ["🍒", "🍋", "🍊", "🍇", "🔔", "💎", "7️⃣"]

WIN_TABLE: Dict[Tuple[str, str, str], int] = {
    ("🍒", "🍒", "🍒"): 2,
    ("🍋", "🍋", "🍋"): 3,
    ("🍊", "🍊", "🍊"): 5,
    ("🍇", "🍇", "🍇"): 8,
    ("🔔", "🔔", "🔔"): 15,
    ("💎", "💎", "💎"): 35,
    ("7️⃣", "7️⃣", "7️⃣"): 100,
}


def init_pygame() -> tuple[pygame.Surface, pygame.time.Clock]:
    """Инициализира pygame преди да създадем шрифтове/прозорец."""
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        pygame.mixer.quit()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("КАЗИНО СЛОТ МАШИНА – George Edition")
    clock = pygame.time.Clock()
    return screen, clock


# Викаме init_pygame веднъж, за да сме сигурни, че font модулът е инициализиран,
# след което шрифтовете могат безопасно да се създадат.
pygame.init()

BIG_FONT = pygame.font.SysFont("arial", 80, bold=True)
MEDIUM_FONT = pygame.font.SysFont("arial", 50, bold=True)


class Button:
    def __init__(self, x: int, y: int, w: int, h: int, text: str, color, hover) -> None:
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover = hover

    def draw(self, surface: pygame.Surface) -> None:
        color = self.hover if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        pygame.draw.rect(surface, GOLD, self.rect, 6, border_radius=15)
        txt = BIG_FONT.render(self.text, True, WHITE)
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.centery - txt.get_height() // 2))

    def contains_event(self, event: pygame.event.Event) -> bool:
        return self.rect.collidepoint(event.pos)


def create_buttons() -> Dict[str, Button]:
    return {
        "spin": Button(WIDTH // 2 - 150, 550, 300, 100, "ВЪРТИ", GREEN, (0, 255, 0)),
        "auto": Button(40, 550, 180, 100, "АВТО", LIGHT_BLUE, (150, 200, 255)),
        "p10": Button(150, 480, 100, 60, "+10", LIGHT_BLUE, (100, 180, 255)),
        "p50": Button(270, 480, 100, 60, "+50", LIGHT_BLUE, (100, 180, 255)),
        "p100": Button(390, 480, 100, 60, "+100", LIGHT_BLUE, (100, 180, 255)),
        "max": Button(530, 480, 140, 60, "МАКС", RED, (255, 50, 50)),
    }


def draw_emoji(surface: pygame.Surface, emoji: str, x: int, y: int, size: int = 140) -> None:
    font = pygame.font.SysFont("Segoe UI Emoji", size, bold=True)
    surf = font.render(emoji, True, WHITE)
    surface.blit(surf, (x - surf.get_width() // 2, y - surf.get_height() // 2))


def start_spin(state: dict) -> None:
    if state["balance"] >= state["bet"] and not state["spinning"]:
        state["balance"] -= state["bet"]
        state["spinning"] = True
        state["win_to_show"] = None
        delay = 0
        for col in state["columns"]:
            col["timer"] = random.randint(20, 35) + delay
            col["stop"] = col["timer"]
            delay += 10


def check_win(state: dict, result: List[str]) -> int:
    result_tuple = tuple(result)
    if result_tuple in WIN_TABLE:
        return state["bet"] * WIN_TABLE[result_tuple]
    return 0


def main() -> None:
    screen, clock = init_pygame()
    buttons = create_buttons()

    state = {
        "balance": 50000,
        "bet": 50,
        "columns": [
            {"emoji": "❔", "timer": 0, "stop": 0},
            {"emoji": "❔", "timer": 0, "stop": 0},
            {"emoji": "❔", "timer": 0, "stop": 0},
        ],
        "spinning": False,
        "auto_spin": False,
        "win_to_show": None,
        "win_timer": 0,
    }

    running = True
    while running:
        screen.fill(DARK_GREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons["spin"].contains_event(event):
                    start_spin(state)
                if buttons["auto"].contains_event(event):
                    state["auto_spin"] = not state["auto_spin"]
                if buttons["p10"].contains_event(event):
                    state["bet"] = min(state["bet"] + 10, state["balance"])
                if buttons["p50"].contains_event(event):
                    state["bet"] = min(state["bet"] + 50, state["balance"])
                if buttons["p100"].contains_event(event):
                    state["bet"] = min(state["bet"] + 100, state["balance"])
                if buttons["max"].contains_event(event):
                    state["bet"] = state["balance"]

        if state["auto_spin"] and not state["spinning"]:
            start_spin(state)

        result_final: List[str] = []
        all_stopped = True
        for col in state["columns"]:
            if col["timer"] > 0:
                col["timer"] -= 1
                col["emoji"] = random.choice(EMOJIS)
                all_stopped = False
            result_final.append(col["emoji"])

        if state["spinning"] and all_stopped:
            state["spinning"] = False
            state["win_to_show"] = check_win(state, result_final)
            state["win_timer"] = 120
            if state["win_to_show"] > 0:
                state["balance"] += state["win_to_show"]

        pygame.draw.rect(screen, BLACK, (120, 130, 660, 240), border_radius=30)
        pygame.draw.rect(screen, GOLD, (120, 130, 660, 240), 15, border_radius=30)

        for i, col in enumerate(state["columns"]):
            draw_emoji(screen, col["emoji"], 250 + i * 215, 250, 160)

        bal_txt = MEDIUM_FONT.render(f"ПАРИ: {state['balance']} лв.", True, GOLD)
        screen.blit(bal_txt, (40, 40))
        bet_txt = MEDIUM_FONT.render(f"ЗАЛОГ: {state['bet']} лв.", True, WHITE)
        screen.blit(bet_txt, (WIDTH - bet_txt.get_width() - 40, 40))

        if state["win_to_show"] and state["win_timer"] > 0:
            state["win_timer"] -= 1
            win_txt = BIG_FONT.render(f"+{state['win_to_show']} лв.!", True, GOLD)
            screen.blit(win_txt, (WIDTH // 2 - win_txt.get_width() // 2, 390))

        for btn in buttons.values():
            btn.draw(screen)

        if state["balance"] <= 0:
            over = BIG_FONT.render("НЯМА ПАРИ!", True, RED)
            screen.blit(over, (WIDTH // 2 - over.get_width() // 2, HEIGHT // 2 - 50))
            again = MEDIUM_FONT.render("SPACE за нова игра", True, WHITE)
            screen.blit(again, (WIDTH // 2 - again.get_width() // 2, HEIGHT // 2 + 20))
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                state["balance"] = 50000
                state["bet"] = 50

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
