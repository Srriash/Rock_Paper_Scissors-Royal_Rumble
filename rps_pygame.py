import sys
import random
import pygame
import wave
import struct
import math
import os
from rps_logic import get_computer_move, winner_decider

# Retro / arcade themed Rock-Paper-Scissors using pygame
WIDTH, HEIGHT = 800, 480
BG_COLOR = (18, 18, 30)
PANEL_COLOR = (26, 26, 40)
ACCENT = (255, 168, 0)
TEXT_COLOR = (230, 230, 230)


class Button:
    def __init__(self, rect, text, color, key):
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


def wrap_lines(text, font, max_width):
    """Wrap a string into multiple lines so each rendered line stays within max_width."""
    words = text.split()
    lines = []
    current = ''
    for w in words:
        test = w if current == '' else current + ' ' + w
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def draw_wrapped_center(surf, text, font, start_y, max_width, color=TEXT_COLOR, line_gap=6):
    """Draw multi-line wrapped text centered horizontally starting at start_y."""
    lines = wrap_lines(text, font, max_width)
    y = start_y
    for ln in lines:
        draw_text_center(surf, ln, font, y, color)
        y += font.get_linesize() + line_gap
    return y


def build_summary_msgs(player_name, player_score, computer_score):
    if player_score == computer_score == 0:
        return [("Just try the game once and I am sure you will love it!!", (255, 80, 80))]
    if player_score > computer_score:
        return [
            (f'You, {player_name}, scored {player_score} and the computer scored {computer_score}', (230, 230, 230)),
            ('YOU BEAT THE ALMIGHTY COMPUTER!!!', (255, 200, 50)),
            ('Thank you for playing the game, see you soon!!', (200, 200, 200)),
        ]
    if player_score < computer_score:
        return [
            (f'You, {player_name}, scored {player_score} and the computer scored {computer_score}', (230, 230, 230)),
            ('A MERE COMPUTER BEAT YOU, HUMAN INTELLIGENCE IS ON THE NOSE DIVE. TRY AGAIN AND PROVE ME WRONG', (255, 80, 80)),
        ]
    return [
        (f'You, {player_name}, scored {player_score} and the computer scored {computer_score}', (230, 230, 230)),
        ('YOU DREW WITH THE COMPUTER, TRY AGAIN AND BEAT IT ONCE FOR ALL', (80, 160, 255)),
    ]


def main():
    pygame.init()
    # try to initialize mixer
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
    except Exception:
        pass
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Rock - Paper - Scissors - Retro Duel')

    clock = pygame.time.Clock()
    large = pygame.font.SysFont('couriernew', 48, bold=True)
    mid = pygame.font.SysFont('couriernew', 28)
    small = pygame.font.SysFont('couriernew', 20)

    # Buttons
    btn_w = 200
    btn_h = 70
    gap = 30
    left = (WIDTH - (btn_w * 3 + gap * 2)) // 2

    buttons = [
        Button((left, HEIGHT - 120, btn_w, btn_h), 'ROCK', (200, 60, 60), 'rock'),
        Button((left + (btn_w + gap), HEIGHT - 120, btn_w, btn_h), 'PAPER', (60, 180, 120), 'paper'),
        Button((left + 2 * (btn_w + gap), HEIGHT - 120, btn_w, btn_h), 'SCISSORS', (60, 140, 200), 'scissors'),
    ]

    player_score = 0
    computer_score = 0
    round_result = ''
    show_move = None
    countdown = 0
    anim_timer = 0
    pending_player = None
    state = 'enter_name'
    player_name = ''
    music_loaded = False
    music_playing = False

    # prepare simple sound effects (generate small WAV files)
    def make_sine_wav(path, freq=440.0, duration=0.5, volume=0.5):
        framerate = 44100
        amp = int(32767 * volume)
        nframes = int(duration * framerate)
        with wave.open(path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(framerate)
            for i in range(nframes):
                t = float(i) / framerate
                val = int(amp * math.sin(2 * math.pi * freq * t))
                data = struct.pack('<h', val)
                wf.writeframesraw(data)

    def make_battle_music(path):
        # create a short looping chiptune-style track
        framerate = 44100
        duration = 6.0
        amp = 26000
        nframes = int(duration * framerate)
        with wave.open(path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(framerate)
            for i in range(nframes):
                t = float(i) / framerate
                bass = math.sin(2 * math.pi * 110 * t) * 0.55
                lead = math.sin(2 * math.pi * 330 * t + math.sin(2 * math.pi * 2 * t) * 2.5) * 0.35
                beat = (1 if (i // (framerate // 2)) % 2 == 0 else -1) * 0.15
                val = int(amp * (bass + lead + beat))
                data = struct.pack('<h', max(-32768, min(32767, val)))
                wf.writeframesraw(data)

    asset_dir = os.path.dirname(__file__)
    dramatic_path = os.path.join(asset_dir, 'sfx_dramatic.wav')
    click_path = os.path.join(asset_dir, 'sfx_click.wav')
    win_path = os.path.join(asset_dir, 'sfx_win.wav')
    # If you have Alan Walker PS5 Fortnite track, drop it next to this file with this name:
    # Preferred track: drop "lotr_battle.mp3" (or any MP3 with 'lotr' in the name) in this folder to share the same music with others.
    def find_lotr_track():
        mp3s = [f for f in os.listdir(asset_dir) if f.lower().endswith('.mp3')]
        for name in mp3s:
            if 'lotr' in name.lower() or 'lord' in name.lower():
                return os.path.join(asset_dir, name)
        return os.path.join(asset_dir, 'lotr_battle.mp3')

    music_preferred = find_lotr_track()
    if os.path.exists(music_preferred):
        music_path = music_preferred
    else:
        music_path = os.path.join(asset_dir, 'bg_battle.wav')
    if not os.path.exists(dramatic_path):
        try:
            make_sine_wav(dramatic_path, freq=120.0, duration=0.8, volume=0.9)
        except Exception:
            pass
    if not os.path.exists(click_path):
        try:
            make_sine_wav(click_path, freq=880.0, duration=0.06, volume=0.5)
        except Exception:
            pass
    if not os.path.exists(win_path):
        try:
            make_sine_wav(win_path, freq=660.0, duration=0.18, volume=0.6)
        except Exception:
            pass
    if not os.path.exists(music_path):
        try:
            make_battle_music(music_path)
        except Exception:
            pass

    try:
        sfx_dramatic = pygame.mixer.Sound(dramatic_path)
        sfx_click = pygame.mixer.Sound(click_path)
        sfx_win = pygame.mixer.Sound(win_path)
    except Exception:
        sfx_dramatic = sfx_click = sfx_win = None

    if pygame.mixer.get_init():
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.35)
            music_loaded = True
        except Exception:
            music_loaded = False

    def start_music():
        nonlocal music_playing
        if music_loaded and not music_playing and pygame.mixer.get_init():
            try:
                pygame.mixer.music.play(-1)
                music_playing = True
            except Exception:
                music_playing = False

    def stop_music():
        nonlocal music_playing
        if music_playing and pygame.mixer.get_init():
            try:
                pygame.mixer.music.stop()
            finally:
                music_playing = False

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # trigger quit confirm
                if state == 'playing':
                    state = 'confirm_quit'
                    if sfx_dramatic:
                        sfx_dramatic.play()
                else:
                    stop_music()
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if state == 'enter_name':
                    # ignore clicks while entering name
                    pass
                elif state == 'confirm_quit':
                    # check confirm buttons (confirm_rect/cancel_rect defined in draw)
                    if confirm_rect.collidepoint(pos):
                        if sfx_click:
                            sfx_click.play()
                        stop_music()
                        running = False
                    elif cancel_rect.collidepoint(pos):
                        if sfx_click:
                            sfx_click.play()
                        state = 'playing'
                elif state == 'playing':
                    for b in buttons:
                        if b.is_clicked(pos) and countdown <= 0:
                            if sfx_click:
                                sfx_click.play()
                            # start countdown animation
                            player_move = b.key
                            show_move = None
                            countdown = 1.8  # seconds for 3-2-1
                            anim_timer = 0
                            pending_player = player_move
            elif event.type == pygame.KEYDOWN:
                if state == 'enter_name':
                    if event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        if player_name.strip() == '':
                            player_name = 'PLAYER'
                        state = 'playing'
                        start_music()
                    else:
                        if len(player_name) < 20 and event.unicode.isprintable():
                            player_name += event.unicode
                else:
                    if event.key == pygame.K_ESCAPE:
                        if state == 'playing':
                            state = 'confirm_quit'
                            if sfx_dramatic:
                                sfx_dramatic.play()
                        elif state == 'confirm_quit':
                            state = 'playing'
                        else:
                            stop_music()
                            running = False

        if countdown > 0:
            countdown -= dt
            anim_timer += dt
            # when countdown finishes, decide
            if countdown <= 0 and pending_player:
                computer_move = get_computer_move()
                result = winner_decider(pending_player, computer_move)
                if result == 'player':
                    player_score += 1
                    round_result = 'YOU WIN!'
                    if sfx_win:
                        sfx_win.play()
                elif result == 'computer':
                    computer_score += 1
                    round_result = 'COMPUTER WINS'
                else:
                    round_result = "IT'S A TIE"
                show_move = (pending_player, computer_move)

        # draw
        screen.fill(BG_COLOR)
        # header panel
        pygame.draw.rect(screen, PANEL_COLOR, (20, 20, WIDTH - 40, 110), border_radius=10)
        draw_text_center(screen, 'Rock - Paper - Scissors', large, 55, ACCENT)
        if state == 'enter_name':
            draw_text_center(screen, 'Enter your name and press Enter', small, 90)
        else:
            draw_text_center(screen, 'Retro Duel - Click a choice below', small, 90)

        # Score panel
        pygame.draw.rect(screen, PANEL_COLOR, (20, 150, WIDTH - 40, 110), border_radius=10)
        draw_text_center(screen, f'Player: {player_score}   -   Computer: {computer_score}', mid, 200)
        if countdown > 0:
            # show animated 3-2-1
            # compute which number to show
            secs = max(0, countdown)
            if secs > 1.2:
                num = '3'
            elif secs > 0.6:
                num = '2'
            else:
                num = '1'
            draw_text_center(screen, num, large, 260, ACCENT)
        elif show_move:
            # display moves
            p, c = show_move
            draw_text_center(screen, f'You: {p.upper()}   -   Computer: {c.upper()}', mid, 260, TEXT_COLOR)
            draw_text_center(screen, round_result, large, 305, ACCENT)
        else:
            draw_text_center(screen, 'Choose your weapon to begin', mid, 260)

        # If we're on the enter_name screen show input box with blinking cursor
        if state == 'enter_name':
            pygame.draw.rect(screen, PANEL_COLOR, (WIDTH//2 - 260, 300, 520, 60), border_radius=8)
            blink_on = (pygame.time.get_ticks() // 400) % 2 == 0
            display_name = player_name or 'PLAYER'
            if blink_on:
                display_name += '|'
            name_txt = mid.render(display_name, True, TEXT_COLOR)
            screen.blit(name_txt, (WIDTH//2 - name_txt.get_width()//2, 315))

        # draw buttons (only in playing state)
        if state == 'playing':
            for b in buttons:
                b.draw(screen, mid)

        # confirm quit overlay with embedded summary
        confirm_rect = pygame.Rect(0,0,0,0)
        cancel_rect = pygame.Rect(0,0,0,0)
        if state == 'confirm_quit':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            screen.blit(overlay, (0,0))
            panel_w = min(680, WIDTH - 80)
            panel_h = 300
            panel_x = (WIDTH - panel_w) // 2
            panel_y = (HEIGHT - panel_h) // 2
            panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=12)

            wrap_width = panel_w - 60
            y = panel_rect.top + 30
            y = draw_wrapped_center(screen, 'Are you sure you want to quit?', mid, y, wrap_width, ACCENT, line_gap=4) + 6
            summary_msgs = build_summary_msgs(player_name or 'PLAYER', player_score, computer_score)
            for text, col in summary_msgs:
                y = draw_wrapped_center(screen, text, mid, y, wrap_width, col, line_gap=4) + 4
            y = draw_wrapped_center(screen, 'Your progress will be summarized. Exit now?', small, y+6, wrap_width, TEXT_COLOR, line_gap=2) + 10

            btn_w = (panel_w - 3 * 30) // 2
            btn_h = 54
            btn_y = panel_rect.bottom - btn_h - 20
            confirm_rect = pygame.Rect(panel_rect.left + 30, btn_y, btn_w, btn_h)
            cancel_rect = pygame.Rect(panel_rect.right - btn_w - 30, btn_y, btn_w, btn_h)
            pygame.draw.rect(screen, (180,60,60), confirm_rect, border_radius=8)
            pygame.draw.rect(screen, (80,180,90), cancel_rect, border_radius=8)
            confirm_txt = mid.render('Quit', True, (0,0,0))
            cancel_txt = mid.render('Cancel', True, (0,0,0))
            screen.blit(confirm_txt, confirm_txt.get_rect(center=confirm_rect.center))
            screen.blit(cancel_txt, cancel_txt.get_rect(center=cancel_rect.center))

        # footer
        footer = small.render('Press ESC to quit - Built with Pygame', True, (150, 150, 150))
        screen.blit(footer, (20, HEIGHT - 30))

        pygame.display.flip()

    stop_music()
    pygame.quit()


if __name__ == '__main__':
    main()
