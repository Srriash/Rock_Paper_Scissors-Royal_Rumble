import sys
import random
from pathlib import Path
import pygame

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rps.logic import get_computer_move, winner_decider

WIDTH, HEIGHT = 800, 480
BG_COLOR = (18, 18, 30)
PANEL_COLOR = (26, 26, 40)
ACCENT = (255, 168, 0)
TEXT_COLOR = (230, 230, 230)

pygame.init()
pygame.mixer.init()

ASSET_DIR = Path(__file__).resolve().parents[2] / "assets" / "audio"

# --- LOAD SOUNDS (now under assets/audio) ---
try:
    pygame.mixer.music.load(str(ASSET_DIR / "bg_battle.wav"))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)  # loop forever
except pygame.error:
    pygame.mixer.music.stop()

try:
    SND_WIN = pygame.mixer.Sound(str(ASSET_DIR / "sfx_win.wav"))
    SND_LOSE = pygame.mixer.Sound(str(ASSET_DIR / "sfx_dramatic.wav"))
    SND_TIE = pygame.mixer.Sound(str(ASSET_DIR / "sfx_click.wav"))
except pygame.error:
    SND_WIN = SND_LOSE = SND_TIE = None

class Button:
    def __init__(self, rect, text, color, key=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.key = key

    def draw(self, surf, font):
        pygame.draw.rect(surf, self.color, self.rect, border_radius=8)
        txt = font.render(self.text, True, (0, 0, 0))
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_text_center(surf, text, font, y, color=TEXT_COLOR):
    txt = font.render(text, True, color)
    surf.blit(txt, txt.get_rect(center=(WIDTH // 2, y)))

def show_quit_dialog(screen, font_mid, font_small):
    """Return True if user confirms quit, False otherwise."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    box_w, box_h = 500, 220
    box_rect = pygame.Rect((WIDTH - box_w) // 2, (HEIGHT - box_h) // 2, box_w, box_h)
    pygame.draw.rect(screen, PANEL_COLOR, box_rect, border_radius=12)
    pygame.draw.rect(screen, ACCENT, box_rect, 2, border_radius=12)

    draw_text_center(screen, "Are you sure you want to quit?", font_mid, box_rect.y + 50)
    draw_text_center(screen, "Press Y to quit, N to stay", font_small, box_rect.y + 110)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_y, pygame.K_RETURN):
                    return True
                if event.key in (pygame.K_n, pygame.K_ESCAPE):
                    return False

def show_final_message(screen, font_mid, font_small, player_name, player_score, computer_score):
    if player_score == computer_score == 0:
        msg1 = "Just try the game once"
        msg2 = "and I am sure you will love it!!"
        color = (255, 80, 80)
    elif player_score > computer_score:
        msg1 = f"You, {player_name}, scored {player_score}"
        msg2 = "YOU BEAT THE ALMIGHTY COMPUTER!!!"
        color = (255, 215, 0)
    elif player_score < computer_score:
        msg1 = f"You, {player_name}, scored {player_score}"
        msg2 = "A MERE COMPUTER BEAT YOU. TRY AGAIN!"
        color = (255, 80, 80)
    else:
        msg1 = f"You, {player_name}, scored {player_score}"
        msg2 = "YOU DREW WITH THE COMPUTER, TRY AGAIN!"
        color = (80, 160, 255)

    screen.fill(BG_COLOR)
    draw_text_center(screen, "Final Result", font_mid, HEIGHT // 2 - 80, ACCENT)
    draw_text_center(screen, msg1, font_small, HEIGHT // 2 - 20, TEXT_COLOR)
    draw_text_center(screen, msg2, font_small, HEIGHT // 2 + 20, color)
    draw_text_center(screen, "Press any key to exit", font_small, HEIGHT // 2 + 70, (180, 180, 180))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                waiting = False

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rock · Paper · Scissors — Retro Duel")

    clock = pygame.time.Clock()
    large = pygame.font.SysFont("couriernew", 48, bold=True)
    mid = pygame.font.SysFont("couriernew", 28)
    small = pygame.font.SysFont("couriernew", 20)

    player_name = "PLAYER"  # or ask once at start

    btn_w, btn_h = 200, 70
    gap = 30
    left = (WIDTH - (btn_w * 3 + gap * 2)) // 2
    buttons = [
        Button((left, HEIGHT - 120, btn_w, btn_h), "ROCK", (200, 60, 60), "rock"),
        Button((left + (btn_w + gap), HEIGHT - 120, btn_w, btn_h), "PAPER", (60, 180, 120), "paper"),
        Button((left + 2 * (btn_w + gap), HEIGHT - 120, btn_w, btn_h), "SCISSORS", (60, 140, 200), "scissors"),
    ]

    player_score = 0
    computer_score = 0
    round_result = ""
    show_move = None
    countdown = 0
    pending_player = None

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if show_quit_dialog(screen, mid, small):
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                for b in buttons:
                    if b.is_clicked(pos) and countdown <= 0:
                        pending_player = b.key
                        show_move = None
                        countdown = 1.8
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if show_quit_dialog(screen, mid, small):
                    running = False

        if countdown > 0:
            countdown -= dt
            if countdown <= 0 and pending_player:
                computer_move = get_computer_move()
                result = winner_decider(pending_player, computer_move)
                if result == "player":
                    player_score += 1
                    round_result = "YOU WIN!"
                    if SND_WIN:
                        SND_WIN.play()
                elif result == "computer":
                    computer_score += 1
                    round_result = "COMPUTER WINS"
                    if SND_LOSE:
                        SND_LOSE.play()
                else:
                    round_result = "IT'S A TIE"
                    if SND_TIE:
                        SND_TIE.play()
                show_move = (pending_player, computer_move)
                pending_player = None

        # draw
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, PANEL_COLOR, (20, 20, WIDTH - 40, 110), border_radius=10)
        draw_text_center(screen, "Rock · Paper · Scissors", large, 55, ACCENT)
        draw_text_center(screen, "Retro Duel - Click a choice below", small, 90)

        pygame.draw.rect(screen, PANEL_COLOR, (20, 150, WIDTH - 40, 110), border_radius=10)
        draw_text_center(
            screen,
            f"Player: {player_score}   —   Computer: {computer_score}",
            mid,
            200,
        )

        if countdown > 0:
            secs = max(0, countdown)
            if secs > 1.2:
                num = "3"
            elif secs > 0.6:
                num = "2"
            else:
                num = "1"
            draw_text_center(screen, num, large, 260, ACCENT)
        elif show_move:
            p, c = show_move
            draw_text_center(screen, f"You: {p.upper()}   —   Computer: {c.upper()}", mid, 260, TEXT_COLOR)
            draw_text_center(screen, round_result, large, 305, ACCENT)
        else:
            draw_text_center(screen, "Choose your weapon to begin", mid, 260)

        for b in buttons:
            b.draw(screen, mid)

        footer = small.render("Press ESC to quit — Built with Pygame", True, (150, 150, 150))
        screen.blit(footer, (20, HEIGHT - 30))

        pygame.display.flip()

    show_final_message(screen, mid, small, player_name, player_score, computer_score)
    pygame.quit()

if __name__ == "__main__":
    main()
