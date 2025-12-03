"""
Модерен слот автомат с емоджита, реализиран с pygame.

Този файл е структурирана, „репо-готова“ версия:
- има отделна `main()` функция;
- логиката е разделена в малки, ясни функции;
- без излишни глобални променливи извън конфигурацията.
"""

import io
import os
import random
import sys
from typing import Dict, List, Tuple

import pygame
import pygame.freetype
from PIL import Image, ImageDraw, ImageFont


# Инициализация на pygame и freetype преди създаване на шрифтове
pygame.init()
pygame.freetype.init()


# === Константи и конфигурация ===
# По-компактен начален размер (подходящ за лаптоп), прозорецът е ресайзваем.
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


# === Помощни функции за графика ===
def init_pygame() -> Tuple[pygame.Surface, pygame.time.Clock]:
    """Инициализира pygame, freetype и прозореца."""
    # UTF-8 за конзолата (полезно при дебъг с емоджита)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    pygame.init()
    pygame.freetype.init()
    try:
        pygame.mixer.init()
    except Exception:
        pygame.mixer.quit()

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("BETT CASINO – СЛОТ МАШИНА")
    clock = pygame.time.Clock()
    return screen, clock


def get_font_freetype(size: int) -> pygame.freetype.Font:
    """
    Шрифт за текст (кирилица, латиница, числа).
    НЕ използваме emoji шрифтове тук, за да няма квадратчета.
    """
    for font_name in ["Segoe UI", "Arial", "Tahoma", "Calibri", "DejaVu Sans"]:
        try:
            return pygame.freetype.SysFont(font_name, size, bold=True)
        except Exception:
            continue
    # Fallback – каквото има
    return pygame.freetype.SysFont(None, size)


FONT_BIG = get_font_freetype(80)   # за КРАЙ НА ПАРИТЕ / ДЖАКПОТ
FONT_MED = get_font_freetype(48)   # за баланс, залог, бутони, SPACE...
FONT_SMALL = get_font_freetype(28) # за статистиките



def render_emoji_pil(emoji: str, size: int = 180) -> pygame.Surface:
    """
    Рендерира цветен emoji чрез PIL и го връща като pygame.Surface.
    Първо пробва локалния `NotoColorEmoji.ttf`, после системен emoji шрифт.
    Ако всичко се провали, използва pygame.font като fallback, за да няма квадрати.
    """
    # 1) Пробваме локален emoji шрифт в проекта
    here = os.path.dirname(__file__)
    candidates = [
        os.path.join(here, "NotoColorEmoji.ttf"),
        "C:/Windows/Fonts/seguiemj.ttf",
    ]

    for font_path in candidates:
        try:
            if os.path.exists(font_path):
                pil_font = ImageFont.truetype(font_path, size)

                image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                draw = ImageDraw.Draw(image)
                draw.text((0, 0), emoji, font=pil_font, embedded_color=True)

                mode = image.mode
                img_size = image.size
                data = image.tobytes()
                return pygame.image.fromstring(data, img_size, mode)
        except Exception:
            continue

    # 2) Fallback – pygame.font с няколко възможни emoji шрифта (без цветност, но видими)
    for name in ["Segoe UI Emoji", "NotoColorEmoji", "Arial Unicode MS", "DejaVu Sans"]:
        try:
            font = pygame.font.SysFont(name, size, bold=True)
            if font:
                surf = font.render(emoji, True, WHITE)
                return surf.convert_alpha()
        except Exception:
            continue

    # 3) Последен fallback – стандартен шрифт
    font = pygame.font.SysFont(None, size, bold=True)
    surf = font.render(emoji, True, WHITE)
    return surf.convert_alpha()


_emoji_surfaces_cache: Dict[Tuple[str, int], pygame.Surface] = {}


def get_emoji_surface(emoji: str, size: int = 180) -> pygame.Surface:
    """Кеширане на емоджита за по-бързо рисуване."""
    key = (emoji, size)
    if key not in _emoji_surfaces_cache:
        _emoji_surfaces_cache[key] = render_emoji_pil(emoji, size)
    return _emoji_surfaces_cache[key]


# === Бутони ===
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
        text_surf, text_rect = FONT_MED.render(self.text, fgcolor=WHITE)
        text_rect.center = self.rect.center
        surface.blit(text_surf, text_rect)

    def contains_event(self, event: pygame.event.Event) -> bool:
        return self.rect.collidepoint(event.pos)


def create_buttons(screen: pygame.Surface) -> Dict[str, Button]:
    w, h = screen.get_size()
    return {
        "spin": Button(w // 2 - 180, h - 180, 360, 120, "ВЪРТИ", GREEN, (0, 255, 0)),
        "auto": Button(60, h - 180, 200, 120, "АВТО", LIGHT_BLUE, (100, 220, 255)),
        "p10": Button(w // 2 - 400, h - 280, 140, 80, "+10", LIGHT_BLUE, (100, 200, 255)),
        "m10": Button(w // 2 - 240, h - 280, 140, 80, "-10", LIGHT_BLUE, (100, 200, 255)),
        "p100": Button(w // 2 - 80, h - 280, 140, 80, "+100", LIGHT_BLUE, (100, 200, 255)),
        "m100": Button(w // 2 + 80, h - 280, 140, 80, "-100", LIGHT_BLUE, (100, 200, 255)),
        "max": Button(w - 300, h - 280, 220, 80, "МАКС БЕТ", RED, (255, 50, 50)),
    }


# === Игрова логика ===
def start_spin(state: dict) -> None:
    """Започва завъртане, ако имаме пари или free spins."""
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


def check_wins(state: dict) -> Tuple[int, str | None]:
    """Проверява всички печеливши линии и връща общата печалба и евентуално джакпот съобщение."""
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
                jackpot_msg = f"ДЖАКПОТ {jp_amount:,} лв!".replace(",", " ")

    return total_win, jackpot_msg


def update_spin(state: dict) -> None:
    """Ъпдейт на релсите по време на въртене."""
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


# === Рендер функции ===
def draw_reels(screen: pygame.Surface, state: dict) -> None:
    """Рисува рамката и 3×3 емоджи решетката, центрирани и скалирани според прозореца."""
    w, h = screen.get_size()

    # Размер на рамката – ~70% от ширината и ~45% от височината
    frame_w = int(w * 0.7)
    frame_h = int(h * 0.45)
    frame_x = (w - frame_w) // 2
    frame_y = int(h * 0.2)

    pygame.draw.rect(screen, BLACK, (frame_x, frame_y, frame_w, frame_h), border_radius=30)
    pygame.draw.rect(screen, GOLD, (frame_x, frame_y, frame_w, frame_h), 14, border_radius=30)

    # Позиции на 3×3 решетка в рамката
    cell_w = frame_w / 3
    cell_h = frame_h / 3
    # Размер на емоджито – малко по-малко от клетката
    emoji_size = int(min(cell_w, cell_h) * 0.8)

    for r in range(3):
        for c in range(3):
            emoji_img = get_emoji_surface(state["reels"][r][c], emoji_size)
            center_x = frame_x + (c + 0.5) * cell_w
            center_y = frame_y + (r + 0.5) * cell_h
            img_rect = emoji_img.get_rect(center=(int(center_x), int(center_y)))
            screen.blit(emoji_img, img_rect)


def draw_hud(screen: pygame.Surface, state: dict) -> None:
    w, _ = screen.get_size()

    # Баланс и залог
    text_surface, rect = FONT_MED.render(f"БАЛАНС: {state['balance']:,} лв.".replace(",", " "), fgcolor=GOLD)
    rect.topleft = (50, 30)
    screen.blit(text_surface, rect)

    text_surface, rect = FONT_MED.render(f"ЗАЛОГ: {state['bet']} лв.", fgcolor=WHITE)
    rect.topright = (w - 50, 30)
    screen.blit(text_surface, rect)

    text_surface, rect = FONT_MED.render(f"FREE SPINS: {state['free_spins']}", fgcolor=YELLOW)
    rect.midtop = (w // 2, 80)
    screen.blit(text_surface, rect)


def draw_win(screen: pygame.Surface, state: dict) -> None:
    # ако таймерът е изтекъл – нищо не рисуваме
    if state["win_timer"] <= 0:
        return

    # ако няма печалба и не е джакпот – не показваме надпис
    if state["win_amount"] <= 0 and not state["jackpot_msg"]:
        return

    state["win_timer"] -= 1

    w, h = screen.get_size()

    # позиционираме надписа малко под рамката, над бутоните
    frame_w = int(w * 0.7)
    frame_h = int(h * 0.45)
    frame_x = (w - frame_w) // 2
    frame_y = int(h * 0.2)
    center_x = frame_x + frame_w // 2
    y = frame_y + frame_h + 40   # 40px под рамката

    if state["jackpot_msg"]:
        text_surface, rect = FONT_BIG.render(state["jackpot_msg"], fgcolor=PURPLE)
    else:
        text_surface, rect = FONT_BIG.render(
            f"+{state['win_amount']:,} лв.!".replace(",", " "),
            fgcolor=GOLD,
        )

    rect.center = (center_x, y)
    screen.blit(text_surface, rect)


def draw_stats(screen: pygame.Surface, state: dict) -> None:
    # При КРАЙ НА ПАРИТЕ не показваме статистика – да не се претрупва екрана
    if state["balance"] <= 0 and state["free_spins"] == 0:
        return

    stats = [
        f"Най-голям баланс: {state['high_score']:,} лв.".replace(",", " "),
        f"Най-голяма печалба: {state['max_single_win']:,} лв.".replace(",", " "),
        f"Общо спечелени: {state['total_wins']:,} лв.".replace(",", " "),
        f"Джакпот удари: {state['jackpot_hits']} пъти",
    ]

    w, h = screen.get_size()
    start_x = 50              # малко навътре от левия ръб
    start_y = 120             # под горния HUD

    for i, text in enumerate(stats):
        text_surface, rect = FONT_SMALL.render(text, fgcolor=WHITE)
        rect.topleft = (start_x, start_y + i * (rect.height + 6))
        screen.blit(text_surface, rect)


def draw_game_over(screen: pygame.Surface, state: dict) -> None:
    """
    Показва екран КРАЙ НА ПАРИТЕ, центриран в рамката на слота.
    """
    if state["balance"] > 0 or state["free_spins"] > 0:
        return

    w, h = screen.get_size()

    # Същите размери както в draw_reels
    frame_w = int(w * 0.7)
    frame_h = int(h * 0.45)
    frame_x = (w - frame_w) // 2
    frame_y = int(h * 0.2)

    center_x = frame_x + frame_w // 2

    # Голям червен текст – горната половина на рамката
    text_surface, rect = FONT_BIG.render("КРАЙ НА ПАРИТЕ!", fgcolor=RED)
    rect.center = (center_x, frame_y + int(frame_h * 0.35))
    screen.blit(text_surface, rect)

    # Инструкция за нова игра – долната част на рамката
    text_surface, rect = FONT_MED.render("SPACE – 50 000 лв. нова игра", fgcolor=WHITE)
    rect.center = (center_x, frame_y + int(frame_h * 0.7))
    screen.blit(text_surface, rect)


def handle_events(screen: pygame.Surface, state: dict, buttons: Dict[str, Button]) -> bool:
    """Обработва pygame събитията. Връща False при изход от играта."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.VIDEORESIZE:
            # само обновяваме размера; самият surface идва от pygame
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

        if event.type == pygame.KEYDOWN:
            # SPACE -> или нова игра, или върти
            if event.key == pygame.K_SPACE:
                if state["balance"] <= 0 and state["free_spins"] == 0:
                    # Нова игра
                    state["balance"] = 50000
                    state["bet"] = 50
                    state["free_spins"] = 0
                    state["auto_spin"] = False
                else:
                    start_spin(state)

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
        screen.fill(DARK_GREEN)
        buttons = create_buttons(screen)

        running = handle_events(screen, state, buttons)

        if state["auto_spin"] and not state["spinning"] and state["free_spins"] == 0:
            start_spin(state)

        update_spin(state)

        # Обновяване на high score
        state["high_score"] = max(state["high_score"], state["balance"])

        # Рендер
        draw_reels(screen, state)
        draw_hud(screen, state)
        draw_win(screen, state)
        draw_stats(screen, state)
        draw_game_over(screen, state)

        for btn in buttons.values():
            btn.draw(screen)
        # АВТО режим – върти, докато има пари или free spins.
        # Спира единствено, ако натиснеш АВТО пак.
        if state["auto_spin"] and not state["spinning"]:
            start_spin(state)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
