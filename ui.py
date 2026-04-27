import pygame

BLACK = (0, 0, 0)
GRAY = (210, 210, 210)
DARK_GRAY = (170, 170, 170)


class Button:
    """
    Simple reusable button for all screens.
    """
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen, font):
        mouse = pygame.mouse.get_pos()
        color = DARK_GRAY if self.rect.collidepoint(mouse) else GRAY

        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)

        surface = font.render(self.text, True, BLACK)
        rect = surface.get_rect(center=self.rect.center)
        screen.blit(surface, rect)

    def handle_event(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


def draw_text(screen, text, font, color, x, y):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def draw_center_text(screen, text, font, color, x, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)