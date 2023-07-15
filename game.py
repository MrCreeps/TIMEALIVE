# Hello! If you are reading this, thats cool.
# This game was made with the help of chatgpt, however, i did do some of the stuff haha
# If you are running the code yourself (which if you see this, you most likely are) you need to install Pygame using pip install pygame
# You can then run the file (if you have Python installed of course)
# PyGame is the only dependency for this (except Python... of course)

TIMEALIVEVERSION = "0.1"

import pygame
import random
import os

pygame.init()
pygame.font.init()
pygame.joystick.init()

# Constants to be used throughout the program
# Original design dimensions
ORIGINAL_WIDTH = 1742
ORIGINAL_HEIGHT = 980

# Get actual screen dimensions
actual_screen_info = pygame.display.Info()
max_width = actual_screen_info.current_w
max_height = actual_screen_info.current_h

# Calculate 16:9 dimensions based on max dimensions
if max_width / max_height > 16 / 9:
    # Too wide, adjust width
    ACTUAL_WIDTH = int(max_height * (16 / 9))
    ACTUAL_HEIGHT = max_height
else:
    # Too tall, adjust height
    ACTUAL_HEIGHT = int(max_width / (16 / 9))
    ACTUAL_WIDTH = max_width

# Calculate scale factors
SCALE_X = ACTUAL_WIDTH / ORIGINAL_WIDTH
SCALE_Y = ACTUAL_HEIGHT / ORIGINAL_HEIGHT

# Scaled constants
SCREEN_WIDTH = ACTUAL_WIDTH
SCREEN_HEIGHT = ACTUAL_HEIGHT
BACKGROUND = (0, 0, 0)
PLAYER_RADIUS = int(20 * SCALE_X)
PLAYER_DEFAULT_COLOR = (255, 255, 255)
PLAYER_HURT_COLOR = (153, 25, 0)
PLAYER_MOVEMENT_SPEED = int(400 * SCALE_X)
PLAYER_MOVEMENT_SPEED_INCREASE = int(2 * SCALE_X)
PLAYER_INITIAL_LIVES = 3
MAX_INV_FRAMES = 120
FONT = pygame.font.Font(None, int(36 * SCALE_X))
TITLE_FONT = pygame.font.Font(None, int(72 * SCALE_X))
LIVES_TEXT_POS = (int(10 * SCALE_X), int(10 * SCALE_Y))
TIME_ALIVE_TEXT_POS = (int(10 * SCALE_X), int(50 * SCALE_Y))
HIGHEST_TIME_TEXT_POS = (int(10 * SCALE_X), int(90 * SCALE_Y))
SECOND = 1000
LASER_INITIAL_SPEED = int(200 * SCALE_X)
LASER_INITIAL_SPAWN_TIME = SECOND / 1.5
LASER_MINIMUM_SPAWN_TIME = SECOND / 3
LASER_LENGTH = int(20 * SCALE_X)
LASER_INITIAL_WIDTH = int(300 * SCALE_X)
LASER_MINUM_WIDTH = int(15 * SCALE_X)
LASER_SPEED_INCREASE = int(3 * SCALE_X)
LASER_TIME_DECREASE = 10
LASER_WIDTH_DECREASE = int(5 * SCALE_X)
BUTTON_COLOR = (0, 200, 0)
BUTTON_SIZE = (int(100 * SCALE_X), int(50 * SCALE_Y))
BUTTON_POSITION = (int((SCREEN_WIDTH / 2) - (BUTTON_SIZE[0] / 2)), int((SCREEN_HEIGHT / 2) + (BUTTON_SIZE[1]) - (100 * SCALE_Y)))
UPGRADE_BUTTON_1_COLOR = BUTTON_COLOR
UPGRADE_BUTTON_1_SIZE = (int(200 * SCALE_X), int(50 * SCALE_Y))
UPGRADE_BUTTON_1_POSITION = (int((SCREEN_WIDTH / 2) - (UPGRADE_BUTTON_1_SIZE[0] / 2)), int((SCREEN_HEIGHT / 2) + (UPGRADE_BUTTON_1_SIZE[1]) + (100 * SCALE_Y)))

import sys

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

HIGHEST_TIME_FILE = resource_path("highest_time.txt")

class Player:
    def __init__(self, screen):
        # Initialize variables for the player
        global PLAYER_DEFAULT_COLOR
        self.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.speed = pygame.Vector2(0, 0)
        self.radius = PLAYER_RADIUS
        self.color = PLAYER_DEFAULT_COLOR
        self.move_speed = PLAYER_MOVEMENT_SPEED
        self.lives = PLAYER_INITIAL_LIVES
        self.inv_frames = 0  # Should always start at 0
        self.alive = True

    def draw_player(self, screen, game_progress):
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)
        self.move_speed = PLAYER_MOVEMENT_SPEED + game_progress * PLAYER_MOVEMENT_SPEED_INCREASE

class LaserManager:
    def __init__(self):
        self.lasers = []
        self.laser_speed = LASER_INITIAL_SPEED
        self.spawn_time = LASER_INITIAL_SPAWN_TIME
        self.laser_length = LASER_LENGTH
        self.laser_width = LASER_INITIAL_WIDTH
        self.last_spawn_time = pygame.time.get_ticks()
        self.laser_color = pygame.Color(0)

    def update_lasers(self, game_progress):
        self.laser_speed = LASER_INITIAL_SPEED + game_progress * LASER_SPEED_INCREASE  # increases by X pixel/s every second
        self.spawn_time = max(LASER_MINIMUM_SPAWN_TIME, SECOND - game_progress * LASER_TIME_DECREASE)  # decreases by X ms every second, can't go lower than Y ms
        self.laser_width = max(LASER_MINUM_WIDTH, LASER_INITIAL_WIDTH - LASER_WIDTH_DECREASE * LASER_WIDTH_DECREASE) # decreases by X pixels evey second, can't go lower than Y

        hue = (game_progress * 2) % 360
        self.laser_color = pygame.Color(0)
        self.laser_color.hsva = (hue, 100, 100)

    def render_lasers(self, dt, screen, player=None):
        for laser in self.lasers:
            laser["pos"] += laser["dir"] * self.laser_speed * dt
            pygame.draw.rect(screen, laser["color"], pygame.Rect(laser["pos"], laser["size"]))

            # Effects the player if the player exists (ie. if in game and not title)
            if player:
                if pygame.Rect(laser["pos"], laser["size"]).colliderect(pygame.Rect(player.position - pygame.Vector2(player.radius, player.radius),
                                                                                    (player.radius * 2, player.radius * 2))):
                    if player.inv_frames == 0:
                        player.inv_frames = MAX_INV_FRAMES
                        player.lives -= 1
                        if player.lives <= 0:
                            player.alive = False

    def spawn_lasers(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time > self.spawn_time:
            self.last_spawn_time = current_time
            self.PATTERN_random()
    
    def PATTERN_random(self):
        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            self.lasers.append({
                "pos": pygame.Vector2(-self.laser_length, random.uniform(0, SCREEN_HEIGHT)),
                "dir": pygame.Vector2(1, 0),
                "size": (self.laser_length, self.laser_width),
                "color": self.laser_color})
        elif side == "right":
            self.lasers.append({
                "pos": pygame.Vector2(SCREEN_WIDTH, random.uniform(0, SCREEN_HEIGHT)),
                "dir": pygame.Vector2(-1, 0),
                "size": (self.laser_length, self.laser_width),
                "color": self.laser_color})
        elif side == "top":
            self.lasers.append({
                "pos": pygame.Vector2(random.uniform(0, SCREEN_WIDTH), -self.laser_length),
                "dir": pygame.Vector2(0, 1),
                "size": (self.laser_width, self.laser_length),
                "color": self.laser_color})
        elif side == "bottom":
            self.lasers.append({
                "pos": pygame.Vector2(random.uniform(0, SCREEN_WIDTH), SCREEN_HEIGHT),
                "dir": pygame.Vector2(0, -1),
                "size": (self.laser_width, self.laser_length),
                "color": self.laser_color})

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TIMEALIVE")
        self.clock = pygame.time.Clock()
        self.load_highest_time()
        while True:
            title = self.titlescreen()
            if not title:
                break

            game = self.gameloop()
            if not game:
                break
    
    def load_highest_time(self):
        if os.path.exists(HIGHEST_TIME_FILE):
            with open(HIGHEST_TIME_FILE, "r") as file:
                self.highest_time = int(file.read())
        else:
            self.highest_time = 0

    def titlescreen(self):
        self.title_laser_manager = LaserManager()
        synthetic_gameprogress = random.randint(0, 200)  # random number bc it is large enough to cover full spectrum (180) while not being too large
        self.title_laser_manager.laser_speed = LASER_INITIAL_SPEED + synthetic_gameprogress * LASER_SPEED_INCREASE
        self.title_laser_manager.spawn_time = max(LASER_MINIMUM_SPAWN_TIME, SECOND - synthetic_gameprogress * LASER_TIME_DECREASE)
        self.title_laser_manager.laser_width = max(LASER_MINUM_WIDTH, LASER_INITIAL_WIDTH - synthetic_gameprogress * LASER_WIDTH_DECREASE)
        hue = (synthetic_gameprogress * 2) % 360
        self.title_laser_manager.laser_color.hsva = (hue, 100, 100)
        
        global PLAYER_DEFAULT_COLOR
        global BACKGROUND

        # Konami Sequence
        self.sequence = ["up"]

        while True:
            self.dt = self.clock.tick(60) / SECOND
            self.screen.fill(BACKGROUND)
            self.title_laser_manager.spawn_lasers()
            self.title_laser_manager.render_lasers(self.dt, self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if pygame.Rect(BUTTON_POSITION, BUTTON_SIZE).collidepoint(mouse_pos):
                        return True
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                return True
            if keys[pygame.K_UP]:
                self.sequence = ["up"]
            if keys[pygame.K_DOWN]:
                if self.sequence[-1] != "down":
                    self.sequence.append("down")
            if keys[pygame.K_LEFT]:
                if self.sequence[-1] != "left":
                    self.sequence.append("left")
            if keys[pygame.K_RIGHT]:
                if self.sequence[-1] != "right":
                    self.sequence.append("right")
            if keys[pygame.K_a]:
                if self.sequence[-1] != "a":
                    self.sequence.append("a")
            if keys[pygame.K_b]:
                if self.sequence[-1] != "b":
                    self.sequence.append("b")
            if self.sequence == ['up', 'down', 'left', 'right', 'left', 'right', 'a', 'b']:
                PLAYER_DEFAULT_COLOR = (0, 0, 0)
                BACKGROUND = (255, 255, 255)
            else:
                PLAYER_DEFAULT_COLOR = (255, 255, 255)
                BACKGROUND = (0, 0, 0)
                    
            title = TITLE_FONT.render("TIME ALIVE", True, PLAYER_DEFAULT_COLOR)
            title_rect = title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 200))
            self.screen.blit(title, title_rect)
            highest_time_text = FONT.render("Highest time: " + str(int(self.highest_time)) + "s", True, PLAYER_DEFAULT_COLOR)
            self.screen.blit(highest_time_text, LIVES_TEXT_POS)
            version_text = FONT.render(f"Version: {TIMEALIVEVERSION}", True, PLAYER_DEFAULT_COLOR)
            self.screen.blit(version_text, TIME_ALIVE_TEXT_POS)

            self.draw_button("Play", FONT)
            start = FONT.render("or press SPACE to play.", True, PLAYER_DEFAULT_COLOR)
            self.screen.blit(start, start.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 75)))

            controls = FONT.render(f"Use WASD, Arrow Keys, or Joy Stick to move.", True, PLAYER_DEFAULT_COLOR)
            self.screen.blit(controls, controls.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 300)))
            
            temptext = FONT.render(f"You have {PLAYER_INITIAL_LIVES} lives and {MAX_INV_FRAMES} frames of invincibility when hit.", True, PLAYER_DEFAULT_COLOR)
            self.screen.blit(temptext, temptext.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 330)))
            temptext = FONT.render("Avoid the walls :)", True, PLAYER_DEFAULT_COLOR)
            self.screen.blit(temptext, temptext.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 360)))
            temptext = FONT.render(f"(The game runs at 60 FPS (locked with deltatime), {SECOND} TPS, and {SCREEN_WIDTH}x{SCREEN_HEIGHT} Resolution.)", True, PLAYER_DEFAULT_COLOR)
            self.screen.blit(temptext, temptext.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 30)))

            pygame.display.flip()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.player.speed = pygame.Vector2(0, 0)  # Reset the player's speed

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player.speed.y = -self.player.move_speed
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player.speed.y = self.player.move_speed

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player.speed.x = -self.player.move_speed
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player.speed.x = self.player.move_speed

        # Handle controller input
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

            axis_x = joystick.get_axis(0)
            axis_y = joystick.get_axis(1)

            if axis_y < -0.5:
                self.player.speed.y = -self.player.move_speed
            elif axis_y > 0.5:
                self.player.speed.y = self.player.move_speed

            if axis_x < -0.5:
                self.player.speed.x = -self.player.move_speed
            elif axis_x > 0.5:
                self.player.speed.x = self.player.move_speed

        self.player.position += self.player.speed * self.dt

        # Keep the player on the screen
        self.player.position.x = min(max(self.player.position.x, self.player.radius), SCREEN_WIDTH - self.player.radius)
        self.player.position.y = min(max(self.player.position.y, self.player.radius), SCREEN_HEIGHT - self.player.radius)

    def handle_player_inv(self):
        global PLAYER_DEFAULT_COLOR
        if self.player.inv_frames > 0:
            self.player.inv_frames -= 1
            self.player.color = PLAYER_HURT_COLOR
        else:
            self.player.color = PLAYER_DEFAULT_COLOR

    def display_hud(self):
        global PLAYER_DEFAULT_COLOR
        lives_text = FONT.render("Lives Left: " + str(self.player.lives), True, (PLAYER_DEFAULT_COLOR))
        time_text = FONT.render("Time alive: " + str(int(self.game_progress)) + "s", True, (PLAYER_DEFAULT_COLOR))
        highest_time_text = FONT.render("Highest time: " + str(int(self.highest_time)) + "s", True, (PLAYER_DEFAULT_COLOR))
        self.screen.blit(lives_text, LIVES_TEXT_POS)
        self.screen.blit(time_text, TIME_ALIVE_TEXT_POS)
        self.screen.blit(highest_time_text, HIGHEST_TIME_TEXT_POS)

    def gameloop(self):
        global PLAYER_DEFAULT_COLOR
        global BACKGROUND
        running = True
        self.player = Player(self.screen)
        self.laser_manager = LaserManager()
        self.start_ticks = pygame.time.get_ticks()
        while running:
            self.dt = self.clock.tick(60) / SECOND
            self.screen.fill(BACKGROUND)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN and not self.player.alive:
                    mouse_pos = event.pos
                    if pygame.Rect(BUTTON_POSITION, BUTTON_SIZE).collidepoint(mouse_pos):
                        return True
                    
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not self.player.alive:
                return True

            if self.player.alive == True:
                self.game_progress = (pygame.time.get_ticks() - self.start_ticks) / SECOND
                self.laser_manager.update_lasers(self.game_progress)
                self.laser_manager.spawn_lasers()
                self.laser_manager.render_lasers(self.dt, self.screen, self.player)
                self.handle_input()
                self.handle_player_inv()
                self.display_hud()
                self.player.draw_player(self.screen, self.game_progress)
            else:
                self.laser_manager.render_lasers(self.dt, self.screen, self.player)
                self.player.color = PLAYER_HURT_COLOR
                self.player.draw_player(self.screen, self.game_progress)
                self.draw_button("Back to Title", FONT, pos=(BUTTON_POSITION[0]-50, BUTTON_POSITION[1]),size=(BUTTON_SIZE[0]+100, BUTTON_SIZE[1]))
                retry = FONT.render("or press SPACE to retry.", True, PLAYER_DEFAULT_COLOR)
                self.screen.blit(retry, retry.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 75)))
                lose_text = TITLE_FONT.render("You Lose!", True, PLAYER_DEFAULT_COLOR)
                lose_rect = lose_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 200))
                self.screen.blit(lose_text, lose_rect)
                self.display_hud()

                if self.game_progress > self.highest_time:
                    self.highest_time = self.game_progress
                    with open(HIGHEST_TIME_FILE, "w") as file:
                        file.write(str(int(self.highest_time)))

            pygame.display.flip()

    def draw_button(self, text, font, color=BUTTON_COLOR, pos=BUTTON_POSITION, size=BUTTON_SIZE):
        global BACKGROUND
        pygame.draw.rect(self.screen, color, pygame.Rect(pos, size))
        text_render = font.render(text, True, BACKGROUND)
        text_rect = text_render.get_rect(center=(pos[0] + size[0] / 2, pos[1] + size[1] / 2))
        self.screen.blit(text_render, text_rect)

if __name__ == "__main__":
    

    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    timealive = Game()
    pygame.quit()

# Made by MrCreeps and ChatGPT
