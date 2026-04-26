import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (210, 210, 210)
DARK_GRAY = (150, 150, 150)


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen, font):
        mouse = pygame.mouse.get_pos()
        color = DARK_GRAY if self.rect.collidepoint(mouse) else GRAY

        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)

        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


def draw_text(screen, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


def draw_center_text(screen, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)