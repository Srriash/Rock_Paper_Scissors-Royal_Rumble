import sys
import pygame
import wave
import struct
import math
import os
import json
from pathlib import Path
from rps.logic import get_computer_move, winner_decider
from rps.shared_scores import fetch_leaderboard, fetch_player, upsert_score

# Retro / arcade themed Rock-Paper-Scissors using pygame
WIDTH, HEIGHT = 1100, 720
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
    return []


def load_scores(path):
    return {}


def save_scores(path, data):
    return


def default_record():
    return {'player': 0, 'computer': 0, 'ties': 0, 'games': 0, 'win_streak': 0, 'best_streak': 0, 'matches': 0, 'matches_won': 0, 'matches_lost': 0}


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
    mid_bold = pygame.font.SysFont('couriernew', 28, bold=True)
    small = pygame.font.SysFont('couriernew', 20)

    theme_mode = 'neon'

    themes = {
        'dark': {
            'bg': (18, 18, 30),
            'panel': (26, 26, 40),
            'accent': (255, 168, 0),
            'text': (230, 230, 230),
            'btns': [(200, 60, 60), (60, 180, 120), (60, 140, 200)],
        },
        'neon': {
            'bg': (10, 12, 24),
            'panel': (18, 20, 36),
            'accent': (0, 220, 180),
            'text': (240, 240, 255),
            'btns': [(240, 80, 80), (90, 200, 140), (80, 160, 240)],
        },
    }
    def current_theme():
        return themes.get(theme_mode, themes['dark'])

    bg_color = current_theme()['bg']
    panel_color = current_theme()['panel']
    accent_color = current_theme()['accent']
    text_color = current_theme()['text']

    # Buttons
    btn_w = 240
    btn_h = 70
    gap = 36
    left = (WIDTH - (btn_w * 3 + gap * 2)) // 2

    def build_buttons():
        colors = current_theme()['btns']
        return [
            Button((left, HEIGHT - 140, btn_w, btn_h), 'ROCK', colors[0], 'rock'),
            Button((left + (btn_w + gap), HEIGHT - 140, btn_w, btn_h), 'PAPER', colors[1], 'paper'),
            Button((left + 2 * (btn_w + gap), HEIGHT - 140, btn_w, btn_h), 'SCISSORS', colors[2], 'scissors'),
        ]

    buttons = build_buttons()

    player_score = 0
    computer_score = 0
    current_ties = 0
    current_games = 0
    win_streak = 0
    best_streak = 0
    round_result = ''
    show_move = None
    countdown = 0
    anim_timer = 0
    pending_player = None
    state = 'enter_name'
    player_name = ''
    confirm_user_name = None
    is_new_user = False
    music_loaded = False
    music_playing = False
    sfx_enabled = True  # always on
    music_enabled = True
    best_of_goal = 3
    difficulty_modes = ['random']
    difficulty_idx = 0
    last_player_move = None
    option_rects = []
    matches_won = 0
    matches_lost = 0
    match_in_progress = False
    match_winner_announced = False
    last_match_winner = ''
    quit_rank_note = ''
    remote_leaderboard = []

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

    asset_dir = Path(__file__).resolve().parents[2] / "assets" / "audio"
    asset_dir.mkdir(parents=True, exist_ok=True)
    dramatic_path = asset_dir / 'sfx_dramatic.wav'
    click_path = asset_dir / 'sfx_click.wav'
    win_path = asset_dir / 'sfx_win.wav'
    # If you have Alan Walker PS5 Fortnite track, drop it under assets/audio with this name:
    # Preferred track: drop "lotr_battle.mp3" (or any MP3 with 'lotr' in the name) in this folder to share the same music with others.
    def find_lotr_track():
        mp3s = [f for f in os.listdir(asset_dir) if f.lower().endswith('.mp3')]
        for name in mp3s:
            if 'lotr' in name.lower() or 'lord' in name.lower():
                return asset_dir / name
        return asset_dir / 'lotr_battle.mp3'

    music_preferred = find_lotr_track()
    if os.path.exists(music_preferred):
        music_path = music_preferred
    else:
        music_path = asset_dir / 'bg_battle.wav'
    if not os.path.exists(dramatic_path):
        try:
            asset_dir.mkdir(parents=True, exist_ok=True)
            make_sine_wav(str(dramatic_path), freq=120.0, duration=0.8, volume=0.9)
        except Exception:
            pass
    if not os.path.exists(click_path):
        try:
            asset_dir.mkdir(parents=True, exist_ok=True)
            make_sine_wav(str(click_path), freq=880.0, duration=0.06, volume=0.5)
        except Exception:
            pass
    if not os.path.exists(win_path):
        try:
            asset_dir.mkdir(parents=True, exist_ok=True)
            make_sine_wav(str(win_path), freq=660.0, duration=0.18, volume=0.6)
        except Exception:
            pass
    if not os.path.exists(music_path):
        try:
            asset_dir.mkdir(parents=True, exist_ok=True)
            make_battle_music(str(music_path))
        except Exception:
            pass

    try:
        sfx_dramatic = pygame.mixer.Sound(str(dramatic_path))
        sfx_click = pygame.mixer.Sound(str(click_path))
        sfx_win = pygame.mixer.Sound(str(win_path))
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
        if music_enabled and music_loaded and not music_playing and pygame.mixer.get_init():
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

    def choose_computer_move():
        return get_computer_move()

    def persist_scores():
        return

    def refresh_remote_leaderboard():
        nonlocal remote_leaderboard
        remote_leaderboard = fetch_leaderboard(10)

    running = True
    refresh_remote_leaderboard()
    while running:
        dt = clock.tick(60) / 1000.0
        panel_w_pre = min(760, WIDTH - 100)
        panel_h_pre = 300
        panel_x_pre = (WIDTH - panel_w_pre) // 2
        panel_y_pre = (HEIGHT - panel_h_pre) // 2
        option_rects = [
            pygame.Rect(panel_x_pre + 60, panel_y_pre + panel_h_pre - 110, 180, 64),
            pygame.Rect(panel_x_pre + 60 + 190, panel_y_pre + panel_h_pre - 110, 180, 64),
            pygame.Rect(panel_x_pre + 60 + 190*2, panel_y_pre + panel_h_pre - 110, 180, 64),
        ]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # trigger quit confirm
                if state == 'playing':
                    state = 'confirm_quit'
                    if sfx_dramatic and sfx_enabled:
                        sfx_dramatic.play()
                else:
                    stop_music()
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if state == 'enter_name':
                    # ignore clicks while entering name
                    pass
                elif state == 'tutorial':
                    if confirm_rect.collidepoint(pos):
                        state = 'best_of_choice'
                elif state == 'best_of_choice':
                    for idx, rect in enumerate(option_rects):
                        if rect.collidepoint(pos):
                            best_of_goal = [3,5,10][idx]
                            state = 'playing'
                            start_music()
                            break
                elif state == 'post_match_choice':
                    for idx, rect in enumerate(option_rects):
                        if rect.collidepoint(pos):
                            best_of_goal = [3,5,10][idx]
                            state = 'playing'
                            start_music()
                            break
                elif state == 'confirm_identity':
                    if confirm_rect.collidepoint(pos):
                        rec = fetch_player(confirm_user_name)
                        player_score = 0
                        computer_score = 0
                        current_ties = 0
                        current_games = 0
                        win_streak = 0
                        best_streak = int(rec.get('best_streak', 0)) if rec else 0
                        matches_won = int(rec.get('matches_won', 0)) if rec else 0
                        matches_lost = int(rec.get('matches_lost', 0)) if rec else 0
                        player_name = confirm_user_name or player_name
                        confirm_user_name = None
                        is_new_user = False
                        state = 'best_of_choice'
                    elif cancel_rect.collidepoint(pos):
                        # try another name
                        player_name = ''
                        confirm_user_name = None
                        state = 'enter_name'
                elif state == 'confirm_quit':
                    # check confirm buttons (confirm_rect/cancel_rect defined in draw)
                    if confirm_rect.collidepoint(pos):
                        if sfx_click and sfx_enabled:
                            sfx_click.play()
                        # build rank note based on remote leaderboard
                        leaderboard = sorted(remote_leaderboard, key=lambda rec: rec.get('best_streak',0), reverse=True)
                        rank = None
                        if player_name:
                            for idx_lb, rec in enumerate(leaderboard):
                                if rec.get('name') == player_name:
                                    rank = idx_lb
                                    break
                        if rank == 0:
                            quit_rank_note = 'You are #1. Play to maintain the top spot.'
                        elif rank is not None:
                            quit_rank_note = f'You are #{rank+1} on the leaderboard. Play more to reach the top.'
                        else:
                            top_streak = leaderboard[0].get('best_streak',0) if leaderboard else 0
                            quit_rank_note = f'Top streak is {top_streak}. Climb the board!'
                        if match_in_progress:
                            quit_rank_note = 'Match not recorded. ' + quit_rank_note
                        state = 'quit_stats'
                    elif cancel_rect.collidepoint(pos):
                        if sfx_click and sfx_enabled:
                            sfx_click.play()
                        state = 'playing'
                elif state == 'quit_stats':
                    if confirm_rect.collidepoint(pos):
                        if sfx_click and sfx_enabled:
                            sfx_click.play()
                        # If quitting mid-match, clear in-progress round scores
                        if match_in_progress:
                            player_score = 0
                            computer_score = 0
                            current_ties = 0
                            current_games = 0
                            match_in_progress = False
                            show_move = None
                            round_result = ''
                            persist_scores()
                        stop_music()
                        running = False
                    elif cancel_rect.collidepoint(pos):
                        if sfx_click and sfx_enabled:
                            sfx_click.play()
                        state = 'playing'
                elif state == 'playing':
                    for b in buttons:
                        if b.is_clicked(pos) and countdown <= 0:
                            if sfx_click and sfx_enabled:
                                sfx_click.play()
                            # start countdown animation
                            player_move = b.key
                            show_move = None
                            countdown = 1.8  # seconds for 3-2-1
                            anim_timer = 0
                            pending_player = player_move
                            last_player_move = player_move
            elif event.type == pygame.KEYDOWN:
                if state == 'enter_name':
                    if event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        chosen = player_name.strip() or 'PLAYER'
                        # if user exists remotely, confirm identity; else create fresh
                        existing = fetch_player(chosen)
                        if existing:
                            confirm_user_name = chosen
                            state = 'confirm_identity'
                        else:
                            player_name = chosen
                            player_score = 0
                            computer_score = 0
                            current_ties = 0
                            current_games = 0
                            win_streak = 0
                            best_streak = 0
                            matches_won = 0
                            matches_lost = 0
                            is_new_user = True
                            refresh_remote_leaderboard()
                            state = 'tutorial'
                    else:
                        if len(player_name) < 20 and event.unicode.isprintable():
                            player_name += event.unicode
                else:
                    if event.key == pygame.K_ESCAPE:
                        if state in ('best_of_choice', 'post_match_choice'):
                            state = 'playing'
                            start_music()
                        elif state == 'playing':
                            state = 'confirm_quit'
                            if sfx_dramatic and sfx_enabled:
                                sfx_dramatic.play()
                        elif state == 'confirm_quit':
                            stop_music()
                            running = False
                        elif state == 'quit_stats':
                            state = 'playing'
                        elif state == 'confirm_quit':
                            stop_music()
                            running = False
                        else:
                            stop_music()
                            running = False
                    elif state == 'tutorial':
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            state = 'best_of_choice'
                    elif state == 'best_of_choice':
                        if event.key in (pygame.K_3, pygame.K_5, pygame.K_0, pygame.K_KP3, pygame.K_KP5, pygame.K_KP0):
                            key_to_goal = {pygame.K_3:3, pygame.K_KP3:3, pygame.K_5:5, pygame.K_KP5:5, pygame.K_0:10, pygame.K_KP0:10}
                            best_of_goal = key_to_goal.get(event.key, best_of_goal)
                            state = 'playing'
                            start_music()
                    elif state == 'post_match_choice':
                        if event.key in (pygame.K_3, pygame.K_5, pygame.K_0, pygame.K_KP3, pygame.K_KP5, pygame.K_KP0):
                            key_to_goal = {pygame.K_3:3, pygame.K_KP3:3, pygame.K_5:5, pygame.K_KP5:5, pygame.K_0:10, pygame.K_KP0:10}
                            best_of_goal = key_to_goal.get(event.key, best_of_goal)
                            state = 'playing'
                        elif event.key == pygame.K_q:
                            stop_music()
                            running = False
                    elif state == 'playing' and countdown <= 0:
                        if event.key in (pygame.K_r, pygame.K_p, pygame.K_s):
                            move_key = {pygame.K_r: 'rock', pygame.K_p: 'paper', pygame.K_s: 'scissors'}[event.key]
                            if sfx_click and sfx_enabled:
                                sfx_click.play()
                            show_move = None
                            countdown = 1.8
                            anim_timer = 0
                            pending_player = move_key
                            last_player_move = move_key
                        elif event.key == pygame.K_m:
                            music_enabled = not music_enabled
                            if music_enabled:
                                start_music()
                            else:
                                stop_music()
                    elif state == 'post_match_choice':
                        if event.key in (pygame.K_3, pygame.K_5, pygame.K_0, pygame.K_KP3, pygame.K_KP5, pygame.K_KP0):
                            key_to_goal = {pygame.K_3:3, pygame.K_KP3:3, pygame.K_5:5, pygame.K_KP5:5, pygame.K_0:10, pygame.K_KP0:10}
                            best_of_goal = key_to_goal.get(event.key, best_of_goal)
                            state = 'playing'

        if countdown > 0:
            countdown -= dt
            anim_timer += dt
            # when countdown finishes, decide
            if countdown <= 0 and pending_player:
                computer_move = choose_computer_move()
                result = winner_decider(pending_player, computer_move)
                if result == 'player':
                    player_score += 1
                    round_result = 'YOU WIN!'
                    if sfx_win and sfx_enabled:
                        sfx_win.play()
                elif result == 'computer':
                    computer_score += 1
                    round_result = 'COMPUTER WINS'
                else:
                    current_ties += 1
                    round_result = "IT'S A TIE"
                current_games += 1
                match_in_progress = True
                show_move = (pending_player, computer_move)
                if player_score >= best_of_goal or computer_score >= best_of_goal:
                    match_in_progress = False
                    match_winner_announced = True
                    if player_score > computer_score:
                        matches_won += 1
                        round_result = f'MATCH WINNER! Race to {best_of_goal}'
                        last_match_winner = 'You won the match!'
                        win_streak += 1  # match win streak
                        best_streak = max(best_streak, win_streak)
                    else:
                        matches_lost += 1
                        round_result = f'COMPUTER TAKES THE MATCH ({best_of_goal})'
                        last_match_winner = 'Computer won the match.'
                        win_streak = 0  # reset match streak on loss
                    # reset round scores for next match
                    player_score = 0
                    computer_score = 0
                    current_ties = 0
                    current_games = 0
                    show_move = None
                    total_played = matches_won + matches_lost
                    win_pct = (matches_won / total_played * 100.0) if total_played else 0.0
                    upsert_score(player_name or 'PLAYER', matches_won, matches_lost, best_streak, win_pct=win_pct)
                    refresh_remote_leaderboard()
                    state = 'post_match_choice'
                persist_scores()

        # draw
        # refresh theme colors (for dynamic toggle)
        bg_color = current_theme()['bg']
        panel_color = current_theme()['panel']
        accent_color = current_theme()['accent']
        text_color = current_theme()['text']

        screen.fill(bg_color)
        # header panel
        pygame.draw.rect(screen, panel_color, (20, 20, WIDTH - 40, 170), border_radius=10)
        draw_text_center(screen, 'Rock - Paper - Scissors', large, 100, accent_color)
        draw_text_center(screen, 'ROYAL RUMBLE', mid_bold, 140, (220, 70, 70))
        if state == 'enter_name':
            draw_text_center(screen, 'Enter your name and press Enter', small, HEIGHT // 2 - 40, text_color)

        # Stats and score panels (hide until onboarding is done)
        if state not in ('enter_name','tutorial','best_of_choice'):
            stats_rect = pygame.Rect(20, 200, WIDTH - 40, 110)
            pygame.draw.rect(screen, panel_color, stats_rect, border_radius=10)
            stats_padding = 24
            total_played = matches_won + matches_lost
            win_rate = (matches_won / total_played * 100) if total_played else 0
            stats_lines = [
                f'Matches: {total_played}    Win%: {win_rate:.0f}%',
                f'Streak: {win_streak} (Best {best_streak})    Race to {best_of_goal}',
            ]
            for i, line in enumerate(stats_lines):
                txt = small.render(line, True, text_color)
                screen.blit(txt, (stats_rect.left + stats_padding, stats_rect.top + 16 + i * 22))

            leaderboard = [(rec.get('name','?'), rec) for rec in remote_leaderboard][:3]
            lb_title = small.render('Leaderboard (streaks)', True, accent_color)
            lb_x = stats_rect.right - stats_padding - lb_title.get_width()
            lb_y = stats_rect.top + 12
            screen.blit(lb_title, (lb_x, lb_y))
            for idx, (name, rec) in enumerate(leaderboard):
                line = f"{idx+1}. {name}: {rec.get('best_streak',0)}"
                txt = small.render(line, True, text_color)
                screen.blit(txt, (lb_x, lb_y + 18 + idx * 18))

            pygame.draw.rect(screen, panel_color, (20, 330, WIDTH - 40, 170), border_radius=10)
            draw_text_center(screen, f'Player: {player_score}   -   Computer: {computer_score}', mid, 370, text_color)
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
                draw_text_center(screen, num, large, 430, accent_color)
            elif show_move:
                # display moves
                p, c = show_move
                draw_text_center(screen, f'You: {p.upper()}   -   Computer: {c.upper()}', mid, 410, text_color)
                # animate result glow
                glow = 40 + int(40 * abs(math.sin(anim_timer * 4)))
                glow_color = (min(255, accent_color[0] + glow//2), min(255, accent_color[1] + glow//3), min(255, accent_color[2] + glow//4))
                draw_text_center(screen, round_result, large, 450, glow_color)
            else:
                draw_text_center(screen, 'Choose your weapon to begin', mid, 430, text_color)

        # If we're on the enter_name screen show input box with blinking cursor
        if state == 'enter_name':
            box_w, box_h = 520, 60
            box_rect = pygame.Rect(WIDTH//2 - box_w//2, HEIGHT//2 + 10, box_w, box_h)
            pygame.draw.rect(screen, panel_color, box_rect, border_radius=8)
            blink_on = (pygame.time.get_ticks() // 400) % 2 == 0
            display_name = player_name
            if blink_on:
                display_name += '|'
            name_txt = mid.render(display_name, True, text_color)
            screen.blit(name_txt, (WIDTH//2 - name_txt.get_width()//2, box_rect.y + (box_h - name_txt.get_height())//2))

        # draw buttons (only in playing state)
        if state == 'playing':
            for b in buttons:
                b.draw(screen, mid)

        # overlays
        confirm_rect = pygame.Rect(0,0,0,0)
        cancel_rect = pygame.Rect(0,0,0,0)
        if state == 'tutorial':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            screen.blit(overlay, (0,0))
            panel_w = min(700, WIDTH - 80)
            panel_h = 420
            panel_x = (WIDTH - panel_w) // 2
            panel_y = (HEIGHT - panel_h) // 2
            panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            pygame.draw.rect(screen, panel_color, panel_rect, border_radius=12)

            wrap_width = panel_w - 60
            y = panel_rect.top + 30
            y = draw_wrapped_center(screen, 'Welcome to Rock-Paper-Scissors', mid_bold, y, wrap_width, accent_color, line_gap=6) + 8
            tutorial_lines = [
                'Play with keys R / P / S or click the icons.',
                'Match length: best of 3, 5, or 10 (choose next).',
                'Music: press M to toggle on/off.',
                'Stats: win%, streaks, and leaderboard show top streaks (top 3).',
            ]
            for line in tutorial_lines:
                y = draw_wrapped_center(screen, line, small, y, wrap_width, text_color, line_gap=4) + 4
            y += 20

            btn_w = 200
            btn_h = 54
            btn_x = panel_rect.centerx - btn_w // 2
            btn_y = panel_rect.bottom - btn_h - 24
            confirm_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            cancel_rect = pygame.Rect(0,0,0,0)
            pygame.draw.rect(screen, (80,180,90), confirm_rect, border_radius=8)
            confirm_txt = mid.render('Continue', True, (0,0,0))
            screen.blit(confirm_txt, confirm_txt.get_rect(center=confirm_rect.center))

        elif state == 'best_of_choice':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            screen.blit(overlay, (0,0))
            panel_w = panel_w_pre
            panel_h = panel_h_pre
            panel_x = panel_x_pre
            panel_y = panel_y_pre
            panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            pygame.draw.rect(screen, panel_color, panel_rect, border_radius=12)

            wrap_width = panel_w - 60
            y = panel_rect.top + 34
            y = draw_wrapped_center(screen, 'Choose match length (best of)', mid_bold, y, wrap_width, accent_color, line_gap=6) + 14
            labels = ['Best of 3', 'Best of 5', 'Best of 10']
            for rect, label in zip(option_rects, labels):
                pygame.draw.rect(screen, accent_color, rect, border_radius=10)
                lbl = mid.render(label, True, (0,0,0))
                screen.blit(lbl, lbl.get_rect(center=rect.center))

        elif state == 'confirm_identity':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            screen.blit(overlay, (0,0))
            panel_w = min(620, WIDTH - 80)
            panel_h = 240
            panel_x = (WIDTH - panel_w) // 2
            panel_y = (HEIGHT - panel_h) // 2
            panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            pygame.draw.rect(screen, panel_color, panel_rect, border_radius=12)

            wrap_width = panel_w - 60
            y = panel_rect.top + 32
            y = draw_wrapped_center(screen, 'Username already exists', mid_bold, y, wrap_width, accent_color, line_gap=6) + 10
            existing_label = confirm_user_name or 'this user'
            y = draw_wrapped_center(screen, f'Are you "{existing_label}"?', mid, y, wrap_width, text_color, line_gap=4) + 18

            btn_w = (panel_w - 3 * 30) // 2
            btn_h = 54
            btn_y = panel_rect.bottom - btn_h - 24
            confirm_rect = pygame.Rect(panel_rect.left + 30, btn_y, btn_w, btn_h)
            cancel_rect = pygame.Rect(panel_rect.right - btn_w - 30, btn_y, btn_w, btn_h)
            pygame.draw.rect(screen, (80,180,90), confirm_rect, border_radius=8)
            pygame.draw.rect(screen, (180,60,60), cancel_rect, border_radius=8)
            confirm_txt = mid.render('Yes, that is me', True, (0,0,0))
            cancel_txt = mid.render('Try another', True, (0,0,0))
            screen.blit(confirm_txt, confirm_txt.get_rect(center=confirm_rect.center))
            screen.blit(cancel_txt, cancel_txt.get_rect(center=cancel_rect.center))

        elif state == 'post_match_choice':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            screen.blit(overlay, (0,0))
            panel_w = min(760, WIDTH - 80)
            panel_h = 300
            panel_x = (WIDTH - panel_w) // 2
            panel_y = (HEIGHT - panel_h) // 2
            panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            pygame.draw.rect(screen, panel_color, panel_rect, border_radius=12)

            wrap_width = panel_w - 60
            y = panel_rect.top + 32
            y = draw_wrapped_center(screen, last_match_winner, mid_bold, y, wrap_width, accent_color, line_gap=6) + 10
            y = draw_wrapped_center(screen, 'Play another match?', mid, y, wrap_width, text_color, line_gap=4) + 16

            labels = ['Best of 3', 'Best of 5', 'Best of 10']
            total_btn_w = 160 * 3 + 40 * 2
            start_x = panel_rect.centerx - total_btn_w // 2
            option_rects = [
                pygame.Rect(start_x, panel_rect.bottom - 120, 160, 60),
                pygame.Rect(start_x + 200, panel_rect.bottom - 120, 160, 60),
                pygame.Rect(start_x + 400, panel_rect.bottom - 120, 160, 60),
            ]
            for rect, label in zip(option_rects, labels):
                pygame.draw.rect(screen, accent_color, rect, border_radius=10)
                lbl = mid.render(label, True, (0,0,0))
                screen.blit(lbl, lbl.get_rect(center=rect.center))

        elif state == 'confirm_quit':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            screen.blit(overlay, (0,0))
            panel_w = min(680, WIDTH - 80)
            panel_h = 460
            panel_x = (WIDTH - panel_w) // 2
            panel_y = (HEIGHT - panel_h) // 2
            panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            pygame.draw.rect(screen, panel_color, panel_rect, border_radius=12)

            wrap_width = panel_w - 60
            y = panel_rect.top + 30
            # Motivation based on leaderboard standing for existing users
            leaderboard = sorted(remote_leaderboard, key=lambda rec: rec.get('best_streak',0), reverse=True)
            if player_name:
                rank = None
                for idx_lb, rec in enumerate(leaderboard):
                    if rec.get('name') == player_name:
                        rank = idx_lb
                        break
                top_streak = leaderboard[0].get('best_streak', 0) if leaderboard else 0
                if rank == 0:
                    msg = 'You are #1. Keep the crown!'
                elif rank is not None:
                    msg = f'You are #{rank+1}. Top streak is {top_streak}. Climb to #1!'
                else:
                    msg = f'Top streak is {top_streak}. Play to get on the board!'
                y = draw_wrapped_center(screen, msg, mid, y, wrap_width, (200, 200, 255), line_gap=6) + 10

            summary_msgs = build_summary_msgs(player_name or 'PLAYER', player_score, computer_score)
            for text, col in summary_msgs:
                y = draw_wrapped_center(screen, text, mid, y, wrap_width, col, line_gap=8) + 6
            y += 20

            # Stats snapshot
            if quit_rank_note:
                y = draw_wrapped_center(screen, quit_rank_note, mid, y, wrap_width, (200, 200, 255), line_gap=6) + 10

            total_played = matches_won + matches_lost
            stats_block = [
                f"Matches: {total_played} (W {matches_won} / L {matches_lost})",
                f"Current streak: {win_streak}   Best streak: {best_streak}",
                f"Best-of target: {best_of_goal}",
            ]
            for line in stats_block:
                y = draw_wrapped_center(screen, line, small, y, wrap_width, text_color, line_gap=4) + 4
            y += 20

            btn_w = (panel_w - 3 * 30) // 2
            btn_h = 54
            btn_y = max(y + 20, panel_rect.bottom - btn_h - 20)
            confirm_rect = pygame.Rect(panel_rect.left + 30, btn_y, btn_w, btn_h)
            cancel_rect = pygame.Rect(panel_rect.right - btn_w - 30, btn_y, btn_w, btn_h)
            pygame.draw.rect(screen, (180,60,60), confirm_rect, border_radius=8)
            pygame.draw.rect(screen, (80,180,90), cancel_rect, border_radius=8)
            confirm_txt = mid.render('Quit', True, (0,0,0))
            cancel_txt = mid.render('Cancel', True, (0,0,0))
            screen.blit(confirm_txt, confirm_txt.get_rect(center=confirm_rect.center))
            screen.blit(cancel_txt, cancel_txt.get_rect(center=cancel_rect.center))

        elif state == 'quit_stats':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            screen.blit(overlay, (0,0))
            panel_w = min(760, WIDTH - 80)
            panel_h = 520
            panel_x = (WIDTH - panel_w) // 2
            panel_y = (HEIGHT - panel_h) // 2
            panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            pygame.draw.rect(screen, panel_color, panel_rect, border_radius=12)

            wrap_width = panel_w - 60
            y = panel_rect.top + 28
            y = draw_wrapped_center(screen, 'Leaderboard (top streaks)', mid, y, wrap_width, accent_color, line_gap=6) + 10

            leaderboard = [(rec.get('name','?'), rec) for rec in remote_leaderboard][:10]
            for idx, (name, rec) in enumerate(leaderboard):
                line = f"{idx+1}. {name}: {rec.get('best_streak',0)}"
                y = draw_wrapped_center(screen, line, mid, y, wrap_width, text_color, line_gap=4) + 4
            y += 14

            btn_w = (panel_w - 3 * 30) // 2
            btn_h = 54
            btn_y = max(y + 16, panel_rect.bottom - btn_h - 18)
            confirm_rect = pygame.Rect(panel_rect.left + 30, btn_y, btn_w, btn_h)
            cancel_rect = pygame.Rect(panel_rect.right - btn_w - 30, btn_y, btn_w, btn_h)
            pygame.draw.rect(screen, (180,60,60), confirm_rect, border_radius=8)
            pygame.draw.rect(screen, (80,180,90), cancel_rect, border_radius=8)
            confirm_txt = mid.render('Quit', True, (0,0,0))
            cancel_txt = mid.render('Cancel', True, (0,0,0))
            screen.blit(confirm_txt, confirm_txt.get_rect(center=confirm_rect.center))
            screen.blit(cancel_txt, cancel_txt.get_rect(center=cancel_rect.center))

        # footer
        footer_text = f"ESC: quit  |  R/P/S: play  |  M: music {'on' if music_enabled else 'off'}  |  3/5/0: best-of"
        footer = small.render(footer_text, True, (150, 150, 150))
        screen.blit(footer, (20, HEIGHT - 30))

        pygame.display.flip()

    stop_music()
    pygame.quit()


if __name__ == '__main__':
    main()
#ashwin created this @AshAs org
