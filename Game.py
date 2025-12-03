"""
По-лека версия на BETT CASINO слота – без PIL, само с pygame шрифтове и емоджита.

Структурата е подобна на `pp.py`, но кодът е по-изчистен и лек, подходящ за демо/училище.
"""

import io
import random
import sys
from typing import Dict, List, Tuple

import pygame
import pygame.freetype


# === Константи ===
# По-компактен начален размер (подходящ за лаптоп); прозорецът е ресайзваем.
WIDTH, HEIGHT = 1280, 720
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 80, 0)
RED = (220, 20, 60)
GOLD = (255, 215, 0)
LIGHT_BLUE = (70, 180, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)

EMOJIS: List[str] = ["🍒", "🍋", "🍊", "🍇", "🔔", "💎", "7️⃣", "✨", "🔥", "🎵", "⭐", "🏆"]

WIN_TABLE: Dict[Tuple[str, str, str], int] = {
    ("🍒", "🍒", "🍒"): 2,
    ("🍋", "🍋", "🍋"): 3,
    ("🍊", "🍊", "🍊"): 5,
    ("🍇", "🍇", "🍇"): 8,
    ("🔔", "🔔", "🔔"): 15,
    ("💎", "💎", "💎"): 35,
    ("7️⃣", "7️⃣", "7️⃣"): 100,
}

JACKPOTS: Dict[str, int] = {"Mini": 1000, "Major": 5000, "Mega": 20000, "ULTRA": 100000}


def init_pygame() -> tuple[pygame.Surface, pygame.time.Clock]:
    """Инициализация на pygame и прозореца."""
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    pygame.init()
    pygame.freetype.init()
    try:
        pygame.mixer.init()
    except Exception:
        pygame.mixer.quit()

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("BETT CASINO – СЛОТ МАШИНА (Лека версия)")
    clock = pygame.time.Clock()
    return screen, clock


def get_font(size: int) -> pygame.font.Font:
    """Шрифт, който поддържа емоджита, доколкото е възможно."""
    for font_name in ["Segoe UI Emoji", "NotoColorEmoji", "Apple Color Emoji", "Arial Unicode MS", "DejaVu Sans"]:
        font = pygame.font.SysFont(font_name, size, bold=True)
        if font:
            return font
    return pygame.font.SysFont(None, size)


# Инициализация на font модула ПРЕДИ да създадем големите шрифтове
pygame.init()

BIG_FONT = get_font(140)
MED_FONT = get_font(80)
SMALL_FONT = get_font(40)


class Button:
    def __init__(self, x: int, y: int, w: int, h: int, text: str, color, hover) -> None:
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover = hover

    def draw(self, surface: pygame.Surface) -> None:
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=20)
        pygame.draw.rect(surface, GOLD, self.rect, 8, border_radius=20)
        txt = MED_FONT.render(self.text, True, WHITE)
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.centery - txt.get_height() // 2))

    def contains_event(self, event: pygame.event.Event) -> bool:
        return self.rect.collidepoint(event.pos)


def create_buttons(screen: pygame.Surface) -> Dict[str, Button]:
    w, h = screen.get_size()
    return {
        "spin": Button(w // 2 - 180, h - 180, 360, 120, "🎰 ВЪРТИ", GREEN, (0, 255, 0)),
        "auto": Button(60, h - 180, 200, 120, "АВТО", LIGHT_BLUE, (100, 220, 255)),
        "p10": Button(w // 2 - 400, h - 280, 140, 80, "+10", LIGHT_BLUE, (100, 200, 255)),
        "m10": Button(w // 2 - 240, h - 280, 140, 80, "-10", LIGHT_BLUE, (100, 200, 255)),
        "p100": Button(w // 2 - 80, h - 280, 140, 80, "+100", LIGHT_BLUE, (100, 200, 255)),
        "m100": Button(w // 2 + 80, h - 280, 140, 80, "-100", LIGHT_BLUE, (100, 200, 255)),
        "max": Button(w - 300, h - 280, 220, 80, "МАКС БЕТ", RED, (255, 50, 50)),
    }


def start_spin(state: dict) -> None:
    if (state["balance"] >= state["bet"] or state["free_spins"] > 0) and not state["spinning"]:
        if state["free_spins"] == 0:
            state["balance"] -= state["bet"]
        else:
            state["free_spins"] -= 1
        state["spinning"] = True
        state["win_amount"] = 0
        base = 20
        for r in range(3):
            for c in range(3):
                state["timers"][r][c] = base + random.randint(5, 25) + c * 12 + r * 8


def check_wins(state: dict) -> tuple[int, str | None]:
    reels = state["reels"]
    bet = state["bet"]
    lines = [
        [reels[0][0], reels[1][0], reels[2][0]],
        [reels[0][1], reels[1][1], reels[2][1]],
        [reels[0][2], reels[1][2], reels[2][2]],
        [reels[0][0], reels[0][1], reels[0][2]],
        [reels[1][0], reels[1][1], reels[1][2]],
        [reels[2][0], reels[2][1], reels[2][2]],
        [reels[0][0], reels[1][1], reels[2][2]],
        [reels[2][0], reels[1][1], reels[0][2]],
    ]
    total_win = 0
    jackpot_msg = None
    for line in lines:
        if all(s == line[0] for s in line) and tuple(line) in WIN_TABLE:
            win = bet * WIN_TABLE[tuple(line)]
            total_win += win
            state["balance"] += win
            state["total_wins"] += win
            state["max_single_win"] = max(state["max_single_win"], win)
            if line[0] == "7️⃣":
                jp_amount = random.choice(list(JACKPOTS.values()))
                state["balance"] += jp_amount
                total_win += jp_amount
                state["jackpot_hits"] += 1
                jackpot_msg = f"ДЖАКПОТ {jp_amount:,} лв.!".replace(",", " ")
    return total_win, jackpot_msg


def update_spin(state: dict) -> None:
    if not state["spinning"]:
        return
    all_stopped = True
    for r in range(3):
        for c in range(3):
            if state["timers"][r][c] > 0:
                state["timers"][r][c] -= 1
                if state["timers"][r][c] % 4 == 0:
                    state["reels"][r][c] = random.choice(EMOJIS)
                all_stopped = False
    if all_stopped:
        state["spinning"] = False
        state["win_amount"], state["jackpot_msg"] = check_wins(state)
        state["win_timer"] = 200
        sparkle_count = sum(row.count("✨") for row in state["reels"])
        if sparkle_count >= 3:
            state["free_spins"] += sparkle_count


def draw_emoji(screen: pygame.Surface, emoji: str, x: int, y: int, size: int = 160) -> None:
    font = get_font(size)
    surf = font.render(emoji, True, WHITE)
    screen.blit(surf, (x - surf.get_width() // 2, y - surf.get_height() // 2))


def draw_scene(screen: pygame.Surface, state: dict, buttons: Dict[str, Button]) -> None:
    """Рисува целия слот – фон, рамка, решетка, HUD и бутони – респонсив по размер."""
    screen.fill(DARK_GREEN)
    w, h = screen.get_size()

    # Рамка на слота – центрирана и скалирана
    frame_w = int(w * 0.7)
    frame_h = int(h * 0.45)
    frame_x = (w - frame_w) // 2
    frame_y = int(h * 0.2)

    pygame.draw.rect(screen, BLACK, (frame_x, frame_y, frame_w, frame_h), border_radius=30)
    pygame.draw.rect(screen, GOLD, (frame_x, frame_y, frame_w, frame_h), 16, border_radius=30)

    # 3×3 решетка вътре в рамката
    cell_w = frame_w / 3
    cell_h = frame_h / 3
    emoji_size = int(min(cell_w, cell_h) * 0.8)

    for r in range(3):
        for c in range(3):
            emoji = state["reels"][r][c]
            center_x = frame_x + (c + 0.5) * cell_w
            center_y = frame_y + (r + 0.5) * cell_h
            draw_emoji(screen, emoji, int(center_x), int(center_y), emoji_size)

    # HUD – баланс, залог, free spins
    bal_txt = MED_FONT.render(f"БАЛАНС: {state['balance']:,} лв.".replace(",", " "), True, GOLD)
    screen.blit(bal_txt, (40, 30))
    bet_txt = MED_FONT.render(f"ЗАЛОГ: {state['bet']} лв.", True, WHITE)
    screen.blit(bet_txt, (w - bet_txt.get_width() - 40, 30))
    fs_txt = MED_FONT.render(f"FREE SPINS: {state['free_spins']}", True, YELLOW)
    screen.blit(fs_txt, (w // 2 - fs_txt.get_width() // 2, 80))

    # Печалба / джакпот текст
    if state["win_timer"] > 0:
        state["win_timer"] -= 1
        if state["jackpot_msg"]:
            big_win = BIG_FONT.render(state["jackpot_msg"], True, PURPLE)
        else:
            big_win = BIG_FONT.render(f"+{state['win_amount']:,} лв.!", True, GOLD)
        screen.blit(big_win, (w // 2 - big_win.get_width() // 2, frame_y + frame_h + 40))

    # Бутони
    for btn in buttons.values():
        btn.draw(screen)
    if state["auto_spin"]:
        auto_txt = MED_FONT.render("АВТО", True, YELLOW)
        screen.blit(auto_txt, (90, h - 160))

    # Статистика
    stats = [
        f"Най-голям баланс: {state['high_score']:,} лв.",
        f"Най-голяма печалба: {state['max_single_win']:,} лв.",
        f"Общо спечелени: {state['total_wins']:,} лв.",
        f"Джакпот удари: {state['jackpot_hits']} пъти",
    ]
    for i, text in enumerate(stats):
        t = SMALL_FONT.render(text, True, WHITE)
        screen.blit(t, (40, 150 + i * 50))

    # Край на парите
    if state["balance"] <= 0 and state["free_spins"] == 0:
        over = BIG_FONT.render("КРАЙ НА ПАРИТЕ!", True, RED)
        screen.blit(over, (w // 2 - over.get_width() // 2, h // 2 - 100))
        again = MED_FONT.render("SPACE – 50 000 лв. нова игра", True, WHITE)
        screen.blit(again, (w // 2 - again.get_width() // 2, h // 2 + 20))


def handle_events(screen: pygame.Surface, state: dict, buttons: Dict[str, Button]) -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.VIDEORESIZE:
            state["width"], state["height"] = event.w, event.h
        if event.type == pygame.MOUSEBUTTONDOWN:
            if buttons["spin"].contains_event(event):
                start_spin(state)
            if buttons["auto"].contains_event(event):
                state["auto_spin"] = not state["auto_spin"]
            if buttons["p10"].contains_event(event):
                state["bet"] = min(state["bet"] + 10, state["balance"])
            if buttons["m10"].contains_event(event):
                state["bet"] = max(state["bet"] - 10, 1)
            if buttons["p100"].contains_event(event):
                state["bet"] = min(state["bet"] + 100, state["balance"])
            if buttons["m100"].contains_event(event):
                state["bet"] = max(state["bet"] - 100, 1)
            if buttons["max"].contains_event(event):
                state["bet"] = state["balance"]
        if event.type == pygame.KEYDOWN and state["balance"] <= 0 and state["free_spins"] == 0:
            if event.key == pygame.K_SPACE:
                state["balance"] = 50000
                state["bet"] = 50
                state["free_spins"] = 0
                state["auto_spin"] = False
    return True


def main() -> None:
    screen, clock = init_pygame()
    state = {
        "width": WIDTH,
        "height": HEIGHT,
        "balance": 50000,
        "bet": 50,
        "spinning": False,
        "auto_spin": False,
        "win_amount": 0,
        "win_timer": 0,
        "free_spins": 0,
        "high_score": 0,
        "total_wins": 0,
        "jackpot_hits": 0,
        "max_single_win": 0,
        "reels": [["❔"] * 3 for _ in range(3)],
        "timers": [[0] * 3 for _ in range(3)],
        "jackpot_msg": None,
    }

    running = True
    while running:
        buttons = create_buttons(screen)
        running = handle_events(screen, state, buttons)

        if state["auto_spin"] and not state["spinning"] and state["free_spins"] == 0:
            start_spin(state)

        update_spin(state)
        state["high_score"] = max(state["high_score"], state["balance"])

        draw_scene(screen, state, buttons)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
