import pygame
import random
import os

# Window and road settings
WIDTH = 500
HEIGHT = 700
ROAD_LEFT = 70
ROAD_RIGHT = 430
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANE_COUNT = 3
LANE_WIDTH = ROAD_WIDTH // LANE_COUNT
LANE_CENTERS = [ROAD_LEFT + LANE_WIDTH // 2 + i * LANE_WIDTH for i in range(LANE_COUNT)]
FINISH_DISTANCE = 3000

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
DARK_GRAY = (60, 60, 60)
GREEN = (30, 150, 30)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
PURPLE = (160, 32, 240)
CYAN = (0, 220, 255)
BROWN = (139, 69, 19)
BRONZE = (205, 127, 50)
SILVER = (180, 180, 180)


def lane_from_x(x):
    # Return nearest lane index from x coordinate
    distances = [abs(x - c) for c in LANE_CENTERS]
    return distances.index(min(distances))


def safe_load_image(filename, size=None, fallback_color=BLUE):
    # Load image if it exists, otherwise create colored fallback rectangle
    if os.path.exists(filename):
        image = pygame.image.load(filename).convert_alpha()
        if size is not None:
            image = pygame.transform.scale(image, size)
        return image

    if size is None:
        size = (50, 90)

    image = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(image, fallback_color, (0, 0, size[0], size[1]), border_radius=10)
    pygame.draw.rect(image, BLACK, (0, 0, size[0], size[1]), 2, border_radius=10)
    return image


class Player(pygame.sprite.Sprite):
    def __init__(self, car_color):
        super().__init__()

        color_map = {
            "blue": BLUE,
            "red": RED,
            "green": (0, 180, 0),
            "yellow": YELLOW
        }
        fallback_color = color_map.get(car_color, BLUE)

        self.image = safe_load_image("Player.png", (50, 90), fallback_color)
        self.rect = self.image.get_rect(center=(LANE_CENTERS[1], 600))

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        if self.rect.left > ROAD_LEFT and pressed_keys[pygame.K_LEFT]:
            self.rect.move_ip(-6, 0)

        if self.rect.right < ROAD_RIGHT and pressed_keys[pygame.K_RIGHT]:
            self.rect.move_ip(6, 0)


class TrafficCar(pygame.sprite.Sprite):
    def __init__(self, player_lane, speed):
        super().__init__()
        self.image = safe_load_image("Enemy.png", (50, 90), RED)
        self.rect = self.image.get_rect()
        self.speed = speed
        self.spawn(player_lane)

    def spawn(self, player_lane):
        # Safe spawn: avoid placing directly in player lane most of the time
        lane_choices = [0, 1, 2]
        if player_lane in lane_choices and len(lane_choices) > 1:
            lane_choices.remove(player_lane)

        lane = random.choice(lane_choices if random.random() < 0.8 else [0, 1, 2])
        self.rect.center = (LANE_CENTERS[lane], random.randint(-500, -120))

    def move(self, world_speed):
        self.rect.move_ip(0, world_speed + self.speed)


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.weight = random.choice([1, 2, 3])
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)

        color = BRONZE
        if self.weight == 2:
            color = SILVER
        elif self.weight == 3:
            color = YELLOW

        pygame.draw.circle(self.image, color, (14, 14), 14)
        pygame.draw.circle(self.image, BLACK, (14, 14), 14, 2)

        self.rect = self.image.get_rect()
        self.spawn()

    def spawn(self):
        lane = random.randint(0, 2)
        self.rect.center = (LANE_CENTERS[lane], random.randint(-600, -50))

    def move(self, world_speed):
        self.rect.move_ip(0, world_speed)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, kind, player_lane):
        super().__init__()
        self.kind = kind
        self.image = pygame.Surface((70, 40), pygame.SRCALPHA)

        if kind == "barrier":
            pygame.draw.rect(self.image, ORANGE, (0, 0, 70, 40))
            pygame.draw.rect(self.image, BLACK, (0, 0, 70, 40), 2)
        elif kind == "oil":
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(self.image, BLACK, (25, 25), 22)
        elif kind == "pothole":
            self.image = pygame.Surface((52, 52), pygame.SRCALPHA)
            pygame.draw.circle(self.image, BROWN, (26, 26), 22)
            pygame.draw.circle(self.image, BLACK, (26, 26), 22, 2)

        self.rect = self.image.get_rect()
        self.spawn(player_lane)

    def spawn(self, player_lane):
        lane_choices = [0, 1, 2]
        if player_lane in lane_choices and len(lane_choices) > 1:
            lane_choices.remove(player_lane)

        lane = random.choice(lane_choices if random.random() < 0.75 else [0, 1, 2])
        self.rect.center = (LANE_CENTERS[lane], random.randint(-700, -100))

    def move(self, world_speed):
        self.rect.move_ip(0, world_speed)


class RoadEvent(pygame.sprite.Sprite):
    def __init__(self, event_type):
        super().__init__()
        self.event_type = event_type
        self.dx = 0

        if event_type == "moving_barrier":
            self.image = pygame.Surface((100, 25))
            self.image.fill(ORANGE)
            self.rect = self.image.get_rect(center=(WIDTH // 2, -80))
            self.dx = random.choice([-3, 3])

        elif event_type == "speed_bump":
            self.image = pygame.Surface((LANE_WIDTH - 10, 16))
            self.image.fill(BROWN)
            lane = random.randint(0, 2)
            self.rect = self.image.get_rect(center=(LANE_CENTERS[lane], -80))

        else:  # nitro_strip
            self.image = pygame.Surface((LANE_WIDTH - 20, 16))
            self.image.fill(CYAN)
            lane = random.randint(0, 2)
            self.rect = self.image.get_rect(center=(LANE_CENTERS[lane], -80))

    def move(self, world_speed):
        self.rect.move_ip(0, world_speed)

        if self.event_type == "moving_barrier":
            self.rect.move_ip(self.dx, 0)

            if self.rect.left <= ROAD_LEFT or self.rect.right >= ROAD_RIGHT:
                self.dx *= -1


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, kind):
        super().__init__()
        self.kind = kind
        self.spawn_time = pygame.time.get_ticks()
        self.timeout = 5000

        self.image = pygame.Surface((34, 34), pygame.SRCALPHA)

        if kind == "nitro":
            color = CYAN
        elif kind == "shield":
            color = PURPLE
        else:
            color = GREEN

        pygame.draw.circle(self.image, color, (17, 17), 17)
        pygame.draw.circle(self.image, BLACK, (17, 17), 17, 2)

        self.rect = self.image.get_rect()
        lane = random.randint(0, 2)
        self.rect.center = (LANE_CENTERS[lane], random.randint(-900, -200))

    def move(self, world_speed):
        self.rect.move_ip(0, world_speed)

    def expired(self):
        return pygame.time.get_ticks() - self.spawn_time > self.timeout


class RacerGame:
    def __init__(self, screen, username, settings):
        self.screen = screen
        self.username = username
        self.settings = settings

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 20)
        self.small_font = pygame.font.SysFont("Verdana", 16)

        # Base speed depends on settings
        difficulty_speed = {
            "easy": 5,
            "normal": 7,
            "hard": 9
        }
        self.base_speed = difficulty_speed[settings["difficulty"]]
        self.speed = self.base_speed

        self.player = Player(settings["car_color"])

        # Sprite groups
        self.traffic = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.road_events = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        # Old base values kept from Practice 10–11
        self.coin_value_total = 0

        # New TSIS 3 values
        self.distance = 0
        self.bonus_score = 0
        self.road_scroll = 0
        self.won = False

        # Active power-up
        self.active_powerup = None
        self.powerup_end_time = 0
        self.shield_ready = False

        # Spawn timers
        now = pygame.time.get_ticks()
        self.last_traffic_spawn = now
        self.last_obstacle_spawn = now
        self.last_event_spawn = now
        self.last_coin_spawn = now
        self.last_powerup_spawn = now

        # Spawn intervals
        if settings["difficulty"] == "easy":
            self.traffic_interval = 1800
            self.obstacle_interval = 2200
        elif settings["difficulty"] == "hard":
            self.traffic_interval = 950
            self.obstacle_interval = 1400
        else:
            self.traffic_interval = 1300
            self.obstacle_interval = 1800

        self.event_interval = 3000
        self.coin_interval = 1200
        self.powerup_interval = 6500

        # Sound
        self.crash_sound = None
        if settings["sound"] and os.path.exists("crash.wav"):
            try:
                self.crash_sound = pygame.mixer.Sound("crash.wav")
            except:
                self.crash_sound = None

    def current_score(self):
        # Score = weighted coins + distance + bonuses
        return self.coin_value_total * 20 + self.distance // 5 + self.bonus_score

    def draw_road(self):
        self.screen.fill(GREEN)
        pygame.draw.rect(self.screen, GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))

        # Scrolling lane markings
        self.road_scroll += self.speed
        if self.road_scroll >= 80:
            self.road_scroll = 0

        for y in range(-80, HEIGHT, 80):
            pygame.draw.rect(self.screen, WHITE, (ROAD_LEFT + LANE_WIDTH - 5, y + self.road_scroll, 10, 40))
            pygame.draw.rect(self.screen, WHITE, (ROAD_LEFT + 2 * LANE_WIDTH - 5, y + self.road_scroll, 10, 40))

    def spawn_entities(self):
        now = pygame.time.get_ticks()
        player_lane = lane_from_x(self.player.rect.centerx)

        if now - self.last_traffic_spawn >= self.traffic_interval:
            traffic_speed = random.randint(0, 3)
            self.traffic.add(TrafficCar(player_lane, traffic_speed))
            self.last_traffic_spawn = now

        if now - self.last_obstacle_spawn >= self.obstacle_interval:
            kind = random.choice(["barrier", "oil", "pothole"])
            self.obstacles.add(Obstacle(kind, player_lane))
            self.last_obstacle_spawn = now

        if now - self.last_event_spawn >= self.event_interval:
            event_type = random.choice(["moving_barrier", "speed_bump", "nitro_strip"])
            self.road_events.add(RoadEvent(event_type))
            self.last_event_spawn = now

        if now - self.last_coin_spawn >= self.coin_interval:
            self.coins.add(Coin())
            self.last_coin_spawn = now

        if now - self.last_powerup_spawn >= self.powerup_interval:
            kind = random.choice(["nitro", "shield", "repair"])
            self.powerups.add(PowerUp(kind))
            self.last_powerup_spawn = now

    def update_groups(self):
        for group in [self.traffic, self.coins, self.obstacles, self.road_events, self.powerups]:
            for sprite in list(group):
                sprite.move(self.speed)

                # Remove off-screen objects
                if sprite.rect.top > HEIGHT + 60:
                    group.remove(sprite)

        # Remove expired powerups
        for p in list(self.powerups):
            if p.expired():
                self.powerups.remove(p)

    def apply_nitro(self):
        self.active_powerup = "Nitro"
        self.powerup_end_time = pygame.time.get_ticks() + 4000
        self.speed = self.base_speed + 4

    def apply_shield(self):
        self.active_powerup = "Shield"
        self.powerup_end_time = 0
        self.shield_ready = True
        self.speed = self.base_speed

    def clear_active_powerup(self):
        self.active_powerup = None
        self.powerup_end_time = 0
        self.shield_ready = False
        self.speed = self.base_speed

    def apply_repair(self):
        # Instant effect:
        # remove one obstacle in player lane or restore speed to base
        player_lane = lane_from_x(self.player.rect.centerx)

        removed = False
        for obs in list(self.obstacles):
            if lane_from_x(obs.rect.centerx) == player_lane:
                self.obstacles.remove(obs)
                removed = True
                break

        if not removed:
            self.speed = self.base_speed

        self.bonus_score += 40
        self.active_powerup = None
        self.powerup_end_time = 0
        self.shield_ready = False

    def handle_powerup_timeout(self):
        if self.active_powerup == "Nitro":
            if pygame.time.get_ticks() >= self.powerup_end_time:
                self.clear_active_powerup()

    def use_shield_if_available(self):
        if self.shield_ready:
            self.clear_active_powerup()
            self.bonus_score += 25
            return True
        return False

    def handle_collisions(self):
        # Traffic collision ends run unless shield
        traffic_hit = pygame.sprite.spritecollideany(self.player, self.traffic)
        if traffic_hit:
            if self.use_shield_if_available():
                self.traffic.remove(traffic_hit)
            else:
                return False

        # Coins
        collected_coins = pygame.sprite.spritecollide(self.player, self.coins, True)
        for coin in collected_coins:
            self.coin_value_total += coin.weight

            # Old Practice 11 idea: increase speed after earning N coins
            if self.coin_value_total % 5 == 0:
                self.base_speed += 1
                if self.active_powerup != "Nitro":
                    self.speed = self.base_speed

        # Obstacles
        collided_obstacles = pygame.sprite.spritecollide(self.player, self.obstacles, False)
        for obs in collided_obstacles:
            if obs.kind == "barrier":
                if self.use_shield_if_available():
                    self.obstacles.remove(obs)
                else:
                    return False

            elif obs.kind == "oil":
                # Oil spill pushes car sideways
                self.player.rect.x += random.choice([-50, 50])
                if self.player.rect.left < ROAD_LEFT:
                    self.player.rect.left = ROAD_LEFT
                if self.player.rect.right > ROAD_RIGHT:
                    self.player.rect.right = ROAD_RIGHT
                self.obstacles.remove(obs)

            elif obs.kind == "pothole":
                # Pothole slows temporarily
                self.speed = max(3, self.speed - 2)
                self.obstacles.remove(obs)

        # Road events
        collided_events = pygame.sprite.spritecollide(self.player, self.road_events, False)
        for ev in collided_events:
            if ev.event_type == "moving_barrier":
                if self.use_shield_if_available():
                    self.road_events.remove(ev)
                else:
                    return False

            elif ev.event_type == "speed_bump":
                self.speed = max(3, self.speed - 1)
                self.road_events.remove(ev)

            elif ev.event_type == "nitro_strip":
                self.clear_active_powerup()
                self.apply_nitro()
                self.road_events.remove(ev)

        # Power-ups
        collected_powerups = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for power in collected_powerups:
            # Only one power-up active at a time
            self.clear_active_powerup()

            if power.kind == "nitro":
                self.apply_nitro()
                self.bonus_score += 30

            elif power.kind == "shield":
                self.apply_shield()
                self.bonus_score += 30

            elif power.kind == "repair":
                self.apply_repair()

        return True

    def scale_difficulty(self):
        # Increase traffic and obstacles as distance grows
        if self.distance > 0 and self.distance % 500 == 0:
            self.traffic_interval = max(600, self.traffic_interval - 40)
            self.obstacle_interval = max(900, self.obstacle_interval - 35)

    def draw_hud(self):
        remaining = max(0, FINISH_DISTANCE - self.distance)
        checkpoint = min(3, self.distance // 1000 + 1)

        lines = [
            f"Player: {self.username}",
            f"Score: {self.current_score()}",
            f"Coins: {self.coin_value_total}",
            f"Distance: {self.distance}",
            f"Remaining: {remaining}",
            f"Checkpoint: {checkpoint}/3"
        ]

        y = 10
        for line in lines:
            surf = self.font.render(line, True, BLACK)
            self.screen.blit(surf, (10, y))
            y += 24

        # Active power-up display
        power_text = "Power-up: None"
        if self.active_powerup == "Nitro":
            seconds = max(0, (self.powerup_end_time - pygame.time.get_ticks()) // 1000 + 1)
            power_text = f"Power-up: Nitro ({seconds}s)"
        elif self.active_powerup == "Shield":
            power_text = "Power-up: Shield"

        power_surf = self.font.render(power_text, True, BLACK)
        self.screen.blit(power_surf, (250, 10))

        help_surf = self.small_font.render("Left / Right arrows to drive", True, BLACK)
        self.screen.blit(help_surf, (250, 38))

    def draw_all(self):
        self.draw_road()

        for group in [self.coins, self.powerups, self.road_events, self.obstacles, self.traffic]:
            for sprite in group:
                self.screen.blit(sprite.image, sprite.rect)

        self.screen.blit(self.player.image, self.player.rect)
        self.draw_hud()

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

            self.player.move()
            self.spawn_entities()
            self.update_groups()
            self.handle_powerup_timeout()

            if not self.handle_collisions():
                if self.crash_sound is not None:
                    self.crash_sound.play()
                    pygame.time.delay(300)
                running = False

            # Progress
            self.distance += self.speed // 2
            self.scale_difficulty()

            # Finish line
            if self.distance >= FINISH_DISTANCE:
                self.won = True
                self.bonus_score += 200
                running = False

            self.draw_all()
            pygame.display.update()
            self.clock.tick(60)

        return {
            "name": self.username,
            "score": self.current_score(),
            "distance": self.distance,
            "coins": self.coin_value_total,
            "won": self.won
        }