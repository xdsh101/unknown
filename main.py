import pygame
import sys
from racer import RacerGame
from ui import Button, draw_text, draw_center_text
from persistence import load_settings, save_settings, load_leaderboard, add_score

pygame.init()

# Window settings
WIDTH = 500
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 3 Racer")
clock = pygame.time.Clock()

# Basic colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (225, 225, 225)
RED = (255, 0, 0)
GREEN = (0, 160, 0)

# Fonts
font = pygame.font.SysFont("Verdana", 24)
small_font = pygame.font.SysFont("Verdana", 18)
big_font = pygame.font.SysFont("Verdana", 40)


def menu_screen(username, settings):
    """
    Main menu screen.
    Also contains username input, so the player can type the name before starting.
    """
    play_btn = Button(170, 260, 160, 50, "Play")
    board_btn = Button(170, 330, 160, 50, "Leaderboard")
    settings_btn = Button(170, 400, 160, 50, "Settings")
    quit_btn = Button(170, 470, 160, 50, "Quit")

    while True:
        screen.fill(LIGHT_GRAY)

        draw_center_text(screen, "Racer Game", big_font, BLACK, WIDTH // 2, 90)
        draw_center_text(screen, "Enter Username", font, BLACK, WIDTH // 2, 150)

        # Username input box
        pygame.draw.rect(screen, WHITE, (120, 180, 260, 45))
        pygame.draw.rect(screen, BLACK, (120, 180, 260, 45), 2)
        draw_text(screen, username + "|", font, BLACK, 130, 190)

        # Small settings preview
        draw_center_text(
            screen,
            f"Difficulty: {settings['difficulty']}   Car color: {settings['car_color']}   Sound: {'On' if settings['sound'] else 'Off'}",
            small_font,
            BLACK,
            WIDTH // 2,
            235
        )

        for btn in [play_btn, board_btn, settings_btn, quit_btn]:
            btn.draw(screen, font)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Username typing
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.key == pygame.K_RETURN and username.strip() != "":
                    return "game", username
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.unicode.isprintable() and len(username) < 12:
                    username += event.unicode

            # Button clicks
            if play_btn.handle_event(event) and username.strip() != "":
                return "game", username
            if board_btn.handle_event(event):
                return "leaderboard", username
            if settings_btn.handle_event(event):
                return "settings", username
            if quit_btn.handle_event(event):
                pygame.quit()
                sys.exit()

        clock.tick(60)


def leaderboard_screen():
    """
    Shows saved Top 10 scores.
    """
    back_btn = Button(170, 625, 160, 45, "Back")

    while True:
        leaderboard = load_leaderboard()

        screen.fill(WHITE)
        draw_center_text(screen, "Top 10 Leaderboard", big_font, BLACK, WIDTH // 2, 70)

        # Table header
        y = 130
        draw_text(screen, "Rank", small_font, BLACK, 25, y)
        draw_text(screen, "Name", small_font, BLACK, 80, y)
        draw_text(screen, "Score", small_font, BLACK, 210, y)
        draw_text(screen, "Distance", small_font, BLACK, 300, y)
        draw_text(screen, "Date", small_font, BLACK, 390, y)

        y += 35

        if len(leaderboard) == 0:
            draw_center_text(screen, "No scores yet", font, BLACK, WIDTH // 2, 220)
        else:
            for i, row in enumerate(leaderboard[:10], start=1):
                draw_text(screen, str(i), small_font, BLACK, 30, y)
                draw_text(screen, row["name"], small_font, BLACK, 80, y)
                draw_text(screen, str(row["score"]), small_font, BLACK, 210, y)
                draw_text(screen, str(row["distance"]), small_font, BLACK, 305, y)
                draw_text(screen, row["date"], small_font, BLACK, 390, y)
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


def settings_screen(settings):
    """
    Settings screen.
    Allows toggling sound, cycling car color, and changing difficulty.
    """
    sound_btn = Button(150, 210, 200, 45, "")
    color_btn = Button(150, 290, 200, 45, "")
    diff_btn = Button(150, 370, 200, 45, "")
    save_btn = Button(150, 470, 200, 50, "Save & Back")

    colors = ["blue", "red", "green", "yellow"]
    difficulties = ["easy", "normal", "hard"]

    while True:
        sound_btn.text = f"Sound: {'On' if settings['sound'] else 'Off'}"
        color_btn.text = f"Car Color: {settings['car_color']}"
        diff_btn.text = f"Difficulty: {settings['difficulty']}"

        screen.fill(WHITE)
        draw_center_text(screen, "Settings", big_font, BLACK, WIDTH // 2, 100)

        # Color preview
        preview_color = settings["car_color"]
        color_map = {
            "blue": (0, 120, 255),
            "red": (255, 60, 60),
            "green": (0, 180, 0),
            "yellow": (255, 215, 0)
        }
        pygame.draw.rect(screen, color_map[preview_color], (220, 160, 60, 28), border_radius=6)
        pygame.draw.rect(screen, BLACK, (220, 160, 60, 28), 2, border_radius=6)

        for btn in [sound_btn, color_btn, diff_btn, save_btn]:
            btn.draw(screen, font)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if sound_btn.handle_event(event):
                settings["sound"] = not settings["sound"]

            if color_btn.handle_event(event):
                idx = colors.index(settings["car_color"])
                settings["car_color"] = colors[(idx + 1) % len(colors)]

            if diff_btn.handle_event(event):
                idx = difficulties.index(settings["difficulty"])
                settings["difficulty"] = difficulties[(idx + 1) % len(difficulties)]

            if save_btn.handle_event(event):
                save_settings(settings)
                return settings

        clock.tick(60)


def result_screen(result):
    """
    Game over / finish screen.
    Shows the result and allows retry or return to menu.
    """
    retry_btn = Button(150, 520, 200, 45, "Retry")
    menu_btn = Button(150, 580, 200, 45, "Main Menu")

    title = "Finished!" if result["won"] else "Game Over"
    title_color = GREEN if result["won"] else RED

    while True:
        screen.fill(WHITE)

        draw_center_text(screen, title, big_font, title_color, WIDTH // 2, 110)
        draw_center_text(screen, f"Player: {result['name']}", font, BLACK, WIDTH // 2, 210)
        draw_center_text(screen, f"Score: {result['score']}", font, BLACK, WIDTH // 2, 255)
        draw_center_text(screen, f"Distance: {result['distance']}", font, BLACK, WIDTH // 2, 300)
        draw_center_text(screen, f"Coins: {result['coins']}", font, BLACK, WIDTH // 2, 345)

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
    """
    Main state machine of the program.
    """
    settings = load_settings()
    username = ""
    state = "menu"

    while True:
        if state == "menu":
            state, username = menu_screen(username, settings)

        elif state == "leaderboard":
            leaderboard_screen()
            state = "menu"

        elif state == "settings":
            settings = settings_screen(settings)
            state = "menu"

        elif state == "game":
            game = RacerGame(screen, username, settings)
            result = game.run()

            # Save result after run ends
            add_score(
                result["name"],
                result["score"],
                result["distance"],
                result["coins"]
            )

            next_state = result_screen(result)
            if next_state == "retry":
                state = "game"
            else:
                state = "menu"


main()