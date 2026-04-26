import pygame
import sys
from racer import RacerGame
from ui import Button, draw_text, draw_center_text
from persistence import load_settings, save_settings, load_leaderboard, add_score

pygame.init()

WIDTH = 500
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 3 Racer")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (225, 225, 225)
RED = (255, 0, 0)

font = pygame.font.SysFont("Verdana", 24)
small_font = pygame.font.SysFont("Verdana", 18)
big_font = pygame.font.SysFont("Verdana", 40)

settings = load_settings()


def menu_screen():
    play_btn = Button(170, 220, 160, 50, "Play")
    board_btn = Button(170, 290, 160, 50, "Leaderboard")
    settings_btn = Button(170, 360, 160, 50, "Settings")
    quit_btn = Button(170, 430, 160, 50, "Quit")

    while True:
        screen.fill(LIGHT_GRAY)
        draw_center_text(screen, "Racer Game", big_font, BLACK, WIDTH // 2, 120)

        for btn in [play_btn, board_btn, settings_btn, quit_btn]:
            btn.draw(screen, font)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if play_btn.handle_event(event):
                return "name"
            if board_btn.handle_event(event):
                return "leaderboard"
            if settings_btn.handle_event(event):
                return "settings"
            if quit_btn.handle_event(event):
                pygame.quit()
                sys.exit()

        clock.tick(60)


def name_screen():
    name = ""
    start_btn = Button(170, 420, 160, 50, "Start")
    back_btn = Button(170, 490, 160, 50, "Back")

    while True:
        screen.fill(WHITE)
        draw_center_text(screen, "Enter Username", big_font, BLACK, WIDTH // 2, 130)

        pygame.draw.rect(screen, LIGHT_GRAY, (120, 250, 260, 55))
        pygame.draw.rect(screen, BLACK, (120, 250, 260, 55), 2)
        draw_text(screen, name + "|", font, BLACK, 135, 264)

        start_btn.draw(screen, font)
        back_btn.draw(screen, font)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_RETURN and name.strip() != "":
                    return name
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.unicode.isprintable() and len(name) < 12:
                    name += event.unicode

            if start_btn.handle_event(event) and name.strip() != "":
                return name
            if back_btn.handle_event(event):
                return None

        clock.tick(60)


def leaderboard_screen():
    back_btn = Button(170, 620, 160, 45, "Back")

    while True:
        leaderboard = load_leaderboard()

        screen.fill(WHITE)
        draw_center_text(screen, "Top 10 Leaderboard", big_font, BLACK, WIDTH // 2, 70)

        y = 130
        draw_text(screen, "Rank", small_font, BLACK, 30, y)
        draw_text(screen, "Name", small_font, BLACK, 90, y)
        draw_text(screen, "Score", small_font, BLACK, 220, y)
        draw_text(screen, "Distance", small_font, BLACK, 330, y)
        y += 35

        if len(leaderboard) == 0:
            draw_center_text(screen, "No scores yet", font, BLACK, WIDTH // 2, 220)
        else:
            for i, row in enumerate(leaderboard[:10], start=1):
                draw_text(screen, str(i), small_font, BLACK, 35, y)
                draw_text(screen, row["name"], small_font, BLACK, 90, y)
                draw_text(screen, str(row["score"]), small_font, BLACK, 220, y)
                draw_text(screen, str(row["distance"]), small_font, BLACK, 340, y)
                y += 35

        back_btn.draw(screen, font)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if back_btn.handle_event(event):
                return

        clock.tick(60)


def settings_screen():
    global settings

    sound_btn = Button(150, 200, 200, 45, "")
    color_btn = Button(150, 280, 200, 45, "")
    diff_btn = Button(150, 360, 200, 45, "")
    back_btn = Button(150, 470, 200, 45, "Back")

    colors = ["blue", "red", "green", "yellow"]
    difficulties = ["easy", "normal", "hard"]

    while True:
        screen.fill(WHITE)
        draw_center_text(screen, "Settings", big_font, BLACK, WIDTH // 2, 100)

        sound_btn.text = f"Sound: {'On' if settings['sound'] else 'Off'}"
        color_btn.text = f"Car Color: {settings['car_color']}"
        diff_btn.text = f"Difficulty: {settings['difficulty']}"

        for btn in [sound_btn, color_btn, diff_btn, back_btn]:
            btn.draw(screen, font)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if sound_btn.handle_event(event):
                settings["sound"] = not settings["sound"]
                save_settings(settings)

            if color_btn.handle_event(event):
                idx = colors.index(settings["car_color"])
                settings["car_color"] = colors[(idx + 1) % len(colors)]
                save_settings(settings)

            if diff_btn.handle_event(event):
                idx = difficulties.index(settings["difficulty"])
                settings["difficulty"] = difficulties[(idx + 1) % len(difficulties)]
                save_settings(settings)

            if back_btn.handle_event(event):
                return

        clock.tick(60)


def result_screen(result):
    retry_btn = Button(150, 510, 200, 45, "Retry")
    menu_btn = Button(150, 570, 200, 45, "Main Menu")

    add_score(result["name"], result["score"], result["distance"])

    while True:
        screen.fill(WHITE)

        title = "Finished!" if result["won"] else "Game Over"
        title_color = (0, 160, 0) if result["won"] else RED

        draw_center_text(screen, title, big_font, title_color, WIDTH // 2, 110)
        draw_center_text(screen, f"Player: {result['name']}", font, BLACK, WIDTH // 2, 210)
        draw_center_text(screen, f"Score: {result['score']}", font, BLACK, WIDTH // 2, 260)
        draw_center_text(screen, f"Distance: {result['distance']}", font, BLACK, WIDTH // 2, 310)
        draw_center_text(screen, f"Coins: {result['coins']}", font, BLACK, WIDTH // 2, 360)

        retry_btn.draw(screen, font)
        menu_btn.draw(screen, font)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if retry_btn.handle_event(event):
                return "retry"
            if menu_btn.handle_event(event):
                return "menu"

        clock.tick(60)


def main():
    state = "menu"
    username = "Player"

    while True:
        if state == "menu":
            state = menu_screen()

        elif state == "name":
            entered = name_screen()
            if entered is None:
                state = "menu"
            else:
                username = entered
                state = "game"

        elif state == "leaderboard":
            leaderboard_screen()
            state = "menu"

        elif state == "settings":
            settings_screen()
            state = "menu"

        elif state == "game":
            game = RacerGame(screen, username, settings)
            result = game.run()
            next_state = result_screen(result)

            if next_state == "retry":
                state = "game"
            else:
                state = "menu"


main()