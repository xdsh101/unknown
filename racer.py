import pygame
import random
import os

# ---------------------------------
# Window and road constants
# ---------------------------------
WIDTH = 500
HEIGHT = 700

ROAD_LEFT = 70
ROAD_RIGHT = 430
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT

LANE_COUNT = 3
LANE_WIDTH = ROAD_WIDTH // LANE_COUNT
LANE_CENTERS = [
    ROAD_LEFT + LANE_WIDTH // 2 + i * LANE_WIDTH
    for i in range(LANE_COUNT)
]

FINISH_DISTANCE = 3200

# ---------------------------------
# Colors
# ---------------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
GREEN = (25, 140, 25)
YELLOW = (255, 215, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 140, 0)
PURPLE = (160, 32, 240)
CYAN = (0, 220, 255)
BROWN = (139, 69, 19)
BRONZE = (205, 127, 50)
SILVER = (180, 180, 180)


def load_image_or_fallback(filename, size, fallback_color):
    """
    Load an image if it exists.
    If it does not exist, create a simple fallback rectangle sprite.
    """
    if os.path.exists(filename):
        image = pygame.image.load(filename).convert_alpha()
        return pygame.transform.scale(image, size)

    image = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(image, fallback_color, (0, 0, size[0], size[1]), border_radius=10)
    pygame.draw.rect(image, BLACK, (0, 0, size[0], size[1]), 2, border_radius=10)
    return image


def tint_car_image(image, car_color_name):
    """
    Apply a simple color tint to the player sprite.
    This keeps the uploaded car image, while still letting Settings change car color.
    """
    if car_color_name == "blue":
        return image.copy()

    tint_colors = {
        "red": (255, 80, 80),
        "green": (80, 220, 80),
        "yellow": (255, 230, 80)
    }

    result = image.copy()
    tint = tint_colors.get(car_color_name, (255, 255, 255))

    overlay = pygame.Surface(result.get_size(), pygame.SRCALPHA)
    overlay.fill((tint[0], tint[1], tint[2], 45))
    result.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return result


def lane_from_x(x):
    """
    Return the lane index closest to x coordinate.
    """
    distances = [abs(x - center) for center in LANE_CENTERS]
    return distances.index(min(distances))


def choose_safe_lane(player_lane, allow_same_lane_probability=0.2):
    """
    Most of the time do not spawn directly in the player's lane.
    Sometimes allow it, so the game still has tension.
    """
    lanes = [0, 1, 2]

    if random.random() > allow_same_lane_probability:
        if player_lane in lanes:
            lanes.remove(player_lane)

    return random.choice(lanes)


# ---------------------------------
# Sprite classes
# ---------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, car_color):
        super().__init__()

        base_image = load_image_or_fallback("Player.png", (50, 90), BLUE)
        self.image = tint_car_image(base_image, car_color)
        self.rect = self.image.get_rect(center=(LANE_CENTERS[1], 595))

    def move(self):
        """
        Player movement stays like earlier racer versions:
        left/right on the road only.
        """
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[pygame.K_LEFT] and self.rect.left > ROAD_LEFT:
            self.rect.move_ip(-6, 0)

        if pressed_keys[pygame.K_RIGHT] and self.rect.right < ROAD_RIGHT:
            self.rect.move_ip(6, 0)


class TrafficCar(pygame.sprite.Sprite):
    def __init__(self, player_lane):
        super().__init__()

        self.image = load_image_or_fallback("Enemy.png", (50, 90), RED)
        self.rect = self.image.get_rect()

        lane = choose_safe_lane(player_lane, 0.15)
        self.rect.center = (LANE_CENTERS[lane], random.randint(-600, -120))

        # Small per-car speed variation
        self.extra_speed = random.randint(0, 2)

    def move(self, world_speed):
        self.rect.move_ip(0, world_speed + self.extra_speed)


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.weight = random.choice([1, 2, 3])
        self.make_image()
        self.spawn()

    def make_image(self):
        """
        Weighted coins from Practice 11 are kept.
        Bronze = 1, Silver = 2, Gold = 3.
        """
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)

        color = BRONZE
        if self.weight == 2:
            color = SILVER
        elif self.weight == 3:
            color = YELLOW

        pygame.draw.circle(self.image, color, (14, 14), 14)
        pygame.draw.circle(self.image, BLACK, (14, 14), 14, 2)
        self.rect = self.image.get_rect()

    def spawn(self):
        lane = random.randint(0, 2)
        self.rect.center = (LANE_CENTERS[lane], random.randint(-700, -50))

    def respawn(self):
        self.weight = random.choice([1, 2, 3])
        self.make_image()
        self.spawn()

    def move(self, world_speed):
        self.rect.move_ip(0, world_speed)


class Hazard(pygame.sprite.Sprite):
    def __init__(self, hazard_type, lane, y_pos):
        super().__init__()
        self.hazard_type = hazard_type

        if hazard_type == "barrier":
            self.image = pygame.Surface((90, 32), pygame.SRCALPHA)
            pygame.draw.rect(self.image, ORANGE, (0, 0, 90, 32), border_radius=5)
            pygame.draw.rect(self.image, BLACK, (0, 0, 90, 32), 2, border_radius=5)

        elif hazard_type == "oil":
            self.image = pygame.Surface((46, 46), pygame.SRCALPHA)
            pygame.draw.circle(self.image, BLACK, (23, 23), 21)

        else:  # pothole
            self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
            pygame.draw.circle(self.image, BROWN, (24, 24), 20)
            pygame.draw.circle(self.image, BLACK, (24, 24), 20, 2)

        self.rect = self.image.get_rect(center=(LANE_CENTERS[lane], y_pos))

    def move(self, world_speed):
        self.rect.move_ip(0, world_speed)


class RoadEvent(pygame.sprite.Sprite):
    def __init__(self, event_type):
        super().__init__()
        self.event_type = event_type
        self.dx = 0

        if event_type == "moving_barrier":
            self.image = pygame.Surface((100, 22))
            self.image.fill(ORANGE)
            self.rect = self.image.get_rect(center=(WIDTH // 2, -80))
            self.dx = random.choice([-3, 3])

        elif event_type == "speed_bump":
            lane = random.randint(0, 2)
            self.image = pygame.Surface((LANE_WIDTH - 16, 14))
            self.image.fill(BROWN)
            self.rect = self.image.get_rect(center=(LANE_CENTERS[lane], -80))

        else:  # nitro_strip
            lane = random.randint(0, 2)
            self.image = pygame.Surface((LANE_WIDTH - 16, 14))
            self.image.fill(CYAN)
            self.rect = self.image.get_rect(center=(LANE_CENTERS[lane], -80))

    def move(self, world_speed):
        self.rect.move_ip(0, world_speed)

        # Dynamic horizontal movement for moving barrier
        if self.event_type == "moving_barrier":
            self.rect.move_ip(self.dx, 0)

            if self.rect.left <= ROAD_LEFT or self.rect.right >= ROAD_RIGHT:
                self.dx *= -1


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, power_type):
        super().__init__()
        self.power_type = power_type
        self.spawn_time = pygame.time.get_ticks()
        self.timeout = 8000

        self.image = pygame.Surface((34, 34), pygame.SRCALPHA)

        if power_type == "nitro":
            color = CYAN
        elif power_type == "shield":
            color = PURPLE
        else:  # repair
            color = (0, 200, 0)

        pygame.draw.circle(self.image, color, (17, 17), 17)
        pygame.draw.circle(self.image, BLACK, (17, 17), 17, 2)

        lane = random.randint(0, 2)
        self.rect = self.image.get_rect(center=(LANE_CENTERS[lane], random.randint(-900, -250)))

    def move(self, world_speed):
        self.rect.move_ip(0, world_speed)

    def expired(self):
        return pygame.time.get_ticks() - self.spawn_time > self.timeout


# ---------------------------------
# Main game class
# ---------------------------------
class RacerGame:
    def __init__(self, screen, username, settings):
        self.screen = screen
        self.username = username
        self.settings = settings

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 20)
        self.small_font = pygame.font.SysFont("Verdana", 16)

        # Difficulty controls the starting speed and spawn frequency
        difficulty_data = {
            "easy": {"speed": 5, "traffic": 1800, "hazard": 2100},
            "normal": {"speed": 7, "traffic": 1300, "hazard": 1700},
            "hard": {"speed": 9, "traffic": 950, "hazard": 1300}
        }

        self.base_speed = difficulty_data[settings["difficulty"]]["speed"]
        self.traffic_interval = difficulty_data[settings["difficulty"]]["traffic"]
        self.hazard_interval = difficulty_data[settings["difficulty"]]["hazard"]

        self.event_interval = 3000
        self.coin_interval = 1200
        self.powerup_interval = 6500

        self.player = Player(settings["car_color"])

        # Groups
        self.traffic = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()
        self.events = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        # Base racer values
        self.coin_value_total = 0
        self.distance = 0
        self.bonus_score = 0
        self.won = False

        # Road animation
        self.road_scroll = 0

        # Power-up state
        self.active_powerup = None
        self.powerup_end_time = 0
        self.shield_ready = False

        # Speed bump slowdown timer
        self.slow_until = 0

        # Spawn timers
        now = pygame.time.get_ticks()
        self.last_traffic_spawn = now
        self.last_hazard_spawn = now
        self.last_event_spawn = now
        self.last_coin_spawn = now
        self.last_powerup_spawn = now

        # Keep some weighted coins active from the start
        for _ in range(3):
            self.coins.add(Coin())

        # Optional background image
        self.background_image = None
        if os.path.exists("AnimatedStreet.png"):
            img = pygame.image.load("AnimatedStreet.png").convert()
            self.background_image = pygame.transform.scale(img, (WIDTH, HEIGHT))

        # Optional sounds
        self.crash_sound = None
        if settings["sound"] and os.path.exists("crash.wav"):
            try:
                self.crash_sound = pygame.mixer.Sound("crash.wav")
            except:
                self.crash_sound = None

        # Optional background music
        if settings["sound"] and os.path.exists("background.wav"):
            try:
                pygame.mixer.music.load("background.wav")
                pygame.mixer.music.play(-1)
            except:
                pass

    def stop_audio(self):
        """
        Stop music when leaving the game.
        """
        try:
            pygame.mixer.music.stop()
        except:
            pass

    def current_world_speed(self):
        """
        Compute final speed with active effects.
        """
        speed = self.base_speed

        if self.active_powerup == "Nitro":
            speed += 4

        if pygame.time.get_ticks() < self.slow_until:
            speed = max(4, speed - 2)

        return speed

    def current_score(self):
        """
        Score combines:
        - weighted coins
        - distance
        - bonuses from power-ups and events
        """
        return self.coin_value_total * 20 + self.distance // 5 + self.bonus_score

    def draw_road(self):
        """
        Draw moving road background and lane markings.
        """
        if self.background_image is not None:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(GREEN)

        pygame.draw.rect(self.screen, GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))

        self.road_scroll += self.current_world_speed()
        if self.road_scroll >= 80:
            self.road_scroll = 0

        for y in range(-80, HEIGHT, 80):
            pygame.draw.rect(
                self.screen,
                WHITE,
                (ROAD_LEFT + LANE_WIDTH - 5, y + self.road_scroll, 10, 40)
            )
            pygame.draw.rect(
                self.screen,
                WHITE,
                (ROAD_LEFT + 2 * LANE_WIDTH - 5, y + self.road_scroll, 10, 40)
            )

    def spawn_traffic(self):
        """
        Spawn traffic cars with safe spawn logic.
        """
        player_lane = lane_from_x(self.player.rect.centerx)
        self.traffic.add(TrafficCar(player_lane))

    def spawn_hazard_pattern(self):
        """
        Spawn lane hazards while leaving at least one safe path.
        This gives the player a choice of lanes.
        """
        blocked_lane_count = random.choice([1, 2])
        blocked_lanes = random.sample([0, 1, 2], blocked_lane_count)
        y_pos = random.randint(-750, -120)

        for lane in blocked_lanes:
            kind = random.choice(["barrier", "oil", "pothole"])
            self.hazards.add(Hazard(kind, lane, y_pos))

    def spawn_event(self):
        """
        Spawn a dynamic road event.
        """
        event_type = random.choice(["moving_barrier", "speed_bump", "nitro_strip"])
        self.events.add(RoadEvent(event_type))

    def spawn_coin_if_needed(self):
        """
        Keep several weighted coins on the road.
        """
        if len(self.coins) < 3:
            self.coins.add(Coin())

    def spawn_powerup(self):
        """
        Only one collectible power-up on the field at a time.
        """
        if len(self.powerups) == 0:
            kind = random.choice(["nitro", "shield", "repair"])
            self.powerups.add(PowerUp(kind))

    def handle_spawns(self):
        now = pygame.time.get_ticks()

        if now - self.last_traffic_spawn >= self.traffic_interval:
            self.spawn_traffic()
            self.last_traffic_spawn = now

        if now - self.last_hazard_spawn >= self.hazard_interval:
            self.spawn_hazard_pattern()
            self.last_hazard_spawn = now

        if now - self.last_event_spawn >= self.event_interval:
            self.spawn_event()
            self.last_event_spawn = now

        if now - self.last_coin_spawn >= self.coin_interval:
            self.spawn_coin_if_needed()
            self.last_coin_spawn = now

        if now - self.last_powerup_spawn >= self.powerup_interval:
            self.spawn_powerup()
            self.last_powerup_spawn = now

    def update_groups(self):
        """
        Move all objects and remove those that go off screen.
        """
        speed = self.current_world_speed()

        for group in [self.traffic, self.coins, self.hazards, self.events, self.powerups]:
            for sprite in list(group):
                sprite.move(speed)

                if sprite.rect.top > HEIGHT + 70:
                    group.remove(sprite)

        for p in list(self.powerups):
            if p.expired():
                self.powerups.remove(p)

    def clear_active_powerup(self):
        """
        Reset currently active power-up effect.
        """
        self.active_powerup = None
        self.powerup_end_time = 0
        self.shield_ready = False

    def activate_nitro(self):
        self.clear_active_powerup()
        self.active_powerup = "Nitro"
        self.powerup_end_time = pygame.time.get_ticks() + 4000
        self.bonus_score += 30

    def activate_shield(self):
        self.clear_active_powerup()
        self.active_powerup = "Shield"
        self.shield_ready = True
        self.bonus_score += 30

    def use_repair(self):
        """
        Instant Repair effect:
        clears one nearest hazard or traffic object in the player's lane.
        If nothing is found, it restores road speed.
        """
        player_lane = lane_from_x(self.player.rect.centerx)
        player_y = self.player.rect.centery

        candidates = []

        for sprite in self.hazards:
            if lane_from_x(sprite.rect.centerx) == player_lane and sprite.rect.centery < player_y:
                candidates.append(sprite)

        for sprite in self.traffic:
            if lane_from_x(sprite.rect.centerx) == player_lane and sprite.rect.centery < player_y:
                candidates.append(sprite)

        if len(candidates) > 0:
            nearest = min(candidates, key=lambda s: abs(player_y - s.rect.centery))

            if nearest in self.hazards:
                self.hazards.remove(nearest)
            elif nearest in self.traffic:
                self.traffic.remove(nearest)
        else:
            # If nothing to clear, just remove slowdown
            self.slow_until = 0

        self.bonus_score += 40
        self.clear_active_powerup()

    def handle_powerup_timeout(self):
        """
        End Nitro after time expires.
        Shield stays until triggered.
        """
        if self.active_powerup == "Nitro":
            if pygame.time.get_ticks() >= self.powerup_end_time:
                self.clear_active_powerup()

    def use_shield_if_available(self):
        """
        Consume shield on first collision.
        """
        if self.shield_ready:
            self.clear_active_powerup()
            self.bonus_score += 20
            return True
        return False

    def handle_collisions(self):
        """
        Handle all gameplay collisions.
        Return False if run should end.
        """
        # Traffic collision
        traffic_hit = pygame.sprite.spritecollideany(self.player, self.traffic)
        if traffic_hit:
            if self.use_shield_if_available():
                self.traffic.remove(traffic_hit)
            else:
                return False

        # Coin collection
        collected = pygame.sprite.spritecollide(self.player, self.coins, False)
        for coin in collected:
            self.coin_value_total += coin.weight
            coin.respawn()

            # Keep old Practice 11 rule:
            # enemy/world speed increases after N earned coins
            if self.coin_value_total % 5 == 0:
                self.base_speed += 1

        # Hazard collisions
        collided_hazards = pygame.sprite.spritecollide(self.player, self.hazards, False)
        for hazard in collided_hazards:
            if hazard.hazard_type == "barrier":
                if self.use_shield_if_available():
                    self.hazards.remove(hazard)
                else:
                    return False

            elif hazard.hazard_type == "oil":
                # Oil spill shifts the car sideways
                self.player.rect.x += random.choice([-55, 55])

                if self.player.rect.left < ROAD_LEFT:
                    self.player.rect.left = ROAD_LEFT
                if self.player.rect.right > ROAD_RIGHT:
                    self.player.rect.right = ROAD_RIGHT

                self.hazards.remove(hazard)

            elif hazard.hazard_type == "pothole":
                # Pothole temporarily slows the road
                self.slow_until = pygame.time.get_ticks() + 1500
                self.hazards.remove(hazard)

        # Dynamic road events
        collided_events = pygame.sprite.spritecollide(self.player, self.events, False)
        for event in collided_events:
            if event.event_type == "moving_barrier":
                if self.use_shield_if_available():
                    self.events.remove(event)
                else:
                    return False

            elif event.event_type == "speed_bump":
                self.slow_until = pygame.time.get_ticks() + 1200
                self.events.remove(event)

            elif event.event_type == "nitro_strip":
                # Nitro strip gives temporary speed boost
                self.activate_nitro()
                self.events.remove(event)

        # Collectible power-ups
        collected_powerups = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for power in collected_powerups:
            if power.power_type == "nitro":
                self.activate_nitro()
            elif power.power_type == "shield":
                self.activate_shield()
            elif power.power_type == "repair":
                self.use_repair()

        return True

    def scale_difficulty(self):
        """
        As the player progresses, traffic and hazard frequency increase.
        """
        if self.distance > 0 and self.distance % 600 == 0:
            self.traffic_interval = max(600, self.traffic_interval - 35)
            self.hazard_interval = max(900, self.hazard_interval - 30)

    def draw_hud(self):
        """
        Draw score, coins, distance, remaining distance, checkpoint,
        and active power-up information.
        """
        remaining = max(0, FINISH_DISTANCE - self.distance)
        checkpoint = min(4, self.distance // 800 + 1)

        info_lines = [
            f"Player: {self.username}",
            f"Score: {self.current_score()}",
            f"Coins: {self.coin_value_total}",
            f"Distance: {self.distance}",
            f"Remaining: {remaining}",
            f"Checkpoint: {checkpoint}/4"
        ]

        y = 10
        for line in info_lines:
            surface = self.font.render(line, True, BLACK)
            self.screen.blit(surface, (10, y))
            y += 24

        # Active power-up display
        power_text = "Power-up: None"
        if self.active_powerup == "Nitro":
            secs = max(0, (self.powerup_end_time - pygame.time.get_ticks()) // 1000 + 1)
            power_text = f"Power-up: Nitro ({secs}s)"
        elif self.active_powerup == "Shield":
            power_text = "Power-up: Shield"

        power_surface = self.font.render(power_text, True, BLACK)
        self.screen.blit(power_surface, (265, 10))

        help_surface = self.small_font.render("Use Left / Right arrows", True, BLACK)
        self.screen.blit(help_surface, (265, 37))

    def draw_all(self):
        """
        Draw the full scene every frame.
        """
        self.draw_road()

        for group in [self.coins, self.powerups, self.events, self.hazards, self.traffic]:
            for sprite in group:
                self.screen.blit(sprite.image, sprite.rect)

        self.screen.blit(self.player.image, self.player.rect)
        self.draw_hud()

    def run(self):
        """
        Main gameplay loop.
        Returns result data for game over / leaderboard.
        """
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_audio()
                    pygame.quit()
                    raise SystemExit

            # Player movement
            self.player.move()

            # Spawns and updates
            self.handle_spawns()
            self.update_groups()
            self.handle_powerup_timeout()

            # Collisions
            if not self.handle_collisions():
                if self.crash_sound is not None:
                    self.crash_sound.play()
                    pygame.time.delay(250)

                running = False

            # Progress
            self.distance += self.current_world_speed() // 2
            self.scale_difficulty()

            # Finish condition
            if self.distance >= FINISH_DISTANCE:
                self.won = True
                self.bonus_score += 200
                running = False

            # Draw frame
            self.draw_all()
            pygame.display.update()
            self.clock.tick(60)

        self.stop_audio()

        return {
            "name": self.username,
            "score": self.current_score(),
            "distance": self.distance,
            "coins": self.coin_value_total,
            "won": self.won
        }